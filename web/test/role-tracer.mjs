import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { createServer } from "node:net";
import { test } from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const directoryPath = "/api/demo-roles";
const loopback = "127.0.0.1";
const vite = fileURLToPath(new URL("../node_modules/vite/bin/vite.js", import.meta.url));

async function loopbackPort() {
  const server = createServer().listen(0, loopback);
  await once(server, "listening");
  const { port } = server.address();
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
  return port;
}

function startService(command, args, env = process.env) {
  const child = spawn(command, args, { env, stdio: ["ignore", "pipe", "pipe"] });
  let output = "";
  let exited = false;
  for (const stream of [child.stdout, child.stderr]) {
    stream.setEncoding("utf8").on("data", (chunk) => {
      output = (output + chunk).slice(-8_000);
    });
  }
  child.on("error", (error) => { output += error.message; });
  const closed = new Promise((resolve) => {
    child.once("close", () => {
      exited = true;
      resolve();
    });
  });
  return {
    get exited() { return exited; },
    get output() { return output; },
    async stop() {
      if (!exited) {
        child.kill();
        await Promise.race([closed, delay(3_000, undefined, { ref: false })]);
      }
      if (!exited) child.kill("SIGKILL");
      await closed;
    },
  };
}

async function awaitReady(service, url) {
  const deadline = Date.now() + 25_000;
  while (!service.exited && Date.now() < deadline) {
    const response = await fetch(url, { signal: AbortSignal.timeout(500) }).catch(() => undefined);
    await response?.body?.cancel();
    if (response?.ok && !service.exited) return;
    await delay(100);
  }
  throw new Error(`Timed out waiting for ${url}\n${service.output}`);
}

async function traceRoles(page, webOrigin, bffOrigin) {
  const directoryResponse = page
    .waitForResponse(
      (response) =>
        response.url() === new URL(directoryPath, webOrigin).href &&
        response.request().method() === "GET",
      { timeout: 5_000 },
    )
    .catch((error) => {
      if (error.name !== "TimeoutError") throw error;
      return undefined;
    });
  await page.goto(webOrigin, { timeout: 5_000 });
  const response = await directoryResponse;
  assert.ok(response?.ok(), "The browser's first directory GET must reach the live BFF");

  const direct = await fetch(new URL(directoryPath, bffOrigin), {
    signal: AbortSignal.timeout(5_000),
  });
  assert.equal(direct.status, 200, "The BFF directory must respond directly");
  const directory = await response.json();
  assert.deepEqual(directory, await direct.json(), "The browser must receive the actual BFF reply");

  const roles = [directory.administrator, ...directory.students];
  const expectedOptions = roles.map(({ id, label }) => ({ id, label }));
  const selector = page.getByRole("combobox", { name: "Demo role" });
  const options = selector.locator("option");
  await options.nth(roles.length - 1).waitFor({ state: "attached", timeout: 5_000 });
  assert.deepEqual(
    await options.evaluateAll((elements) =>
      elements.map((option) => ({ id: option.value, label: option.text })),
    ),
    expectedOptions,
    "The selector must display the BFF labels and identifiers in directory order",
  );
  assert.deepEqual(
    roles.map(({ label }) => label),
    ["Administrator", "Maya Chen", "Alex Rivera"],
    "The live directory must supply the three demo personas",
  );
  assert.equal(await selector.inputValue(), directory.administrator.id);
  const alex = directory.students.find(({ label }) => label === "Alex Rivera");
  await selector.selectOption({ label: alex.label });
  assert.equal(await selector.inputValue(), alex.id);
  assert.equal(await selector.locator("option:checked").textContent(), alex.label);
}

test("selects a role from the first live BFF response", async () => {
  const { ROLE_TRACER_JAVA, ROLE_TRACER_BFF_JAR, ROLE_TRACER_WEB_DIST } = process.env;
  const bffPort = await loopbackPort();
  const bffOrigin = `http://${loopback}:${bffPort}`;
  const bff = startService(ROLE_TRACER_JAVA, [
    "-jar", ROLE_TRACER_BFF_JAR, `--server.address=${loopback}`, `--server.port=${bffPort}`,
  ]);
  let web;
  try {
    await awaitReady(bff, new URL("/openapi.json", bffOrigin));
    const webPort = await loopbackPort();
    const webOrigin = `http://${loopback}:${webPort}`;
    web = startService(process.execPath, [
      vite, "preview", "--host", loopback, "--port", String(webPort), "--strictPort",
      "--outDir", ROLE_TRACER_WEB_DIST,
    ], { ...process.env, VITE_BFF_ORIGIN: bffOrigin });
    await awaitReady(web, new URL(webOrigin));
    if (process.env.ROLE_TRACER_STOP_BFF === "1") await bff.stop();

    const browser = await chromium.launch({ timeout: 10_000 });
    try {
      const page = await browser.newPage();
      await traceRoles(page, webOrigin, bffOrigin);
      console.log(`Chromium ${browser.version()} selected Alex Rivera from the live BFF.`);
    } finally {
      await browser.close();
    }
  } finally {
    await Promise.all([web?.stop(), bff.stop()]);
  }
});
