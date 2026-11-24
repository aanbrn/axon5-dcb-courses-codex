import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { constants, existsSync, lstatSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = fileURLToPath(new URL('.', import.meta.url));
const lockfile = join(project, 'package-lock.json');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const nodeVersion = `v${readFileSync(join(project, '../../.nvmrc'), 'utf8').trim()}`;
const npmVersion = JSON.parse(readFileSync(join(project, 'package.json'), 'utf8')).packageManager.slice(4);
const defaultMarker = 'phase-one-static';

function stagedFile(staging) {
  return join(project, 'build', staging, 'public', 'index.html');
}

function build() {
  assert.equal(process.version, nodeVersion, 'Wrong Node executable');
  assert.ok(process.env.npm_execpath, 'Run this build through npm');
  const actualNpm = execFileSync(process.execPath, [process.env.npm_execpath, '--version'], { encoding: 'utf8' }).trim();
  assert.equal(actualNpm, npmVersion, 'Wrong npm executable');

  const marker = process.env.PROBE_MARKER ?? defaultMarker;
  const staging = process.env.PROBE_STAGING ?? 'staged';
  assert.match(marker, /^[a-z0-9-]{1,80}$/);
  assert.match(staging, /^staged(?:-[a-z0-9-]{1,35})?$/);
  const root = join(project, 'build');
  for (const directory of [root, join(root, staging), join(root, staging, 'public')]) {
    if (!existsSync(directory)) mkdirSync(directory);
    assert.ok(lstatSync(directory).isDirectory(), `Invalid staging directory ${directory}`);
  }

  const html = `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Static packaging probe</title>
<p id="marker">${marker}</p>
</html>
`;
  const flag = constants.O_WRONLY | constants.O_CREAT | constants.O_TRUNC | constants.O_NOFOLLOW;
  writeFileSync(stagedFile(staging), html, { flag });
  console.log(`Static asset built with Node ${process.version} and npm ${actualNpm}`);
}

function verifyFixture() {
  assert.equal(process.version, nodeVersion, 'Wrong Node executable');
  const initialLock = readFileSync(lockfile);
  const markers = [defaultMarker, `${defaultMarker}-changed`];
  const stage = 'frontend-fixture';
  const evidence = resolve(process.env.PROBE_EVIDENCE_DIR ?? join(project, '../build/reports/feasibility'));
  const env = { ...process.env, PROBE_STAGING: 'staged-fixture' };
  const artifacts = [];

  function cleanBuild(marker) {
    const output = stagedFile(env.PROBE_STAGING);
    const options = { cwd: project, env: { ...env, PROBE_MARKER: marker }, stdio: 'inherit' };
    execFileSync('npm', ['ci'], options);
    assert.deepEqual(readFileSync(lockfile), initialLock, 'npm ci changed the lockfile');
    execFileSync('npm', ['run', 'build'], options);
    const bytes = readFileSync(output);
    assert.ok(bytes.includes(`<p id="marker">${marker}</p>`), 'Expected marker was not built');
    return bytes;
  }

  const first = cleanBuild(markers[0]);
  rmSync(stagedFile(env.PROBE_STAGING));
  assert.deepEqual(cleanBuild(markers[0]), first, 'Identical inputs produced different bytes');
  const changed = cleanBuild(markers[1]);
  assert.notDeepEqual(changed, first, 'Changing the marker did not change the bytes');

  mkdirSync(evidence, { recursive: true });
  for (const [marker, bytes] of [[markers[0], first], [markers[1], changed]]) {
    const artifact = `${stage}-${marker}.html`;
    writeFileSync(join(evidence, artifact), bytes);
    artifacts.push(artifact);
  }
  console.log(`PROBE_SECONDARY ${JSON.stringify({ stage, artifacts, markers, repeatIdentical: true, lockfileSha256: sha256(initialLock) })}`);
}

try {
  if (process.argv[2] === '--verify-fixture') verifyFixture();
  else build();
} catch (error) {
  console.error(error);
  process.exitCode = Number.isInteger(error.status) ? error.status : 1;
}
