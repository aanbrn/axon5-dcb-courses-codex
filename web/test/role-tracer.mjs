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
const fallbackMessage =
  "Your previous demo student is unavailable. You’re now using Administrator.";
const loopback = "127.0.0.1";
const vite = fileURLToPath(
  new URL("../node_modules/vite/bin/vite.js", import.meta.url),
);
const testLoader = await createViteServer({
  configFile: false,
  appType: "custom",
  optimizeDeps: { noDiscovery: true },
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
  const child = spawn(command, args, {
    env,
    stdio: ["ignore", "pipe", "pipe"],
  });
  let output = "";
  let exited = false;
  for (const stream of [child.stdout, child.stderr]) {
    stream.setEncoding("utf8").on("data", (chunk) => {
      output = (output + chunk).slice(-8_000);
    });
  }
  child.on("error", (error) => {
    output += error.message;
  });
  const closed = new Promise((resolve) => {
    child.once("close", () => {
      exited = true;
      resolve();
    });
  });
  return {
    get exited() {
      return exited;
    },
    get output() {
      return output;
    },
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
    const response = await fetch(url, {
      signal: AbortSignal.timeout(500),
    }).catch(() => undefined);
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
  assert.ok(
    response?.ok(),
    "The browser's first directory GET must reach the live BFF",
  );

  const direct = await fetch(new URL(directoryPath, bffOrigin), {
    signal: AbortSignal.timeout(5_000),
  });
  assert.equal(direct.status, 200, "The BFF directory must respond directly");
  const directory = await response.json();
  assert.deepEqual(
    directory,
    await direct.json(),
    "The browser must receive the actual BFF reply",
  );

  const roles = [directory.administrator, ...directory.students];
  const expectedOptions = roles.map(({ id, label }) => ({ id, label }));
  const selector = page.getByRole("combobox", { name: "Demo role" });
  const options = selector.locator("option");
  await options
    .nth(roles.length - 1)
    .waitFor({ state: "attached", timeout: 5_000 });
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
  const { ROLE_TRACER_JAVA, ROLE_TRACER_BFF_JAR, ROLE_TRACER_WEB_DIST } =
    process.env;
  const bffPort = await loopbackPort();
  bffOrigin = `http://${loopback}:${bffPort}`;
  bff = startService(ROLE_TRACER_JAVA, [
    "-jar",
    ROLE_TRACER_BFF_JAR,
    `--server.address=${loopback}`,
    `--server.port=${bffPort}`,
  ]);
  await awaitReady(bff, new URL("/openapi.json", bffOrigin));
  const webPort = await loopbackPort();
  webOrigin = `http://${loopback}:${webPort}`;
  web = startService(
    process.execPath,
    [
      vite,
      "preview",
      "--host",
      loopback,
      "--port",
      String(webPort),
      "--strictPort",
      "--outDir",
      ROLE_TRACER_WEB_DIST,
    ],
    { ...process.env, VITE_BFF_ORIGIN: bffOrigin },
  );
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
  await selector
    .locator("option")
    .filter({ hasText: label })
    .waitFor({ state: "attached" });
  return selector;
}

test("retains independent live BFF selections across same-context tab reloads", async (t) => {
  const context = await openContext(t);
  const first = await context.newPage();
  const {
    administrator,
    students: [maya, alex],
  } = await traceRoles(first, webOrigin, bffOrigin);
  const firstSelector = await readySelector(first, maya.label);
  await firstSelector.selectOption(maya.id);
  assert.equal(await firstSelector.inputValue(), maya.id);
  await first.reload();
  await readySelector(first, maya.label);
  assert.equal(
    await firstSelector.inputValue(),
    maya.id,
    "The first tab must restore Maya",
  );

  const second = await context.newPage();
  await second.goto(webOrigin);
  assert.equal(await second.evaluate(() => window.opener), null);
  const secondSelector = await readySelector(second, alex.label);
  assert.equal(
    await secondSelector.inputValue(),
    administrator.id,
    "An independent tab starts as Administrator",
  );
  await secondSelector.selectOption(alex.id);
  assert.equal(await secondSelector.inputValue(), alex.id);
  await Promise.all([first.reload(), second.reload()]);
  await Promise.all([
    readySelector(first, maya.label),
    readySelector(second, alex.label),
  ]);
  assert.equal(
    await firstSelector.inputValue(),
    maya.id,
    "Alex must not overwrite Maya in the first tab",
  );
  assert.equal(await secondSelector.inputValue(), alex.id);
  assert.equal(await readStoredRole(first), maya.id);
  assert.equal(await readStoredRole(second), alex.id);
  console.log(
    `Chromium ${browser.version()} restored distinct Maya and Alex selections from the live BFF.`,
  );
});

for (const [name, stored, students] of [
  [
    "a removed student in an administrator-only directory",
    "student_removed",
    [],
  ],
  [
    "a differently cased student ID",
    "Student_Maya",
    [{ id: "student_maya", label: "Maya Chen", kind: "student" }],
  ],
]) {
  test(`reconciles ${name} only after a valid directory loads`, async (t) => {
    const context = await openContext(t);
    const page = await context.newPage();
    const administrator = {
      id: "admin_exact",
      label: "Administrator",
      kind: "administrator",
    };
    await page.addInitScript(
      ({ key, value }) => {
        if (sessionStorage.getItem(key) === null)
          sessionStorage.setItem(key, value);
      },
      { key: roleStorageKey, value: stored },
    );
    const release = Promise.withResolvers();
    await page.route(`**${directoryPath}`, async (route) => {
      await release.promise;
      await route.fulfill({ json: { administrator, students } });
    });
    try {
      await Promise.all([
        page.waitForRequest(`**${directoryPath}`),
        page.goto(webOrigin),
      ]);
      assert.equal(
        await readStoredRole(page),
        stored,
        "Loading must preserve the stored ID",
      );
    } finally {
      release.resolve();
    }
    const selector = await readySelector(page, administrator.label);
    assert.equal(await selector.inputValue(), administrator.id);
    assert.equal(
      await readStoredRole(page),
      administrator.id,
      "A valid response must persist the fallback",
    );
    assert.equal(
      await page
        .getByRole("status")
        .filter({ hasText: fallbackMessage })
        .count(),
      1,
    );
    if (students.length === 0) {
      await page
        .getByRole("heading", { name: "No demo students available" })
        .waitFor();
      assert.equal(
        await page
          .getByText(
            "You can continue as Administrator or read the quick start.",
          )
          .count(),
        1,
      );
      assert.equal(
        await page
          .getByRole("link", { name: "quick start", exact: true })
          .count(),
        1,
      );
    }
    await page.reload();
    await readySelector(page, administrator.label);
    assert.equal(
      await page.getByText(fallbackMessage, { exact: true }).count(),
      0,
      "The fallback is announced once",
    );
  });
}

async function assertNoPageOverflow(page, context) {
  const { clientWidth, scrollWidth } = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  assert.ok(
    scrollWidth <= clientWidth,
    `${context} must fit: ${scrollWidth}px > ${clientWidth}px`,
  );
}

test("wraps the shell and shows full selected names at narrow widths and enlarged text", async (t) => {
  const page = await (await openContext(t)).newPage();
  const mediumName = "M".repeat(20);
  const longName = `<strong data-role-proof>Demo student ${"LongName".repeat(18)}</strong>`;
  const students = [
    { id: "student_medium", label: mediumName, kind: "student" },
    { id: "student_long", label: longName, kind: "student" },
  ];
  await page.route(`**${directoryPath}`, (route) =>
    route.fulfill({
      json: {
        administrator: {
          id: "admin",
          label: "Administrator",
          kind: "administrator",
        },
        students,
      },
    }),
  );
  await page.goto(webOrigin);
  await page.evaluate(() => document.fonts.ready.then(() => {}));
  const loadedFont = await page.evaluate(() =>
    [...document.fonts].some(
      ({ family, status }) =>
        family === "Geist Variable" && status === "loaded",
    ),
  );
  assert.equal(
    loadedFont,
    true,
    "The production shell must load the bundled Geist face",
  );

  const select = await readySelector(page, longName);
  const fullName = page.locator(".role-full-name");
  await select.selectOption("student_medium");
  assert.equal(
    await fullName.count(),
    0,
    "A fitting value does not need a duplicate label",
  );
  await page.setViewportSize({ width: 320, height: 900 });
  await fullName.waitFor({ state: "visible" });
  assert.equal(await fullName.textContent(), mediumName);
  await page.setViewportSize({ width: 1280, height: 900 });
  await fullName.waitFor({ state: "detached" });

  await select.selectOption("student_long");
  assert.equal(await select.locator("option:checked").textContent(), longName);
  assert.equal(
    await page.locator("[data-role-proof]").count(),
    0,
    "Directory labels render as literal text",
  );
  for (const width of [320, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    for (const scale of [100, 200]) {
      await page.evaluate((size) => {
        document.documentElement.style.fontSize = `${size}%`;
      }, scale);
      const context = `${width}px at ${scale}% text size`;
      await assertNoPageOverflow(page, context);
      await fullName.waitFor({ state: "visible" });
      assert.equal(await fullName.textContent(), longName);
      assert.ok(
        await fullName.evaluate(
          (element) =>
            element.getBoundingClientRect().height >
            parseFloat(getComputedStyle(element).lineHeight),
        ),
        `The complete label must wrap at ${context}`,
      );
      for (const control of [
        select,
        page.getByRole("link", { name: "DCB Courses", exact: true }),
        page.getByRole("link", { name: "Documentation", exact: true }),
        page.getByRole("link", { name: "Quick start", exact: true }),
        page.getByRole("link", { name: "Read feasibility report" }),
      ]) {
        const box = await control.boundingBox();
        assert.ok(
          box && box.x >= 0 && box.x + box.width <= width && box.height >= 48,
          context,
        );
      }
      if (width === 320) {
        const { x, width: selectWidth } = await select.boundingBox();
        assert.equal(
          x,
          (16 * scale) / 100,
          "The role group starts at the compact gutter",
        );
        assert.equal(
          selectWidth,
          width - 2 * x,
          "The select fills its own row",
        );
      }
    }
  }

  await page.setViewportSize({ width: 320, height: 900 });
  await page.evaluate((copy) => {
    for (const selector of [
      "h1",
      "label[for=demo-role]",
      "nav a",
      "[role=status]",
    ]) {
      document.querySelector(selector).textContent = copy;
    }
  }, "UnbrokenCopy".repeat(20));
  await assertNoPageOverflow(
    page,
    "Long heading, label, navigation, and status at 320px and 200% text size",
  );
});

test("keeps keyboard order and focus visible in the compact shell and forced colors", async (t) => {
  const page = await (await openContext(t)).newPage();
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto(webOrigin);
  const select = await readySelector(page, "Maya Chen");
  const skip = page.getByRole("link", { name: "Skip to main content" });
  const main = page.getByRole("main");
  const docs = page.getByRole("link", { name: "Documentation", exact: true });
  const report = page.getByRole("link", { name: "Read feasibility report" });
  assert.equal(
    await page
      .getByRole("heading", { level: 1, name: "Axon 5 DCB Courses" })
      .count(),
    1,
  );
  assert.equal(
    await docs.evaluate((link) => getComputedStyle(link).textDecorationLine),
    "underline",
  );
  assert.equal(
    await skip.evaluate((link) => getComputedStyle(link).clipPath),
    "inset(50%)",
  );

  for (const target of [
    skip,
    page.getByRole("link", { name: "DCB Courses", exact: true }),
    docs,
    page.getByRole("link", { name: "Quick start", exact: true }),
    select,
    report,
  ]) {
    await page.keyboard.press("Tab");
    assert.equal(
      await target.evaluate((element) => element === document.activeElement),
      true,
    );
    const focus = await target.evaluate((element) => {
      const style = getComputedStyle(element);
      return [
        style.outlineWidth,
        style.outlineOffset,
        style.outlineStyle,
        style.outlineColor,
      ];
    });
    assert.deepEqual(focus, ["2px", "2px", "solid", "rgb(67, 56, 202)"]);
    if (target === skip) {
      assert.equal(
        await skip.evaluate((link) => getComputedStyle(link).clipPath),
        "none",
      );
    }
  }
  await page.keyboard.press("Shift+Tab");
  assert.equal(
    await select.evaluate((element) => element === document.activeElement),
    true,
  );
  await page.emulateMedia({ forcedColors: "active" });
  const forcedColors = await select.evaluate((element) => {
    const reference = document.createElement("span");
    reference.style.outlineColor = "Highlight";
    reference.style.borderColor = "ButtonText";
    element.after(reference);
    const expected = getComputedStyle(reference);
    const actual = getComputedStyle(element);
    const matches =
      actual.outlineColor === expected.outlineColor &&
      actual.borderTopColor === expected.borderTopColor;
    const outline = [
      actual.outlineWidth,
      actual.outlineOffset,
      actual.outlineStyle,
    ];
    reference.remove();
    return { matches, outline };
  });
  assert.deepEqual(forcedColors, {
    matches: true,
    outline: ["2px", "2px", "solid"],
  });
  await skip.focus();
  await page.keyboard.press("Enter");
  assert.equal(
    await main.evaluate((element) => element === document.activeElement),
    true,
  );

  await page.emulateMedia({ forcedColors: "none" });
  await page.route(`**${directoryPath}`, (route) =>
    route.fulfill({ status: 503 }),
  );
  await page.reload();
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  await page.getByRole("alert").waitFor();
  await assertNoPageOverflow(
    page,
    "Role directory failure at 320px and 200% text size",
  );
  const retry = page.getByRole("button", { name: "Retry loading roles" });
  assert.equal(
    await retry.evaluate(
      (element) => getComputedStyle(element).backgroundColor,
    ),
    "rgb(255, 255, 255)",
  );
  assert.ok((await retry.boundingBox()).height >= 48);
});

registerRoleStateTests({
  openContext,
  webOrigin: () => webOrigin,
  async developmentOrigin(t) {
    const port = await loopbackPort();
    const origin = `http://${loopback}:${port}`;
    const dev = startService(
      process.execPath,
      [vite, "--host", loopback, "--port", String(port), "--strictPort"],
      { ...process.env, VITE_BFF_ORIGIN: bffOrigin },
    );
    t.after(() => dev.stop());
    await awaitReady(dev, new URL(origin));
    return origin;
  },
});
