import assert from "node:assert/strict";
import { test } from "node:test";
import { chromium } from "playwright";

const directoryPath = "/api/demo-roles";

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
  const browser = await chromium.launch({ timeout: 10_000 });
  try {
    const page = await browser.newPage();
    await traceRoles(page, process.env.ROLE_TRACER_WEB_ORIGIN, process.env.ROLE_TRACER_BFF_ORIGIN);
  } finally {
    await browser.close();
  }
});
