"""Verify the Phase 2 build and runnable reader entry points."""

import contextlib
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import signal
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = Path("bff/src/main/resources/static/openapi.json")
LOCKS = (
    Path("web/package-lock.json"),
    Path("docs-site/package-lock.json"),
    Path("tools/style/package-lock.json"),
    Path("probe/typeid/package-lock.json"),
    Path("probe/web/package-lock.json"),
)
OUTPUTS = {
    ":web:generateClient": "web/build/generated",
    ":web:webBuild": "web/build/dist",
    ":web:buildStorybook": "web/build/storybook",
    ":docs-site:docsBuild": "docs-site/build/site",
}
TEST_SUITES = {
    ":bff:test": "bff/build/test-results/test",
    ":bff:componentTest": "bff/build/test-results/componentTest",
    ":probe:test": "probe/build/test-results/test",
}
REQUIRED = {
    *OUTPUTS,
    *TEST_SUITES,
    ":bff:bootJar",
    ":bff:verifyFixtureIsolation",
    ":web:typecheck",
    ":web:fsdCheck",
    ":web:webCheck",
    ":docs-site:docsCheck",
}
FORBIDDEN = re.compile(
    r"docker|compose|bootrun|(?:image|paket|packaging)|integrationtest|"
    r"browser|playwright|tracer|smoke|storytest|foundationproof",
    re.IGNORECASE,
)
BUILD_PATHS = (
    ".githooks",
    ".gitignore",
    ".java-version",
    ".nvmrc",
    "build.gradle.kts",
    "mise.toml",
    "settings.gradle.kts",
    "gradlew",
    "bff",
    "build-logic",
    "config",
    "docs",
    "docs-site",
    "fixtures",
    "gradle",
    "probe",
    "tools",
    "web",
)


def copy_candidate(directory):
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *BUILD_PATHS], cwd=ROOT
    )
    directory.mkdir()
    for raw_path in paths.rstrip(b"\0").split(b"\0"):
        path = Path(os.fsdecode(raw_path))
        source = ROOT / path
        if source.is_symlink() or not source.is_file():
            raise RuntimeError(f"Expected a regular tracked build input: {path}")
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def task_outcomes(output, *, dry_run=False):
    pattern = (
        r"^(:[\w:.-]+) (SKIPPED)$"
        if dry_run
        else r"^> Task (:[\w:.-]+)(?: ([A-Z-]+))?$"
    )
    return {
        task: status or "EXECUTED" for task, status in re.findall(pattern, output, re.M)
    }


def snapshot(directory):
    return {
        path.relative_to(directory): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


class AssetLinks(HTMLParser):
    def __init__(self, entry):
        super().__init__()
        self.assets = []
        self.feed(entry.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "module":
            self.assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.assets.append(attrs["href"])


def fetch(url):
    # The fixtures listen on IPv4 loopback and need no configured HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=2) as response:
        if response.status != 200 or response.url != url:
            raise RuntimeError(
                f"Expected HTTP 200 at {url}, received {response.status} at {response.url}"
            )
        return response.read()


def verify_available_ports():
    for port in (8080, 5173, 8081):
        with socket.socket() as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", port))


@contextlib.contextmanager
def launch(command, directory, environment, endpoint):
    with tempfile.TemporaryFile(mode="w+b") as output:
        print(f"Launching {shlex.join(command)}", flush=True)
        child = subprocess.Popen(
            command,
            cwd=directory,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + 100
            while child.poll() is None and time.monotonic() < deadline:
                try:
                    body = fetch(endpoint)
                except (OSError, urllib.error.URLError):
                    time.sleep(0.15)
                else:
                    yield body
                    break
            else:
                output.seek(max(0, output.seek(0, os.SEEK_END) - 8000))
                log = output.read().decode(errors="replace")
                raise RuntimeError(f"{endpoint} did not become ready\n{log}")
        finally:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            finally:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=5)


class Phase2BuildTest(unittest.TestCase):
    def test_installed_hook_survives_a_clean_build(self):
        with tempfile.TemporaryDirectory(prefix="courses-post-clean-hook-") as scratch:
            directory = Path(scratch) / "candidate"
            copy_candidate(directory)
            environment = {
                **os.environ,
                "DOCKER_HOST": "tcp://127.0.0.1:1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_CONFIG_NOSYSTEM": "1",
            }
            for name in (
                "DOCKER_CONTEXT",
                "GIT_DIR",
                "GIT_INDEX_FILE",
                "GIT_WORK_TREE",
                "GIT_CONFIG_COUNT",
            ):
                environment.pop(name, None)

            def git(*args):
                result = subprocess.run(
                    ["git", *args],
                    cwd=directory,
                    env=environment,
                    capture_output=True,
                    timeout=120,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                return result.stdout

            git("init", "-q", "--initial-branch=hook-fixture")
            git("config", "user.name", "Post-clean Hook Fixture")
            git("config", "user.email", "hook-fixture@example.test")
            git("add", "--", *BUILD_PATHS)
            git("commit", "-qm", "Baseline build inputs")
            self.run_build(directory, environment, "installGitHooks")
            self.assertEqual(git("config", "--local", "core.hooksPath"), b".githooks\n")
            self.run_build(directory, environment, "clean", "build", "--no-build-cache")

            kotlin = "HookProof.kt"
            (directory / kotlin).write_bytes(
                b"/** Returns the proof value. */\nfun proof( ):Int=1\n"
            )
            typescript = "web/src/app/main.tsx"
            app = directory / typescript
            original = app.read_bytes()
            app.write_bytes(original.rstrip(b"\n") + b"   \n")
            git("add", "--", kotlin, typescript)
            git("commit", "-qm", "Format an ordinary commit after clean build")
            self.assertEqual(
                git("show", f"HEAD:{kotlin}"),
                b"/** Returns the proof value. */\nfun proof(): Int = 1\n",
            )
            self.assertEqual(git("show", f"HEAD:{typescript}"), original)
            self.assertEqual(app.read_bytes(), original)
            print(
                "The installed hook formatted Kotlin and TypeScript after clean build.",
                flush=True,
            )

    def test_site_smoke_is_a_public_verification_task(self):
        result = subprocess.run(
            ["./gradlew", "--console=plain", ":web:tasks", "--group", "verification"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        tasks = {line.partition(" - ")[0] for line in result.stdout.splitlines()}
        self.assertIn(
            "siteSmoke", tasks, "The runnable reader smoke must be discoverable"
        )

    def assert_build_graph(self, outcomes):
        self.assertFalse(
            [task for task in outcomes if FORBIDDEN.search(task)],
            "An infrastructure or opt-in browser task entered the ordinary build graph",
        )
        self.assertLessEqual(REQUIRED, outcomes.keys())
        ordered = list(outcomes)
        self.assertLess(
            ordered.index(":web:generateClient"), ordered.index(":web:typecheck")
        )
        for consumer in (":web:webBuild", ":web:buildStorybook", ":web:webCheck"):
            self.assertLess(ordered.index(":web:typecheck"), ordered.index(consumer))

    def run_build(self, directory, environment, *args, fails_with=None):
        command = ["./gradlew", "--console=plain", *args]
        result = subprocess.run(
            command,
            cwd=directory,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=360,
            check=False,
        )
        if fails_with is None:
            self.assertEqual(result.returncode, 0, result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(fails_with, result.stdout)
        return result.stdout

    def verify_fault_controls(self, directory, environment):
        contract = directory / CONTRACT
        document = json.loads(contract.read_text(encoding="utf-8"))
        document["paths"]["/api/demo-roles"]["get"]["operationId"] = (
            "listChangedDemoRoles"
        )
        original = contract.read_bytes()
        try:
            contract.write_text(json.dumps(document), encoding="utf-8")
            failed = self.run_build(
                directory,
                environment,
                ":web:typecheck",
                fails_with="has no exported member 'listDemoRoles'",
            )
            outcomes = task_outcomes(failed)
            self.assertEqual(outcomes[":web:generateClient"], "EXECUTED")
            self.assertEqual(outcomes[":web:typecheck"], "FAILED")
        finally:
            contract.write_bytes(original)
        recovered = self.run_build(directory, environment, ":web:typecheck")
        self.assertEqual(task_outcomes(recovered)[":web:generateClient"], "EXECUTED")
        print(
            "Changing the operation invalidated the consumer. Restoring it regenerated and typechecked.",
            flush=True,
        )

        gradle = directory / "build.gradle.kts"
        original = gradle.read_text(encoding="utf-8")
        try:
            gradle.write_text(
                original
                + "\n"
                + 'tasks.named("check") { dependsOn(":probe:integrationTest") }\n',
                encoding="utf-8",
            )
            injected = self.run_build(
                directory, environment, "clean", "build", "--dry-run"
            )
            outcomes = task_outcomes(injected, dry_run=True)
            self.assertIn(":probe:integrationTest", outcomes)
            with self.assertRaisesRegex(
                AssertionError, "infrastructure or opt-in browser task"
            ):
                self.assert_build_graph(outcomes)
        finally:
            gradle.write_text(original, encoding="utf-8")
        print(
            "The real dry-run guard rejected an injected :probe:integrationTest edge.",
            flush=True,
        )

    def verify_outputs(self, directory):
        generated = directory / OUTPUTS[":web:generateClient"]
        self.assertIn(
            "export const listDemoRoles", (generated / "client.ts").read_text()
        )
        self.assertGreater(
            (generated / "schemas/demoRoleDirectory.zod.ts").stat().st_size, 0
        )
        web = directory / OUTPUTS[":web:webBuild"]
        assets = AssetLinks(web / "index.html").assets
        self.assertEqual({Path(asset).suffix for asset in assets}, {".js", ".css"})
        for asset in assets:
            self.assertTrue(asset.startswith("/assets/"), asset)
            self.assertGreater((web / asset.removeprefix("/")).stat().st_size, 0)
        self.assertTrue(
            list((web / "assets").glob("*.woff2")), "Expected bundled fonts"
        )
        storybook = directory / OUTPUTS[":web:buildStorybook"]
        entries = json.loads((storybook / "index.json").read_text())["entries"]
        self.assertTrue(any(entry["type"] == "story" for entry in entries.values()))
        self.assertGreater((storybook / "iframe.html").stat().st_size, 0)
        docs = directory / OUTPUTS[":docs-site:docsBuild"]
        expected = {
            "index.html": "Read quick start",
            "quick-start/index.html": "Start the shell",
            "feasibility/phase-01/index.html": "Phase 01 feasibility record",
            "maintainer-guide/index.html": "Maintainer guide",
            "site.css": ".scroll-region",
        }
        self.assertEqual(
            {str(path.relative_to(docs)) for path in docs.rglob("*") if path.is_file()},
            expected.keys(),
        )
        for name, marker in expected.items():
            self.assertIn(marker, (docs / name).read_text(encoding="utf-8"))
        report = Path("feasibility/phase-01.md")
        self.assertEqual(
            (directory / "docs-site/build/staged" / report).read_bytes(),
            (directory / "docs" / report).read_bytes(),
        )
        boot_jars = [
            path
            for path in (directory / "bff/build/libs").glob("*.jar")
            if not path.name.endswith("-plain.jar")
        ]
        self.assertEqual(len(boot_jars), 1)
        with ZipFile(boot_jars[0]) as archive:
            self.assertEqual(
                archive.read("BOOT-INF/classes/static/openapi.json"),
                (directory / CONTRACT).read_bytes(),
            )
        for task, reports in TEST_SUITES.items():
            suites = [
                ElementTree.parse(report).getroot().attrib
                for report in (directory / reports).glob("TEST-*.xml")
            ]
            count = sum(int(suite["tests"]) for suite in suites)
            self.assertGreater(count, 0, task)
            self.assertEqual(
                sum(
                    int(suite[field])
                    for suite in suites
                    for field in ("failures", "errors", "skipped")
                ),
                0,
                task,
            )
            print(f"{task}: {count} JVM tests; zero failures or skips", flush=True)
        print(
            f"Built {len(assets)} Vite entry assets, {len(entries)} Storybook entries and {len(expected)} docs files.",
            flush=True,
        )

    def verify_quick_start(self, directory, environment):
        guide = (directory / "docs/quick-start.md").read_text(encoding="utf-8")
        commands = [
            shlex.split(line)
            for line in re.findall(r"^   (\./gradlew .+)$", guide, flags=re.M)
        ]
        self.assertEqual(
            [command[:2] for command in commands],
            [
                ["./gradlew", ":bff:bootRun"],
                ["./gradlew", ":web:dev"],
                ["./gradlew", ":docs-site:serve"],
            ],
        )
        verify_available_ports()
        launch_env = {
            **environment,
            "GRADLE_OPTS": environment.get("GRADLE_OPTS", "")
            + " -Dorg.gradle.daemon=false",
        }
        bff = "http://127.0.0.1:8080/"
        web = "http://127.0.0.1:5173/"
        docs = "http://127.0.0.1:8081/"
        with launch(
            commands[0], directory, launch_env, bff + "openapi.json"
        ) as contract:
            self.assertEqual(contract, (directory / CONTRACT).read_bytes())
            with launch(commands[1], directory, launch_env, web) as app:
                self.assertIn(b'id="root"', app)
                self.assertEqual(
                    json.loads(fetch(web + "api/demo-roles")),
                    json.loads(fetch(bff + "api/demo-roles")),
                )
                with launch(commands[2], directory, launch_env, docs) as home:
                    self.assertIn(f'href="{web}">Open demo'.encode(), home)
                    self.assertIn(b"Start the shell", fetch(docs + "quick-start/"))
                    self.assertIn(
                        b"Phase 01 feasibility record",
                        fetch(docs + "feasibility/phase-01/"),
                    )
                    self.assertIn(
                        b"Maintainer guide", fetch(docs + "maintainer-guide/")
                    )

    def test_clean_build_regeneration_and_documented_quick_start(self):
        with tempfile.TemporaryDirectory(prefix="courses-phase2-build-") as scratch:
            directory = Path(scratch) / "candidate"
            copy_candidate(directory)
            browser_cache = Path(scratch) / "browsers"
            environment = {
                **os.environ,
                "DOCKER_HOST": "tcp://127.0.0.1:1",
                "PLAYWRIGHT_BROWSERS_PATH": str(browser_cache),
            }
            for name in ("DOCKER_CONTEXT", "VITE_BFF_ORIGIN", "VITE_DOCS_BASE"):
                environment.pop(name, None)
            lock_bytes = {path: (directory / path).read_bytes() for path in LOCKS}
            self.assertTrue(
                all(not (directory / path).exists() for path in OUTPUTS.values())
            )
            dry = self.run_build(
                directory,
                environment,
                "clean",
                "build",
                "--no-build-cache",
                "--dry-run",
            )
            self.assert_build_graph(task_outcomes(dry, dry_run=True))
            clean = self.run_build(
                directory, environment, "clean", "build", "--no-build-cache"
            )
            outcomes = task_outcomes(clean)
            self.assert_build_graph(outcomes)
            self.assertEqual({outcomes[task] for task in REQUIRED}, {"EXECUTED"})
            self.assertRegex(clean, r"(?m)^# tests [1-9]\d*$")
            self.verify_outputs(directory)
            outputs = {path: snapshot(directory / path) for path in OUTPUTS.values()}
            repeat = self.run_build(directory, environment, "build", "--no-build-cache")
            self.assert_build_graph(task_outcomes(repeat))
            for task in (*OUTPUTS, *TEST_SUITES, ":bff:bootJar"):
                self.assertEqual(task_outcomes(repeat)[task], "UP-TO-DATE", task)
            for path, expected in outputs.items():
                self.assertEqual(snapshot(directory / path), expected, path)
            shutil.rmtree(directory / OUTPUTS[":web:generateClient"])
            recovered = self.run_build(directory, environment, ":web:generateClient")
            self.assertEqual(
                task_outcomes(recovered)[":web:generateClient"], "EXECUTED"
            )
            output = OUTPUTS[":web:generateClient"]
            self.assertEqual(snapshot(directory / output), outputs[output])
            self.assertFalse(
                browser_cache.exists(), "The ordinary build provisioned Chromium"
            )
            self.verify_quick_start(directory, environment)
            self.verify_fault_controls(directory, environment)
            self.assertEqual(snapshot(directory / output), outputs[output])
            for path, expected in lock_bytes.items():
                self.assertEqual((directory / path).read_bytes(), expected, path)
            print(
                f"Verified five unchanged npm locks on {platform.system()} {platform.machine()}.",
                flush=True,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
