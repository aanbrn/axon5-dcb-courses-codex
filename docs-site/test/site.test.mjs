import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const project = fileURLToPath(new URL("../", import.meta.url));
const staged = process.env.DOCS_INPUT ?? join(project, "build/staged");
const eleventy = join(project, "node_modules/@11ty/eleventy/cmd.cjs");

function variant(t, { base = "/courses/", app = "", trustedOrigins = "" } = {}) {
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
      const result = spawnSync(process.execPath, [eleventy, `--output=${output}`], {
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
      });
      if (result.error) throw result.error;
      return result;
    },
  };
}

test("publication rejects a broken prefixed report fragment", (t) => {
  const site = variant(t);
  const guide = join(site.input, "maintainer-guide.md");
  const source = readFileSync(guide, "utf8");
  const changed = source.replace("#hosted-amd64-verification-and-retirement", "#missing-heading");
  assert.notEqual(changed, source, "the fixture must break the guide's report link");
  writeFileSync(guide, changed);

  const result = site.build();
  assert.equal(result.status, 1, "Eleventy must fail when a rendered fragment has no target");
  assert.match(result.stderr, /Missing fragment .*#missing-heading/);
});
