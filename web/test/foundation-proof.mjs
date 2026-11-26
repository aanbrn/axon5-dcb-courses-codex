import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  cp,
  mkdir,
  mkdtemp,
  readFile,
  rm,
  symlink,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const web = fileURLToPath(new URL("../", import.meta.url));
const steiger = "steiger/dist/cli.mjs";
const vitest = "vitest/vitest.mjs";

async function snapshot(t, paths) {
  const workingDir = await mkdtemp(join(tmpdir(), "courses-web-foundation-"));
  t.after(() => rm(workingDir, { recursive: true, force: true }));
  await mkdir(join(workingDir, "build"));
  await Promise.all(
    [...paths, "src", "tsconfig.json", "package.json"].map((path) =>
      cp(join(web, path), join(workingDir, path), { recursive: true }),
    ),
  );
  await symlink(
    join(web, "node_modules"),
    join(workingDir, "node_modules"),
    "junction",
  );
  return workingDir;
}

function run(workingDir, tool, args) {
  const result = spawnSync(
    process.execPath,
    [join(web, "node_modules", tool), ...args],
    {
      cwd: workingDir,
      encoding: "utf8",
      env: { ...process.env, NO_COLOR: "1" },
      timeout: 30_000,
    },
  );
  assert.ifError(result.error);
  assert.equal(result.signal, null);
  return {
    status: result.status,
    stdout: result.stdout,
    output: result.stdout + result.stderr,
  };
}

test("Steiger accepts authored layers and rejects a shared import from pages", async (t) => {
  const workingDir = await snapshot(t, ["steiger.config.ts"]);
  const lint = () =>
    run(workingDir, steiger, [
      "./src",
      "--config",
      "steiger.config.ts",
      "--reporter",
      "json",
    ]);
  const baseline = lint();
  assert.equal(
    baseline.status,
    0,
    `Steiger should accept the authored layers:\n${baseline.output}`,
  );

  const importPath = "src/shared/lib/utils.ts";
  const changed = join(workingDir, importPath);
  const original = await readFile(changed, "utf8");
  await writeFile(changed, `${original}\nimport "@/pages/home";\n`);
  const broken = lint();
  assert.equal(
    broken.status,
    1,
    `Steiger should reject the shared import:\n${broken.output}`,
  );
  const violations = JSON.parse(broken.stdout);
  assert.deepEqual(
    violations.map(({ ruleName }) => ruleName),
    ["fsd/forbidden-imports"],
    broken.output,
  );
  assert.ok(violations[0].location.path.endsWith(importPath), broken.output);
  t.diagnostic("fsd/forbidden-imports rejected the shared-to-pages import");

  await writeFile(changed, original);
  const repaired = lint();
  assert.equal(repaired.status, 0, repaired.output);
});

test("axe rejects an unnamed Storybook button and accepts the restored name", async (t) => {
  const workingDir = await snapshot(t, [
    ".storybook",
    "build/generated",
    "vitest.config.ts",
  ]);
  const storyPath = "src/shared/ui/Controls.stories.tsx";
  const reportPath = join(workingDir, "vitest-result.json");
  const verify = async (status) => {
    await rm(reportPath, { force: true });
    const result = run(workingDir, vitest, [
      "run",
      "--project",
      "storybook",
      storyPath,
      "--testNamePattern",
      "^Actions$",
      "--reporter",
      "json",
      "--outputFile",
      reportPath,
    ]);
    const reportText = await readFile(reportPath, "utf8").catch(() => "");
    assert.equal(result.status, status, result.output + reportText);
    assert.ok(reportText, result.output);
    const report = JSON.parse(reportText);
    const actions = report.testResults
      .flatMap(({ assertionResults }) => assertionResults)
      .filter(({ title }) => title === "Actions");
    assert.equal(actions.length, 1, JSON.stringify(report));
    assert.equal(
      actions[0].status,
      status === 0 ? "passed" : "failed",
      JSON.stringify(actions[0]),
    );
    return actions[0].failureMessages.join("\n");
  };
  await verify(0);

  const changed = join(workingDir, storyPath);
  const original = await readFile(changed, "utf8");
  const namedButton =
    /(<Button[^>]*variant="outline"[^>]*>)\s*Retry loading roles\s*(<\/Button>)/;
  assert.match(
    original,
    namedButton,
    "The Actions story should render the named retry button",
  );
  await writeFile(changed, original.replace(namedButton, "$1$2"));
  const diagnostic = await verify(1);
  assert.match(diagnostic, /\/button-name\b/, diagnostic);
  t.diagnostic("axe button-name rejected the unnamed retry button");

  await writeFile(changed, original);
  await verify(0);
});
