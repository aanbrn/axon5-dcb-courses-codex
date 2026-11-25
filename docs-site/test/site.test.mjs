import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  appendFileSync,
  cpSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative, sep } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { verifyPublication } from "../verify-site.mjs";

const project = fileURLToPath(new URL("../", import.meta.url));
const staged = process.env.DOCS_INPUT ?? join(project, "build/staged");
const distribution = process.env.DOCS_OUTPUT ?? join(project, "build/site");
const canonical =
  process.env.DOCS_CANONICAL_REPORT ??
  join(project, "../docs/feasibility/phase-01.md");
const eleventy = join(project, "node_modules/@11ty/eleventy/cmd.cjs");

function variant(
  t,
  { base = "/courses/", app = "", trustedOrigins = "" } = {},
) {
  const workspace = mkdtempSync(join(dirname(staged), "site-check-"));
  t.after(() => rmSync(workspace, { recursive: true, force: true }));
  const input = join(workspace, "input");
  const output = join(workspace, "site");
  cpSync(staged, input, { recursive: true });

  return {
    input,
    output,
    workspace,
    build() {
      const result = spawnSync(
        process.execPath,
        [eleventy, `--output=${output}`],
        {
          cwd: project,
          env: {
            ...process.env,
            DOCS_INPUT: input,
            DOCS_BASE: base,
            DOCS_APP_URL: app,
            DOCS_TRUSTED_APP_ORIGINS: trustedOrigins,
          },
          encoding: "utf8",
          timeout: 15_000,
        },
      );
      if (result.error) throw result.error;
      return result;
    },
  };
}

function assertLaunch(output, href, label) {
  const home = readFileSync(join(output, "index.html"), "utf8");
  const actions = Array.from(
    home.matchAll(/<a class="launch-action" href="([^"]+)">([^<]+)<\/a>/g),
    ([, target, text]) => [target.replaceAll("&amp;", "&"), text],
  );
  assert.deepEqual(actions, [[href, label]]);
}

test("Gradle stages only approved sources and preserves the canonical report bytes", () => {
  const names = readdirSync(staged, { recursive: true, withFileTypes: true })
    .filter((entry) => !entry.isDirectory())
    .map((entry) =>
      relative(staged, join(entry.parentPath, entry.name)).split(sep).join("/"),
    )
    .sort();
  assert.deepEqual(names, [
    "_includes/page.11ty.js",
    "feasibility/phase-01.11tydata.json",
    "feasibility/phase-01.md",
    "index.11ty.js",
    "maintainer-guide.md",
    "quick-start.md",
    "site.css",
  ]);
  assert.deepEqual(
    readFileSync(join(staged, "feasibility/phase-01.md")),
    readFileSync(canonical),
  );
  verifyPublication(distribution, process.env.DOCS_BASE ?? "/");
});

test("the root site offers the local quick start as its only launch action", (t) => {
  const site = variant(t, { base: "/" });
  const result = site.build();
  assert.equal(result.status, 0, result.stderr);
  assertLaunch(site.output, "/quick-start/", "Read quick start");
});

test("the nested site offers the configured trusted app URL and keeps all navigation in scope", (t) => {
  const app = "https://demo.example.invalid/enroll/?view=demo&mode=student";
  const site = variant(t, {
    app,
    trustedOrigins: "https://demo.example.invalid",
  });
  const result = site.build();
  assert.equal(result.status, 0, result.stderr);
  assertLaunch(site.output, app, "Open demo");

  const home = readFileSync(join(site.output, "index.html"), "utf8");
  for (const route of [
    "",
    "quick-start/",
    "feasibility/phase-01/",
    "maintainer-guide/",
    "site.css",
  ]) {
    assert.ok(
      home.includes(`href="/courses/${route}"`),
      `Missing /courses/${route}`,
    );
  }
  for (const [path, title] of [
    ["index.html", "Run the demo"],
    ["quick-start/index.html", "Quick start"],
    ["feasibility/phase-01/index.html", "Phase 01 feasibility record"],
    ["maintainer-guide/index.html", "Maintainer guide"],
  ]) {
    const page = readFileSync(join(site.output, path), "utf8");
    assert.equal(page.match(/<h1\b[^>]*>([^<]+)<\/h1>/)?.[1], title);
    assert.equal(page.match(/aria-current="page"/g)?.length, 1);
    assert.match(page, /href="#main-content">Skip to main content/);
  }

  const report = readFileSync(
    join(site.output, "feasibility/phase-01/index.html"),
    "utf8",
  );
  assert.match(
    report,
    /role="region" aria-label="Data table [^"]+" tabindex="0"><table>/,
  );
  assert.match(
    report,
    /role="region" aria-label="Code sample [^"]+" tabindex="0"><pre><code class="language-sh">/,
  );
  assert.match(report, /<h2 id="hosted-amd64-verification-and-retirement">/);
  assert.match(report, /Phase 7 owns the first hosted AMD64 DCB runtime proof/);
  assert.match(
    report,
    /committed multi-tag write, rejection of an overlapping append, and a cross-process subscription update correlated with the persisted event/,
  );
  assert.match(report, /passing representative browser workflow in Playwright/);
  assert.match(
    readFileSync(join(site.output, "site.css"), "utf8"),
    /overflow-x:\s*auto/,
  );
});

test("the local Vite app origin is allowed under a nested base", (t) => {
  const app = "http://127.0.0.1:5173/";
  const site = variant(t, { app });
  const result = site.build();
  assert.equal(result.status, 0, result.stderr);
  assertLaunch(site.output, app, "Open demo");
});

test("invalid launch URLs and deployment bases reject the build", async (t) => {
  for (const [options, reason] of [
    [{ app: "javascript:alert(1)" }, /Expected an absolute HTTP\(S\) app URL/],
    [
      { app: "//demo.example.invalid/" },
      /Expected an absolute HTTP\(S\) app URL/,
    ],
    [{ app: "https://user@demo.example.invalid/" }, /without credentials/],
    [
      {
        app: "https://other.example.invalid",
        trustedOrigins: "https://demo.example.invalid",
      },
      /trusted app origin/,
    ],
    [
      {
        app: "http://demo.example.invalid",
        trustedOrigins: "http://demo.example.invalid",
      },
      /comma-separated HTTPS origins/,
    ],
    [{ base: "/courses/../" }, /slash-delimited deployment path/],
  ]) {
    await t.test(options.app ?? options.base, (subtest) => {
      const result = variant(subtest, options).build();
      assert.equal(result.status, 1, result.stderr);
      assert.match(result.stderr, reason);
    });
  }
});

test("publication excludes a private fixture and detects contamination of a rendered copy", (t) => {
  const site = variant(t);
  const excludedName = "synthetic-private-advisory-fixture";
  const excludedBytes = Buffer.from("synthetic-only-5bd26f6134df");
  const leak = { excludedName, excludedBytes };
  writeFileSync(join(site.workspace, `${excludedName}.md`), excludedBytes);
  const result = site.build();
  assert.equal(result.status, 0, result.stderr);
  verifyPublication(site.output, "/courses/", leak);

  const copiedPrivateFile = join(site.output, `${excludedName}.md`);
  writeFileSync(copiedPrivateFile, excludedBytes);
  assert.throws(
    () => verifyPublication(site.output, "/courses/", leak),
    /Excluded fixture filename/,
  );
  assert.throws(
    () => verifyPublication(site.output, "/courses/"),
    /Unexpected public artifact/,
  );
  rmSync(copiedPrivateFile);
  appendFileSync(join(site.output, "site.css"), excludedBytes);
  assert.throws(
    () => verifyPublication(site.output, "/courses/", leak),
    /Excluded fixture bytes in site.css/,
  );
});

test("the rendered maintainer guide publishes scope and provenance without advisory inputs", (t) => {
  const site = variant(t);
  const fixtureName = "synthetic-b8-input";
  const excludedBytes = Buffer.from(
    "synthetic-b8-inventory-feed-result-879fcfa6",
  );
  writeFileSync(join(site.workspace, `${fixtureName}.json`), excludedBytes);
  const result = site.build();
  assert.equal(result.status, 0, result.stderr);
  verifyPublication(site.output, "/courses/", {
    excludedName: fixtureName,
    excludedBytes,
  });

  const guide = readFileSync(
    join(site.output, "maintainer-guide/index.html"),
    "utf8",
  );
  assert.match(
    guide,
    /href="\/courses\/feasibility\/phase-01\/#dependency-and-image-review"/,
  );
  assert.match(guide, /<strong>B8 status: incomplete\.<\/strong>/);
  assert.match(guide, /<code>:bff:runtimeClasspath<\/code>/);
  assert.match(guide, /<code>:probe:testRuntimeClasspath<\/code>/);
  assert.match(guide, /<code>:probe:integrationTestRuntimeClasspath<\/code>/);
  assert.match(guide, /authorized external local directory/);
  assert.match(guide, /2026-12-01/);
  assert.match(guide, /2026-12-02/);
});

test("publication rejects a broken prefixed report fragment", (t) => {
  const site = variant(t);
  const guide = join(site.input, "maintainer-guide.md");
  const source = readFileSync(guide, "utf8");
  const changed = source.replace(
    "#hosted-amd64-verification-and-retirement",
    "#missing-heading",
  );
  assert.notEqual(
    changed,
    source,
    "the fixture must break the guide's report link",
  );
  writeFileSync(guide, changed);

  const result = site.build();
  assert.equal(
    result.status,
    1,
    "Eleventy must fail when a rendered fragment has no target",
  );
  assert.match(result.stderr, /Missing fragment .*#missing-heading/);
});
