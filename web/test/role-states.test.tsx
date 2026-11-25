import assert from "node:assert/strict";
import { test, type TestContext } from "node:test";
import type { BrowserContext, Page, Route } from "playwright";

const roleRequest = "**/api/demo-roles";
const roleKey = "courses.demo.role";
const administrator = { id: "admin_directory", label: "Administrator", kind: "administrator" };
const maya = { id: "Student_Maya", label: "Maya Chen", kind: "student" };
const oneStudent = { administrator, students: [maya] };
const loadingMessage = "Loading demo roles…";
const errorMessage = "Could not load demo roles. Try again to switch roles.";

type RoleFixture = {
  openContext: (t: TestContext) => Promise<BrowserContext>;
  webOrigin: () => string;
  developmentOrigin: (t: TestContext) => Promise<string>;
};

function saveRoleOnLoad(page: Page, id: string) {
  return page.addInitScript(({ key, id }) => sessionStorage.setItem(key, id), { key: roleKey, id });
}

function storedRole(page: Page) {
  return page.evaluate((key) => sessionStorage.getItem(key), roleKey);
}

function roleSelector(page: Page) {
  return page.getByLabel("Demo role", { exact: true });
}

async function assertNavigation(page: Page) {
  const nav = page.getByRole("navigation", { name: "Documentation" });
  const docs = nav.getByRole("link", { name: "Documentation", exact: true });
  const quick = nav.getByRole("link", { name: "Quick start", exact: true });
  const report = page.getByRole("main").getByRole("link", { name: "Read feasibility report" });
  for (const link of [docs, quick, report]) assert.equal(await link.isVisible(), true);
  const docsBase = await docs.getAttribute("href");
  assert.ok(docsBase);
  assert.equal(await quick.getAttribute("href"), new URL("quick-start/", docsBase).href);
  assert.equal(await report.getAttribute("href"), new URL("feasibility/phase-01/", docsBase).href);
}

async function assertFailure(page: Page) {
  const alert = page.getByRole("alert");
  await alert.waitFor();
  assert.equal(await page.getByText(errorMessage, { exact: true }).count(), 1);
  const select = roleSelector(page);
  assert.equal(await select.isDisabled(), true);
  assert.equal(await select.locator("option:checked").textContent(), "Roles unavailable");
  assert.equal(await storedRole(page), maya.id, "A failed directory must preserve the stored role");
  await assertNavigation(page);
}

const failHttp = (route: Route) => route.fulfill({ status: 503 });
const failureResponses = {
  "a transport failure": (route: Route) => route.abort("connectionfailed"),
  "an HTTP failure": failHttp,
  "malformed JSON in an HTTP 200": (route: Route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: '{"administrator":' }),
  "a missing administrator": (route: Route) => route.fulfill({ json: { students: [maya] } }),
  "a missing student label": (route: Route) =>
    route.fulfill({ json: { administrator, students: [{ id: maya.id, kind: maya.kind }] } }),
  "an invalid student kind": (route: Route) =>
    route.fulfill({ json: { administrator, students: [{ ...maya, kind: administrator.kind }] } }),
  "a duplicate role ID": (route: Route) =>
    route.fulfill({ json: { administrator, students: [{ ...maya, id: administrator.id }] } }),
};

export function registerRoleStateTests({ openContext, webOrigin, developmentOrigin }: RoleFixture) {
  async function openPage(t: TestContext) {
    return (await openContext(t)).newPage();
  }

  test("keeps retry mounted, ignores repeat keys and restores focus after recovery", async (t) => {
    const page = await openPage(t);
    await saveRoleOnLoad(page, maya.id);
    const failedRetry = Promise.withResolvers<void>();
    const successfulRetry = Promise.withResolvers<void>();
    let attempts = 0;
    await page.route(roleRequest, async (route) => {
      switch (++attempts) {
        case 1:
          return failHttp(route);
        case 2:
          await failedRetry.promise;
          return failHttp(route);
        case 3:
          await successfulRetry.promise;
          return route.fulfill({ json: oneStudent });
        default:
          return route.abort();
      }
    });
    await page.goto(webOrigin());
    await page.getByRole("alert").waitFor();
    const retry = page.getByRole("button", { name: "Retry loading roles", exact: true });
    assert.equal(await retry.count(), 1, "A directory failure offers a retry button");
    await assertFailure(page);
    const button = await retry.elementHandle();
    assert.ok(button);

    try {
      await Promise.all([page.waitForRequest(roleRequest), retry.press("Enter")]);
      assert.equal(await retry.getAttribute("aria-disabled"), "true");
      const status = page.getByRole("status").filter({ hasText: loadingMessage });
      await status.waitFor();
      assert.equal(await button.evaluate((element) => element === document.activeElement), true);
      await retry.press("Space");
      await retry.press("Enter");
      assert.equal(await attempts, 2);
      await assertNavigation(page);
      assert.equal(await storedRole(page), maya.id);

      failedRetry.resolve();
      await assertFailure(page);
      assert.equal(await retry.isEnabled(), true);
      assert.equal(await button.evaluate((element) => element === document.activeElement), true);

      await Promise.all([page.waitForRequest(roleRequest), retry.press("Space")]);
      assert.equal(await retry.getAttribute("aria-disabled"), "true");
      successfulRetry.resolve();
      const select = roleSelector(page);
      await select.locator(`option[value="${maya.id}"]`).waitFor({ state: "attached" });
      assert.equal(await select.inputValue(), maya.id);
      assert.equal(await select.evaluate((element) => element === document.activeElement), true);
      assert.equal(await retry.count(), 0);
      assert.equal(await page.getByRole("alert").count(), 0);
      assert.equal(await status.count(), 0);
      assert.equal(await attempts, 3);
    } finally {
      failedRetry.resolve();
      successfulRetry.resolve();
    }
  });

  test("preserves docs focus when the reader moves away during retry", async (t) => {
    const page = await openPage(t);
    const release = Promise.withResolvers<void>();
    let attempted = false;
    await page.route(roleRequest, async (route) => {
      if (!attempted) {
        attempted = true;
        return failHttp(route);
      }
      await release.promise;
      return route.fulfill({ json: oneStudent });
    });
    await page.goto(webOrigin());
    const retry = page.getByRole("button", { name: "Retry loading roles" });
    const quick = page.getByRole("link", { name: "Quick start", exact: true });
    try {
      await Promise.all([page.waitForRequest(roleRequest), retry.press("Enter")]);
      await quick.focus();
      release.resolve();
      await roleSelector(page).locator(`option[value="${maya.id}"]`).waitFor({ state: "attached" });
      assert.equal(
        await quick.evaluate((element) => element === document.activeElement),
        true,
        "Retry must preserve focus on the documentation link",
      );
    } finally {
      release.resolve();
    }
  });

  test("keeps navigation and a polite region available through the initial load and an empty directory", async (t) => {
    const page = await openPage(t);
    const release = Promise.withResolvers<void>();
    await page.route(roleRequest, async (route) => {
      await release.promise;
      await route.fulfill({ json: { administrator, students: [] } });
    });
    const select = roleSelector(page);
    const status = page.getByRole("status");
    try {
      await Promise.all([page.waitForRequest(roleRequest), page.goto(webOrigin())]);
      await assertNavigation(page);
      assert.equal(await select.isVisible(), true);
      assert.equal(await select.isDisabled(), true);
      assert.equal(await select.locator("option:checked").textContent(), loadingMessage);
      assert.equal(await status.textContent(), loadingMessage);
      await status.evaluate((element) => element.setAttribute("data-test-status", "initial"));
    } finally {
      release.resolve();
    }
    await page.getByRole("heading", { name: "No demo students available" }).waitFor();
    assert.equal(await status.getAttribute("data-test-status"), "initial");
    assert.equal(await status.textContent(), "");
    assert.equal(await select.inputValue(), administrator.id);
    assert.equal(await select.locator("option").count(), 1);
    const emptyQuick = page.getByText("You can continue as Administrator or", { exact: false })
      .getByRole("link", { name: "quick start", exact: true });
    const quick = page.getByRole("navigation").getByRole("link", { name: "Quick start" });
    assert.equal(await emptyQuick.getAttribute("href"), await quick.getAttribute("href"));
  });

  for (const [name, response] of Object.entries(failureResponses)) {
    test(`preserves the saved role after ${name}`, async (t) => {
      const page = await openPage(t);
      await saveRoleOnLoad(page, maya.id);
      await page.route(roleRequest, response);
      await page.goto(webOrigin());
      await assertFailure(page);
    });
  }

  test("selects the one student with keyboard input while storage is denied", async (t) => {
    const page = await openPage(t);
    const label = "Maya <em>Chen</em> — student with an extended demo label";
    await page.addInitScript(() => {
      Object.defineProperty(window, "sessionStorage", {
        get() { throw new DOMException("Storage is disabled", "SecurityError"); },
      });
    });
    await page.route(roleRequest, (route) =>
      route.fulfill({ json: { administrator, students: [{ ...maya, label }] } }),
    );
    const errors: Error[] = [];
    page.on("pageerror", (error) => errors.push(error));
    await page.goto(webOrigin());
    const select = roleSelector(page);
    const studentOption = select.locator(`option[value="${maya.id}"]`);
    await studentOption.waitFor({ state: "attached" });
    assert.equal(await studentOption.textContent(), label);
    assert.equal(await select.inputValue(), administrator.id);
    await select.press("m");
    assert.equal(await select.inputValue(), maya.id);
    assert.equal(await select.evaluate((element) => element === document.activeElement), true);
    await select.selectOption(administrator.id);
    assert.equal(await select.inputValue(), administrator.id);
    assert.deepEqual(errors, []);
  });

  test("ignores an aborted load that resolves after its replacement", { timeout: 15_000 }, async (t) => {
    const page = await openPage(t);
    await saveRoleOnLoad(page, maya.id);
    await page.addInitScript(() => {
      const fetch = window.fetch.bind(window);
      const requests: Array<{ signal: RequestInit["signal"]; resolve: (response: Response) => void }> = [];
      Object.assign(window, { roleRequests: requests });
      window.fetch = (input, init) => {
        if (input !== "/api/demo-roles") return fetch(input, init);
        const { promise, resolve } = Promise.withResolvers<Response>();
        requests.push({ signal: init?.signal, resolve });
        return promise;
      };
    });
    await page.goto(await developmentOrigin(t));
    await page.waitForFunction(() => (window as Window & { roleRequests: unknown[] }).roleRequests.length === 2);
    const aborted = await page.evaluate((directory) => {
      const { roleRequests: [older, newer] } = window as Window & {
        roleRequests: Array<{ signal: AbortSignal; resolve: (response: Response) => void }>;
      };
      newer.resolve(Response.json(directory));
      return older.signal.aborted;
    }, oneStudent);
    assert.equal(aborted, true);
    const select = roleSelector(page);
    await select.locator(`option[value="${maya.id}"]`).waitFor({ state: "attached" });
    assert.equal(await select.inputValue(), maya.id);
    await page.evaluate(async (administrator) => {
      const { roleRequests: [older] } = window as Window & {
        roleRequests: Array<{ resolve: (response: Response) => void }>;
      };
      const response = Response.json({ administrator, students: [] });
      const body = response.text.bind(response);
      const consumed = Promise.withResolvers<void>();
      response.text = async () => {
        const text = await body();
        consumed.resolve();
        return text;
      };
      older.resolve(response);
      await consumed.promise;
      await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    }, administrator);
    assert.equal(await select.inputValue(), maya.id);
    assert.equal(await storedRole(page), maya.id);
    assert.equal(await page.getByRole("heading", { name: "No demo students available" }).count(), 0);
  });
}
