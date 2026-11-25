"""Report the toolchain readiness of this checkout."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


class DoctorTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.env = dict(os.environ, PATH=str(self.directory), HOME=str(self.directory))
        for name in ("JAVA_HOME", "JAVA_OPTS", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS"):
            self.env.pop(name, None)
        self.env["DOCKER_HOST"] = "tcp://synthetic-secret-doctor.invalid:1"
        self.tool("git", "git version 2.52.0")
        self.tool("mise", "2026.11.14 macos-arm64")
        self.tool("ruff", "ruff 0.17.4")
        self.tool("taplo", "taplo 0.10.0")
        self.java()
        self.tool("node", "v26.13.1")
        self.tool("npm-cli.js", "12.2.3")
        self.managed = {
            "gradle": "9.9.2",
            "worker": str(self.directory / "java"),
            "npm": {
                directory: [str(self.directory / "node"), str(self.directory / "npm-cli.js")]
                for directory in ("tools/style", "web", "docs-site", "probe/web", "probe/typeid")
            },
        }

    def tool(self, name, output, *, status=0):
        path = self.directory / name
        path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{output}'\nexit {status}\n", encoding="utf-8")
        path.chmod(0o700)

    def java(self, vendor="Eclipse Adoptium", release="25.0.5.1"):
        self.tool(
            "java",
            f"java.vendor = {vendor}\njava.version = {release}\njava.runtime.version = {release}+2-LTS",
        )

    def report(self, *, bootstrap=False):
        command = [sys.executable, __file__]
        if not bootstrap:
            command.append("--gradle-input")
        return subprocess.run(
            command,
            input=None if bootstrap else json.dumps(self.managed),
            env=self.env,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

    def test_missing_required_tool_exits_nonzero_with_repair(self):
        (self.directory / "git").unlink()
        result = self.report()
        self.assertEqual(result.returncode, 1)
        self.assertIn("required | FAIL | Git", result.stdout)
        self.assertIn("Install Git", result.stdout)
        self.assertIn("additional | FAIL | Pack", result.stdout)

    def test_optional_failures_leave_regular_build_ready(self):
        self.tool("docker", "synthetic-secret-doctor", status=1)
        result = self.report()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Required checks: ready", result.stdout)
        self.assertIn("additional | FAIL | Docker daemon", result.stdout)
        self.assertIn("additional | FAIL | Docker Compose", result.stdout)
        self.assertIn("additional | FAIL | Pack", result.stdout)
        self.assertNotIn("synthetic-secret-doctor", result.stdout + result.stderr)

    def test_wrong_java_vendor_or_feature_fails_in_both_modes(self):
        for vendor, release in (("Other Vendor", "25.0.1"), ("Eclipse Adoptium", "24.0.1")):
            with self.subTest(vendor=vendor, release=release):
                self.java(vendor, release)
                for bootstrap in (True, False):
                    result = self.report(bootstrap=bootstrap)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("required | FAIL | Launcher JVM", result.stdout)
                    self.assertIn("Set JAVA_HOME", result.stdout)
                    if not bootstrap:
                        self.assertIn("required | FAIL | BFF worker JVM", result.stdout)

    def test_managed_versions_and_executables_are_observed(self):
        path_only = self.directory / "path-only"
        path_only.mkdir()
        (path_only / "node").write_text("#!/bin/sh\nprintf 'v0.0.1\\n'\n", encoding="utf-8")
        (path_only / "node").chmod(0o700)
        self.env["PATH"] = f"{path_only}{os.pathsep}{self.directory}"
        result = self.report()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"v26.13.1 ({self.directory / 'node'})", result.stdout)
        self.assertIn(f"12.2.3 ({self.directory / 'npm-cli.js'})", result.stdout)
        self.assertNotIn("v0.0.1", result.stdout)
        self.tool("node", "v0.0.2")
        result = self.report()
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"v0.0.2 ({self.directory / 'node'})", result.stdout)
        self.assertIn("required | FAIL | Managed Node", result.stdout)

    def test_bootstrap_reports_required_checks_without_starting_gradle(self):
        result = self.report(bootstrap=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("required | DEFERRED | Running Gradle", result.stdout)
        self.assertIn("required | DEFERRED | BFF worker JVM", result.stdout)
        self.assertIn("required | DEFERRED | Managed Node", result.stdout)


if __name__ == "__main__" and "--self-test" in sys.argv:
    unittest.main(argv=[sys.argv[0], *[arg for arg in sys.argv[1:] if arg != "--self-test"]])
