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
import { DomUtils, parseDocument } from "htmlparser2";
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

function articleRegions(output, path) {
  const { children } = parseDocument(readFileSync(join(output, path), "utf8"));
  const blocks = DomUtils.findAll(
    ({ name, children }) =>
      name === "table" ||
      (name === "pre" && children.some((child) => child.name === "code")),
    children,
  );
  assert.ok(blocks.length > 0, `${path} contains tables or code samples`);
  const names = blocks.map(({ name, parent }) => {
    const kind = name === "table" ? "Data table" : "Code sample";
    assert.equal(parent.attribs?.role, "region");
    assert.equal(parent.attribs.tabindex, "0");
    const label = parent.attribs["aria-label"]?.trim();
    assert.ok(
      label?.startsWith(`${kind} — `),
      `${path} has a contextual ${kind}`,
    );
    return label;
  });
  assert.equal(
    new Set(names).size,
    names.length,
    `${path} has duplicate region names: ${names.join("; ")}`,
  );
  return names;
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
    "fonts/geist-LICENSE.txt",
    "fonts/geist-latin-wght-normal.woff2",
    "fonts/geist-mono-LICENSE.txt",
    "fonts/geist-mono-latin-wght-normal.woff2",
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
  const css = readFileSync(join(distribution, "site.css"), "utf8");
  for (const name of ["geist", "geist-mono"]) {
    const asset = `fonts/${name}-latin-wght-normal.woff2`;
    assert.ok(
      css.includes(`./${asset}`),
      `Missing font declaration for ${name}`,
    );
    assert.deepEqual(
      readFileSync(join(distribution, asset)),
      readFileSync(join(staged, asset)),
    );
    assert.match(
      readFileSync(join(distribution, `fonts/${name}-LICENSE.txt`), "utf8"),
      /SIL OPEN FONT LICENSE/i,
    );
  }
});

test("the root site offers the local quick start as its only launch action", (t) => {
  const site = variant(t, { base: "/" });
  const result = site.build();
  assert.equal(result.status, 0, result.stderr);
  assertLaunch(site.output, "/quick-start/", "Read quick start");
});

for (const base of ["/", "/courses/"]) {
  for (const [name, fixture, diagnostic, target] of [
    [
      "raw anchor with spaces around equals",
      '<a href = "../missing-raw-article/">Missing article</a>',
      "Missing destination",
      "missing-raw-article/",
    ],
    [
      "raw image with an unquoted source",
      "<img SRC=../missing-image.svg alt=Fixture>",
      "Missing destination",
      "missing-image.svg",
    ],
    [
      "Markdown link",
      "[Missing article](../missing-markdown-article/)",
      "Missing destination",
      "missing-markdown-article/",
    ],
    [
      "missing fragment on an existing page",
      "[Missing section](../maintainer-guide/#missing-section)",
      "Missing fragment",
      "#missing-section",
    ],
    [
      "fragment matching only a non-anchor name",
      '<span name="not-an-anchor">Fixture</span>\n\n[Missing ID](#not-an-anchor)',
      "Missing fragment",
      "#not-an-anchor",
    ],
  ]) {
    test(`publication at ${base} rejects a broken ${name}`, (t) => {
      const site = variant(t, { base });
      appendFileSync(join(site.input, "quick-start.md"), `\n\n${fixture}\n`);
      const result = site.build();
      assert.equal(result.status, 1, result.stderr || result.stdout);
      assert.ok(
        result.stderr
          .split("\n")
          .some(
            (line) =>
              line.includes(`${diagnostic} in quick-start/index.html:`) &&
              line.includes(target),
          ),
        result.stderr,
      );
    });
  }

  test(`publication at ${base} accepts real destinations and fragment targets`, (t) => {
    const site = variant(t, { base });
    appendFileSync(
      join(site.input, "quick-start.md"),
      [
        "",
        "",
        '<span ID = "caf&eacute;">Decoded ID</span>',
        "<a NAME=legacy-target>Legacy anchor</a>",
        '<a HREF="#caf%C3%A9">Decoded ID link</a>',
        "<a href=#legacy-target>Legacy anchor link</a>",
        '<a href = "../site.css">Stylesheet</a>',
        "[Guide](../maintainer-guide/#setup-and-diagnostics)",
        "",
        '<!-- <a href="../ignored-comment/">Comment</a> -->',
        "",
        '`<a href="../ignored-example/">Code</a>`',
        "",
      ].join("\n"),
    );
    const result = site.build();
    assert.equal(result.status, 0, result.stderr);
    verifyPublication(site.output, base);
  });
}

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

test("published article regions have distinct contextual names", () => {
  const quickStart = articleRegions(distribution, "quick-start/index.html");
  assert.deepEqual(
    quickStart.filter((name) => name.includes("Start the shell")),
    ["Start the BFF", "Start the web app", "Start the documentation"].map(
      (step) => `Code sample — Start the shell — ${step}`,
    ),
  );

  const report = articleRegions(
    distribution,
    "feasibility/phase-01/index.html",
  );
  assert.ok(report.includes("Data table — Phase 01 feasibility record"));
  assert.deepEqual(
    report.filter((name) => name.includes("Reproduce the proof")),
    [1, 2].map((number) => `Code sample — Reproduce the proof (${number})`),
  );

  const guide = articleRegions(distribution, "maintainer-guide/index.html");
  assert.ok(guide.includes("Data table — Version owners"));
  assert.deepEqual(
    guide.filter((name) => name.includes("Setup and diagnostics")),
    [1, 2, 3, 4].map(
      (number) => `Code sample — Setup and diagnostics (${number})`,
    ),
  );
});

test("region names stay distinct for repeated headings and tables without captions", (t) => {
  const path = "quick-start/index.html";
  const heading = '## Example **commands** &amp; "output"';
  const fence = "```sh\nprintf '%s\\n' example\n```";
  const table = "| Tool |\n| --- |\n| Gradle |";
  const fixture = [
    "",
    "",
    heading,
    fence,
    '**Comparison** &amp; "details":',
    table,
    "More examples.",
    table,
    "Additional examples.",
    table,
    heading,
    fence,
    "",
  ].join("\n\n");

  const labels = ["/", "/courses/"].map((base) => {
    const site = variant(t, { base });
    appendFileSync(join(site.input, "quick-start.md"), fixture);
    const result = site.build();
    assert.equal(result.status, 0, result.stderr);
    return articleRegions(site.output, path).slice(-5);
  });
  assert.deepEqual(labels[0], [
    'Code sample — Example commands & "output"',
    'Data table — Example commands & "output" — Comparison & "details"',
    'Data table — Example commands & "output" (2)',
    'Data table — Example commands & "output" (3)',
    'Code sample — Example commands & "output" (example-commands-output-2)',
  ]);
  assert.deepEqual(labels[1], labels[0]);
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
