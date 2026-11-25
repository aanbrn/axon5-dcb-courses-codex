import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { createServer } from "node:net";
import { after, before, test } from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { createServer as createViteServer } from "vite";

const directoryPath = "/api/demo-roles";
const roleStorageKey = "courses.demo.role";
const fallbackMessage = "Your previous demo student is unavailable. You’re now using Administrator.";
const loopback = "127.0.0.1";
const vite = fileURLToPath(new URL("../node_modules/vite/bin/vite.js", import.meta.url));
const testLoader = await createViteServer({
  configFile: false,
  appType: "custom",
  server: { middlewareMode: true, watch: null, ws: false },
});
const { registerRoleStateTests } = await testLoader
  .ssrLoadModule("/test/role-states.test.tsx")
  .finally(() => testLoader.close());

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
  return directory;
}

let browser;
let bff;
let bffOrigin;
let web;
let webOrigin;

before(async () => {
  const { ROLE_TRACER_JAVA, ROLE_TRACER_BFF_JAR, ROLE_TRACER_WEB_DIST } = process.env;
  const bffPort = await loopbackPort();
  bffOrigin = `http://${loopback}:${bffPort}`;
  bff = startService(ROLE_TRACER_JAVA, [
    "-jar", ROLE_TRACER_BFF_JAR, `--server.address=${loopback}`, `--server.port=${bffPort}`,
  ]);
  await awaitReady(bff, new URL("/openapi.json", bffOrigin));
  const webPort = await loopbackPort();
  webOrigin = `http://${loopback}:${webPort}`;
  web = startService(process.execPath, [
    vite, "preview", "--host", loopback, "--port", String(webPort), "--strictPort",
    "--outDir", ROLE_TRACER_WEB_DIST,
  ], { ...process.env, VITE_BFF_ORIGIN: bffOrigin });
  await awaitReady(web, new URL(webOrigin));
  if (process.env.ROLE_TRACER_STOP_BFF === "1") await bff.stop();
  browser = await chromium.launch({ timeout: 10_000 });
});

after(async () => {
  await Promise.all([browser?.close(), web?.stop(), bff?.stop()]);
});

async function openContext(t) {
  const context = await browser.newContext();
  context.setDefaultTimeout(5_000);
  t.after(() => context.close());
  return context;
}

async function readStoredRole(page) {
  return page.evaluate((key) => sessionStorage.getItem(key), roleStorageKey);
}

async function readySelector(page, label) {
  const selector = page.getByLabel("Demo role", { exact: true });
  await selector.locator("option").filter({ hasText: label }).waitFor({ state: "attached" });
  return selector;
}

test("retains independent live BFF selections across same-context tab reloads", async (t) => {
  const context = await openContext(t);
  const first = await context.newPage();
  const { administrator, students: [maya, alex] } = await traceRoles(first, webOrigin, bffOrigin);
  const firstSelector = await readySelector(first, maya.label);
  await firstSelector.selectOption(maya.id);
  assert.equal(await firstSelector.inputValue(), maya.id);
  await first.reload();
  await readySelector(first, maya.label);
  assert.equal(await firstSelector.inputValue(), maya.id, "The first tab must restore Maya");

  const second = await context.newPage();
  await second.goto(webOrigin);
  assert.equal(await second.evaluate(() => window.opener), null);
  const secondSelector = await readySelector(second, alex.label);
  assert.equal(await secondSelector.inputValue(), administrator.id, "An independent tab starts as Administrator");
  await secondSelector.selectOption(alex.id);
  assert.equal(await secondSelector.inputValue(), alex.id);
  await Promise.all([first.reload(), second.reload()]);
  await Promise.all([readySelector(first, maya.label), readySelector(second, alex.label)]);
  assert.equal(await firstSelector.inputValue(), maya.id, "Alex must not overwrite Maya in the first tab");
  assert.equal(await secondSelector.inputValue(), alex.id);
  assert.equal(await readStoredRole(first), maya.id);
  assert.equal(await readStoredRole(second), alex.id);
  console.log(`Chromium ${browser.version()} restored distinct Maya and Alex selections from the live BFF.`);
});

for (const [name, stored, students] of [
  ["a removed student in an administrator-only directory", "student_removed", []],
  ["a differently cased student ID", "Student_Maya", [
    { id: "student_maya", label: "Maya Chen", kind: "student" },
  ]],
]) {
  test(`reconciles ${name} only after a valid directory loads`, async (t) => {
    const context = await openContext(t);
    const page = await context.newPage();
    const administrator = { id: "admin_exact", label: "Administrator", kind: "administrator" };
    await page.addInitScript(({ key, value }) => {
      if (sessionStorage.getItem(key) === null) sessionStorage.setItem(key, value);
    }, { key: roleStorageKey, value: stored });
    const release = Promise.withResolvers();
    await page.route(`**${directoryPath}`, async (route) => {
      await release.promise;
      await route.fulfill({ json: { administrator, students } });
    });
    try {
      await Promise.all([page.waitForRequest(`**${directoryPath}`), page.goto(webOrigin)]);
      assert.equal(await readStoredRole(page), stored, "Loading must preserve the stored ID");
    } finally {
      release.resolve();
    }
    const selector = await readySelector(page, administrator.label);
    assert.equal(await selector.inputValue(), administrator.id);
    assert.equal(await readStoredRole(page), administrator.id, "A valid response must persist the fallback");
    assert.equal(await page.getByRole("status").filter({ hasText: fallbackMessage }).count(), 1);
    if (students.length === 0) {
      await page.getByRole("heading", { name: "No demo students available" }).waitFor();
      assert.equal(await page.getByText("You can continue as Administrator or read the quick start.").count(), 1);
      assert.equal(await page.getByRole("link", { name: "quick start", exact: true }).count(), 1);
    }
    await page.reload();
    await readySelector(page, administrator.label);
    assert.equal(await page.getByText(fallbackMessage, { exact: true }).count(), 0, "The fallback is announced once");
  });
}

registerRoleStateTests({
  openContext,
  webOrigin: () => webOrigin,
  async developmentOrigin(t) {
    const port = await loopbackPort();
    const origin = `http://${loopback}:${port}`;
    const dev = startService(process.execPath, [
      vite, "--host", loopback, "--port", String(port), "--strictPort",
    ], { ...process.env, VITE_BFF_ORIGIN: bffOrigin });
    t.after(() => dev.stop());
    await awaitReady(dev, new URL(origin));
    return origin;
  },
});
