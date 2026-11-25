import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const loopback = "127.0.0.1";
const webUrl = "http://127.0.0.1:5173/";
const docsUrl = "http://127.0.0.1:8081/courses/";
const directoryPath = "/api/demo-roles";
const directoryError = "Could not load demo roles. Try again to switch roles.";
const vite = fileURLToPath(
  new URL("../node_modules/vite/bin/vite.js", import.meta.url),
);
const docsProject = fileURLToPath(new URL("../../docs-site/", import.meta.url));
const docsPages = [
  ["Home", "", "Run the demo"],
  ["Quick start", "quick-start/", "Quick start"],
  [
    "Feasibility report",
    "feasibility/phase-01/",
    "Phase 01 feasibility record",
  ],
  ["Maintainer guide", "maintainer-guide/", "Maintainer guide"],
];

function run(command, args, options = {}) {
  const child = spawn(command, args, {
    ...options,
    stdio: ["ignore", "pipe", "pipe"],
  });
  let output = "";
  let exitCode;
  for (const stream of [child.stdout, child.stderr]) {
    stream.setEncoding("utf8").on("data", (chunk) => {
      output = (output + chunk).slice(-8_000);
    });
  }
  child.on("error", (error) => {
    output += error.message;
  });
  const closed = new Promise((resolve) => {
    child.once("close", (code) => {
      exitCode = code;
      resolve(code);
    });
  });
  return {
    get exited() {
      return exitCode !== undefined;
    },
    get output() {
      return output;
    },
    closed,
    async stop() {
      if (exitCode !== undefined) return;
      child.kill();
      await Promise.race([closed, delay(3_000, undefined, { ref: false })]);
      if (exitCode === undefined) child.kill("SIGKILL");
      await closed;
    },
  };
}

async function waitForService(service, url) {
  const deadline = Date.now() + 20_000;
  while (Date.now() < deadline && !service.exited) {
    const response = await fetch(url, {
      signal: AbortSignal.timeout(500),
    }).catch(() => undefined);
    await response?.body?.cancel();
    if (response?.ok && !service.exited) return;
    await delay(100);
  }
  throw new Error(`Service did not become ready at ${url}\n${service.output}`);
}

async function reservePort(port) {
  const server = createServer();
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, loopback, () => {
      const actual = server.address().port;
      server.close((error) => (error ? reject(error) : resolve(actual)));
    });
  });
}

async function buildDocs(output, appUrl) {
  const renderer = run(
    process.execPath,
    ["node_modules/@11ty/eleventy/cmd.cjs", `--output=${output}`],
    {
      cwd: docsProject,
      env: {
        ...process.env,
        DOCS_INPUT: process.env.SITE_SMOKE_STAGED_DOCS,
        DOCS_BASE: new URL(docsUrl).pathname,
        DOCS_APP_URL: appUrl,
        DOCS_TRUSTED_APP_ORIGINS: "",
      },
    },
  );
  try {
    const status = await Promise.race([
      renderer.closed,
      delay(20_000, "timeout", { ref: false }),
    ]);
    assert.equal(
      status,
      0,
      `Eleventy failed to render the ${appUrl ? "configured" : "local"} site\n${renderer.output}`,
    );
  } finally {
    await renderer.stop();
  }
}

async function visit(page, link, url) {
  assert.equal(await link.evaluate((element) => element.href), url);
  const [response] = await Promise.all([
    page.waitForResponse(
      (reply) =>
        reply.url() === url.split("#", 1)[0] &&
        reply.request().isNavigationRequest(),
    ),
    link.click(),
  ]);
  assert.ok(
    response.ok(),
    `Navigation to ${url} returned ${response.status()}`,
  );
  assert.equal(page.url(), url);
}

function roleSelector(page) {
  return page.getByRole("combobox", { name: "Demo role" });
}

async function firstDirectory(page, bffUrl) {
  const [response] = await Promise.all([
    page.waitForResponse(
      (reply) =>
        reply.url() === new URL(directoryPath, webUrl).href &&
        reply.request().method() === "GET",
    ),
    page.goto(webUrl),
  ]);
  assert.ok(response.ok(), "The shell's first directory request must succeed");
  const direct = await fetch(new URL(directoryPath, bffUrl), {
    signal: AbortSignal.timeout(5_000),
  });
  assert.equal(direct.status, 200, "The real BFF directory is reachable");
  const directory = await direct.json();
  assert.deepEqual(
    await response.json(),
    directory,
    "The browser receives the BFF payload",
  );
  const roles = [directory.administrator, ...directory.students];
  const options = roleSelector(page).locator("option");
  await options.nth(roles.length - 1).waitFor({ state: "attached" });
  assert.deepEqual(
    await options.evaluateAll((entries) =>
      entries.map(({ value, text }) => [value, text]),
    ),
    roles.map(({ id, label }) => [id, label]),
    "Every role shown must use the live response's identifier and label",
  );
  assert.equal(
    await roleSelector(page).inputValue(),
    directory.administrator.id,
  );
  return directory;
}

async function waitForRole(page, role) {
  const selector = roleSelector(page);
  await selector
    .locator("option")
    .filter({ hasText: role.label })
    .waitFor({ state: "attached" });
  await page.waitForFunction(
    (id) => document.querySelector("#demo-role").value === id,
    role.id,
  );
  return selector;
}

async function assertPageFits(page, label) {
  const { scrollWidth, clientWidth } = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  assert.ok(
    scrollWidth <= clientWidth,
    `${label} overflows: ${scrollWidth}px > ${clientWidth}px`,
  );
}

async function assertResponsive(page, label, check = async () => {}) {
  for (const width of [320, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    for (const scale of [100, 200]) {
      await page.evaluate((percent) => {
        document.documentElement.style.fontSize = `${percent}%`;
      }, scale);
      await assertPageFits(page, `${label} at ${width}px and ${scale}% text`);
      await check();
    }
  }
}

async function assertDocsNavigation(page) {
  const nav = page.getByRole("navigation", { name: "Documentation" });
  for (const [label, path, title] of [...docsPages.slice(1), docsPages[0]]) {
    const url = new URL(path, docsUrl).href;
    const link = nav.getByRole("link", { name: label, exact: true });
    await visit(page, link, url);
    await page
      .getByRole("heading", { level: 1, name: title, exact: true })
      .waitFor();
    assert.equal(await link.getAttribute("aria-current"), "page");
    await assertResponsive(page, label);
  }
}

async function assertReportKeyboard(page) {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  const skip = page.getByRole("link", { name: "Skip to main content" });
  await page.keyboard.press("Tab");
  assert.ok(
    await skip.evaluate((element) => element === document.activeElement),
  );
  await page.keyboard.press("Enter");
  assert.equal(new URL(page.url()).hash, "#main-content");
  const main = page.getByRole("main");
  assert.ok(
    await main.evaluate((element) => element === document.activeElement),
  );
  const table = page.getByRole("region", {
    name: /^Data table — Phase 01 feasibility record$/,
  });
  const code = page
    .getByRole("region", { name: /^Code sample — Reproduce the proof$/ })
    .first();
  for (const region of [table, code]) {
    const previous = await region.evaluate(
      (element) => element.scrollWidth > element.clientWidth,
    );
    assert.ok(
      previous,
      "The report region contains horizontally scrollable content",
    );
    await region.focus();
    const focused = await region.evaluate((element) => ({
      focused: element === document.activeElement,
      outline: getComputedStyle(element).outlineStyle,
      tabIndex: element.tabIndex,
    }));
    assert.deepEqual(focused, { focused: true, outline: "solid", tabIndex: 0 });
    await page.keyboard.press("ArrowRight");
    const element = await region.elementHandle();
    await page.waitForFunction((target) => target.scrollLeft > 0, element);
  }
  await assertPageFits(page, "Keyboard-scrolled report");
}

test(
  "follows the live directory, both documentation launch modes, and outage recovery",
  { timeout: 100_000 },
  async (t) => {
    const scratch = await mkdtemp(join(tmpdir(), "courses-site-smoke-"));
    const services = [];
    let browser;
    t.after(async () => {
      try {
        await browser?.close();
      } finally {
        await Promise.all(services.map((service) => service.stop()));
        await rm(scratch, { recursive: true, force: true });
      }
    });
    function start(command, args, options) {
      const service = run(command, args, options);
      services.push(service);
      return service;
    }
    await Promise.all([reservePort(5173), reservePort(8081)]);
    const bffPort = await reservePort(0);
    const bffUrl = `http://${loopback}:${bffPort}/`;
    function startBff() {
      return start(process.env.SITE_SMOKE_JAVA, [
        "-jar",
        process.env.SITE_SMOKE_BFF_JAR,
        `--server.address=${loopback}`,
        `--server.port=${bffPort}`,
      ]);
    }
    const bff = startBff();
    const web = start(
      process.execPath,
      [vite, "--host", loopback, "--port", "5173", "--strictPort"],
      {
        env: {
          ...process.env,
          VITE_BFF_ORIGIN: bffUrl,
          VITE_DOCS_BASE: docsUrl,
        },
      },
    );
    const startDocs = (output) =>
      start(
        process.execPath,
        ["serve.mjs", output, new URL(docsUrl).pathname],
        { cwd: docsProject },
      );
    await Promise.all([
      waitForService(bff, new URL("openapi.json", bffUrl)),
      waitForService(web, webUrl),
      buildDocs(join(scratch, "configured"), webUrl),
      buildDocs(join(scratch, "local"), ""),
    ]);
    const configuredDocs = startDocs(join(scratch, "configured"));
    await waitForService(configuredDocs, docsUrl);
    browser = await chromium.launch({ timeout: 10_000 });
    const context = await browser.newContext();
    context.setDefaultTimeout(5_000);
    const first = await context.newPage();
    const { administrator, students } = await firstDirectory(first, bffUrl);
    const maya = students.find(({ label }) => label === "Maya Chen");
    assert.ok(maya, "The BFF supplies Maya Chen");
    await roleSelector(first).press("m");
    await waitForRole(first, maya);
    assert.ok(
      await roleSelector(first).evaluate(
        (control) => control === document.activeElement,
      ),
    );
    await first.reload();
    await waitForRole(first, maya);
    const independent = await context.newPage();
    await independent.goto(webUrl);
    assert.equal(await independent.evaluate(() => window.opener), null);
    await waitForRole(independent, administrator);

    await bff.stop();
    await first.reload();
    const alert = first.getByRole("alert");
    await alert.waitFor();
    assert.equal(await alert.innerText(), directoryError);
    assert.ok(await roleSelector(first).isDisabled());
    assert.equal(
      await roleSelector(first).locator("option").innerText(),
      "Roles unavailable",
    );
    await assertResponsive(first, "Shell during a BFF outage");
    for (const [name, path] of [
      ["Quick start", "quick-start/"],
      ["Read feasibility report", "feasibility/phase-01/"],
      ["Documentation", ""],
    ]) {
      await visit(
        first,
        first.getByRole("link", { name, exact: true }),
        new URL(path, docsUrl).href,
      );
      if (name === "Read feasibility report") {
        await assertReportKeyboard(first);
        await first.goBack(); // Return from the skip-link fragment to the report URL.
      }
      if (name !== "Documentation") {
        await first.goBack();
        assert.equal(first.url(), webUrl);
      }
    }
    await assertDocsNavigation(first);
    await visit(
      first,
      first.getByRole("link", { name: "Open demo", exact: true }),
      webUrl,
    );
    await alert.waitFor();
    const revived = startBff();
    await waitForService(revived, new URL("openapi.json", bffUrl));
    const retry = first.getByRole("button", { name: "Retry loading roles" });
    await retry.press("Enter");
    await waitForRole(first, maya);
    assert.ok(
      await roleSelector(first).evaluate(
        (control) => control === document.activeElement,
      ),
    );
    assert.equal(await alert.count(), 0);
    await waitForRole(independent, administrator);

    await configuredDocs.stop();
    const localDocs = startDocs(join(scratch, "local"));
    await waitForService(localDocs, docsUrl);
    await visit(
      first,
      first.getByRole("link", { name: "Documentation", exact: true }),
      docsUrl,
    );
    await assertDocsNavigation(first);
    assert.equal(
      await first.getByRole("link", { name: "Open demo", exact: true }).count(),
      0,
    );
    await visit(
      first,
      first.getByRole("link", { name: "Read quick start", exact: true }),
      new URL("quick-start/", docsUrl).href,
    );
    await first
      .getByRole("heading", { name: "Start the shell", exact: true })
      .waitFor();

    // Isolate the long-text case after exercising the real service throughout recovery.
    const longName = "Student" + "LongName".repeat(24);
    await independent.route(`**${directoryPath}`, (route) =>
      route.fulfill({
        json: { administrator, students: [{ ...maya, label: longName }] },
      }),
    );
    await independent.reload();
    const longRole = { ...maya, label: longName };
    const select = roleSelector(independent);
    await select.selectOption(longRole.id);
    await waitForRole(independent, longRole);
    await select.focus();
    await assertResponsive(
      independent,
      "Shell with a long selected role",
      async () => {
        const fullName = independent.locator(".role-full-name");
        await fullName.waitFor();
        assert.equal(await fullName.textContent(), longName);
        assert.ok(
          await select.evaluate(
            (control) => control === document.activeElement,
          ),
        );
      },
    );
    console.log(
      `Chromium ${browser.version()} verified nested docs, BFF outage and recovery, and responsive keyboard checks.`,
    );
  },
);
