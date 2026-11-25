"""Report the toolchain readiness of this checkout."""

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


ROOT = Path(__file__).resolve().parent.parent
VERSION = r"\d+\.\d+\.\d+"
REQUIRED = "required"
ADDITIONAL = "additional"
PROBE_REPAIR = "Run ./gradlew -p probe/web npmSetup."
NPM_CONSUMERS = {
    "tools/style": ("tools/style", REQUIRED, "Run ./gradlew npmSetup."),
    "web": ("web", REQUIRED, "Run ./gradlew :web:npmSetup."),
    "docs-site": ("docs-site", REQUIRED, "Run ./gradlew :docs-site:npmSetup."),
    "probe/web": ("probe/web", ADDITIONAL, PROBE_REPAIR),
    "probe/typeid": ("probe/web", ADDITIONAL, PROBE_REPAIR),
}


@dataclass(frozen=True)
class Check:
    tier: str
    name: str
    owner: str
    declared: str
    observed: str
    status: str
    repair: str


def read_file(path, reader):
    try:
        return reader((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, ValueError, LookupError, TypeError):
        return None


def read_mapping(path, reader=json.loads):
    value = read_file(path, reader)
    return value if isinstance(value, dict) else {}


def read_toml(path):
    return read_mapping(path, tomllib.loads) if tomllib else {}


def command(*args, timeout=5, env=None):
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
            env=env,
        )
    except FileNotFoundError:
        return None, "missing"
    except subprocess.TimeoutExpired:
        return None, "timed out"
    except OSError:
        return None, "could not run"
    if result.returncode:
        return None, f"exit {result.returncode}"
    return (result.stdout + result.stderr).strip(), "unrecognized output"


def observation(args, pattern, *, env=None):
    output, unavailable = command(*args, env=env)
    match = re.search(pattern, output or "", re.MULTILINE)
    return match.group(1) if match else None, unavailable


def valid_value(value, pattern):
    return value if isinstance(value, str) and re.fullmatch(pattern, value) else None


def check(tier, name, owner, declared, observed, passed, repair):
    status = "DEFERRED" if passed is None else "PASS" if passed else "FAIL"
    return Check(
        tier, name, owner, declared or "invalid or missing", observed, status, repair
    )


def launcher():
    home = os.environ.get("JAVA_HOME")
    if home:
        legacy = Path(home) / "jre/sh/java"
        return str(legacy if os.access(legacy, os.X_OK) else Path(home) / "bin/java")
    return "java"


def jvm_check(name, executable, feature, *, deferred=False):
    repair = "Set JAVA_HOME to a Temurin JDK matching .java-version; register it for Gradle toolchain discovery."
    declared = f"Eclipse Temurin {feature}" if feature else None
    if deferred or not executable:
        return check(
            REQUIRED,
            name,
            ".java-version",
            declared,
            "requires running Gradle" if deferred else "toolchain unavailable",
            None if deferred else False,
            repair,
        )
    output, unavailable = command(executable, "-XshowSettings:properties", "-version")
    props = {
        key.strip(): value.strip()
        for key, sep, value in (
            line.partition("=") for line in (output or "").splitlines()
        )
        if sep
    }
    vendor = props.get("java.vendor")
    recognized = {
        "Eclipse Adoptium",
        "Amazon.com Inc.",
        "Azul Systems, Inc.",
        "Homebrew",
        "Oracle Corporation",
        "Microsoft",
    }
    release = valid_value(props.get("java.version"), r"\d+(?:\.\d+){0,3}(?:-ea)?")
    build = valid_value(
        props.get("java.runtime.version"), r"[\d.]+(?:-ea)?\+[\d]+(?:-LTS)?"
    )
    observed = unavailable
    if release and build:
        safe_vendor = vendor if vendor in recognized else "unrecognized vendor"
        observed = f"{safe_vendor} {release} ({build})"
    passed = (
        vendor == "Eclipse Adoptium"
        and bool(build)
        and bool(release)
        and release.split(".")[0] == feature
        and not release.endswith("-ea")
    )
    return check(REQUIRED, name, ".java-version", declared, observed, passed, repair)


def wrapper_checks(gradle, *, bootstrap):
    owner = "gradle/wrapper/gradle-wrapper.properties"
    wrapper = (
        read_file(
            owner,
            lambda raw: dict(
                line.replace(r"\:", ":").split("=", 1)
                for line in raw.splitlines()
                if line and not line.startswith("#")
            ),
        )
        or {}
    )
    url = wrapper.get("distributionUrl", "")
    match = re.fullmatch(
        rf"https://services\.gradle\.org/distributions/gradle-({VERSION})-bin\.zip", url
    )
    release = match.group(1) if match else None
    digest = valid_value(wrapper.get("distributionSha256Sum"), r"[0-9a-f]{64}")
    policy = (
        read_file("tools/style/policy.json", lambda raw: json.loads(raw)["wrapper"])
        or {}
    )
    validated = (
        bool(release and digest)
        and url == policy.get("distributionUrl")
        and digest == policy.get("distributionSha256Sum")
        and wrapper.get("validateDistributionUrl") == "true"
    )
    for path in ("gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar"):
        try:
            file = ROOT / path
            mode = "100755" if file.stat().st_mode & 0o100 else "100644"
            validated = (
                validated
                and mode == policy[path]["mode"]
                and hashlib.sha256(file.read_bytes()).hexdigest()
                == policy[path]["sha256"]
            )
        except (OSError, KeyError):
            validated = False
    repair = "Restore the checked-in wrapper files or verify a wrapper update and its publisher checksums."
    yield check(
        REQUIRED,
        "Gradle wrapper files",
        owner,
        f"{release} sha256={digest}" if release and digest else None,
        "local wrapper files and checksum policy agree"
        if validated
        else "invalid wrapper inputs",
        validated,
        repair,
    )
    yield check(
        REQUIRED,
        "Running Gradle",
        owner,
        release,
        gradle or ("requires running Gradle" if bootstrap else "unavailable"),
        None if bootstrap else bool(release and gradle == release),
        "Use ./gradlew; check wrapper distribution availability and GRADLE_USER_HOME permissions.",
    )


def npm_checks(data, *, bootstrap):
    node_owner = ".nvmrc"
    version = read_file(node_owner, lambda raw: valid_value(raw.strip(), VERSION))
    for directory, (npm_owner, tier, repair) in NPM_CONSUMERS.items():
        owner = f"{npm_owner}/package.json"
        lock_owner = f"{directory}/package-lock.json"
        manifest_owner = f"{directory}/package.json"
        package = read_mapping(manifest_owner)
        lock = read_mapping(lock_owner)
        packages = lock.get("packages")
        root_package = packages.get("") if isinstance(packages, dict) else None
        npm_version = read_file(
            owner,
            lambda raw: valid_value(
                json.loads(raw)["packageManager"], rf"npm@{VERSION}"
            ),
        )
        aligned = (
            bool(npm_version and package.get("name"))
            and lock.get("lockfileVersion") in (3, 4)
            and isinstance(root_package, dict)
            and all(
                package.get(field) == root_package.get(field)
                for field in ("name", "version", "dependencies", "devDependencies")
            )
        )
        yield check(
            tier,
            f"npm inputs ({directory})",
            f"{owner}, {lock_owner}",
            npm_version,
            f"lockfile v{lock['lockfileVersion']}"
            if aligned
            else "missing or manifest and lock disagree",
            aligned,
            "Restore the manifest and lockfile or regenerate the lock with the pinned npm.",
        )
        paths = data.get(directory, [])
        if bootstrap:
            observed = "requires running Gradle"
            yield check(
                tier,
                f"Managed Node ({directory})",
                node_owner,
                version,
                observed,
                None,
                repair,
            )
            yield check(
                tier,
                f"Managed npm ({directory})",
                owner,
                npm_version,
                observed,
                None,
                repair,
            )
            continue
        node, npm = paths if len(paths) == 2 else (None, None)
        node_version, node_status = (
            observation([node, "--version"], rf"^(v{VERSION})$")
            if node
            else (None, "unavailable")
        )
        npm_observed, npm_status = (
            observation(
                [node, npm, "--version"],
                rf"^({VERSION})$",
                env={
                    **os.environ,
                    "PATH": f"{Path(node).parent}{os.pathsep}{os.defpath}",
                },
            )
            if node and npm
            else (None, "unavailable")
        )
        yield check(
            tier,
            f"Managed Node ({directory})",
            node_owner,
            f"v{version}" if version else None,
            f"{node_version or node_status} ({node})" if node else node_status,
            bool(version and node_version == f"v{version}"),
            repair,
        )
        yield check(
            tier,
            f"Managed npm ({directory})",
            owner,
            npm_version,
            f"{npm_observed or npm_status} ({npm})" if npm else npm_status,
            bool(npm_version and f"npm@{npm_observed}" == npm_version),
            repair,
        )


def action_pins():
    owner = ".github/workflows/"
    files = sorted([*(ROOT / owner).glob("*.yml"), *(ROOT / owner).glob("*.yaml")])
    if not files:
        return check(
            REQUIRED,
            "GitHub Actions",
            owner,
            "full commit SHA",
            "workflow pending",
            None,
            "",
        )
    uses = [
        value
        for path in files
        for value in (
            read_file(
                path.relative_to(ROOT),
                lambda raw: re.findall(
                    r"^\s*(?:-\s+)?uses:\s*([^\s#]+)", raw, re.MULTILINE
                ),
            )
            or []
        )
        if not value.strip("\"'").startswith("./")
    ]
    pinned = [
        value.strip("\"'")
        for value in uses
        if re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", value.strip("\"'"))
    ]
    return check(
        REQUIRED,
        "GitHub Actions",
        owner,
        "full commit SHA",
        ", ".join(pinned)
        if len(pinned) == len(uses) and uses
        else "no usable pins or unpinned step",
        bool(uses and len(pinned) == len(uses)),
        "Verify the publisher's release commit and pin each external action to its full SHA.",
    )


def checks(gradle):
    bootstrap = gradle is None
    yield from wrapper_checks(
        None if bootstrap else gradle.get("gradle"), bootstrap=bootstrap
    )
    feature = read_file(
        ".java-version", lambda raw: valid_value(raw.strip(), r"[1-9]\d*")
    )
    yield jvm_check("Launcher JVM", launcher(), feature)
    yield jvm_check(
        "BFF worker JVM",
        None if bootstrap else gradle.get("worker"),
        feature,
        deferred=bootstrap,
    )
    catalog = read_toml("gradle/libs.versions.toml")
    sections = ("versions", "libraries", "plugins")
    present = all(catalog.get(section) for section in sections)
    yield check(
        REQUIRED,
        "Gradle catalog",
        "gradle/libs.versions.toml",
        ", ".join(sections),
        ", ".join(f"{len(catalog[name])} {name}" for name in sections)
        if present
        else "missing sections",
        present,
        "Restore the version catalog.",
    )
    host = f"{platform.system()}/{platform.machine()}"
    supported = host in {
        "Darwin/arm64",
        "Darwin/x86_64",
        "Linux/aarch64",
        "Linux/x86_64",
    }
    yield check(
        REQUIRED,
        "Host",
        "docs/maintainer-guide.md",
        "macOS or Linux, ARM64 or AMD64",
        host,
        supported,
        "Use a supported host.",
    )
    yield check(
        REQUIRED,
        "Python",
        "tools/style/run.py",
        "3.11+",
        platform.python_version(),
        sys.version_info >= (3, 11),
        "Install Python 3.11 or newer.",
    )
    git, unavailable = observation(
        ["git", "--version"], rf"^git version ({VERSION}(?:\.\d+)?)"
    )
    yield check(
        REQUIRED,
        "Git",
        ".githooks/pre-commit",
        "working Git",
        git or unavailable,
        bool(git),
        "Install Git and put it on PATH.",
    )
    shell, unavailable = command("sh", "-n", "gradlew")
    yield check(
        REQUIRED,
        "POSIX shell",
        "gradlew, tools/style/run.py",
        "working sh",
        "syntax check passed" if shell is not None else unavailable,
        shell is not None,
        "Install sh and put it on PATH.",
    )
    mise, unavailable = observation(["mise", "--version"], rf"^({VERSION})(?:\s|$)")
    yield check(
        REQUIRED,
        "mise",
        "mise.toml",
        "working mise",
        mise or unavailable,
        bool(mise),
        "Install mise and put it on PATH.",
    )
    pins = read_toml("mise.toml").get("tools", {})
    if not isinstance(pins, dict):
        pins = {}
    for tool, tier in (("ruff", REQUIRED), ("taplo", REQUIRED), ("pack", ADDITIONAL)):
        expected = valid_value(pins.get(tool), VERSION)
        found, unavailable = observation(
            [tool, "--version"], rf"^(?:{tool} )?v?({VERSION})(?:[+\s]|$)"
        )
        yield check(
            tier,
            tool.title(),
            "mise.toml",
            expected,
            found or unavailable,
            bool(expected and found == expected),
            f"Run mise install {tool}; expose it with mise exec or mise activate.",
        )
    yield from npm_checks(
        {} if bootstrap else gradle.get("npm", {}), bootstrap=bootstrap
    )
    yield action_pins()
    docker, unavailable = observation(
        [
            "docker",
            "info",
            "--format",
            "{{.ServerVersion}} {{.OSType}}/{{.Architecture}}",
        ],
        rf"^({VERSION}[^\s]* [a-z]+/[A-Za-z0-9_]+)$",
    )
    server_version, _, architecture = (docker or "").partition(" ")
    yield check(
        ADDITIONAL,
        "Docker daemon",
        "docs/maintainer-guide.md",
        "reachable Docker server",
        server_version or unavailable,
        bool(server_version),
        "Start Docker and verify the selected context or DOCKER_HOST.",
    )
    supported_arch = architecture in {
        "linux/arm64",
        "linux/aarch64",
        "linux/x86_64",
        "linux/amd64",
    }
    yield check(
        ADDITIONAL,
        "Docker architecture",
        "probe/README.md",
        "Linux ARM64 or AMD64",
        architecture or "daemon unavailable",
        supported_arch,
        "Check the daemon platform and select the platform required by the probe or image workflow.",
    )
    compose, unavailable = observation(
        ["docker", "compose", "version", "--short"],
        rf"^v?({VERSION})(?:[-+.]?[\w.-]+)?$",
    )
    yield check(
        ADDITIONAL,
        "Docker Compose",
        "docs/maintainer-guide.md",
        "Compose v2 or newer",
        compose or unavailable,
        bool(compose and int(compose.split(".")[0]) >= 2),
        "Install the Docker Compose plugin.",
    )


def report(gradle):
    results = list(checks(gradle))
    print("Toolchain doctor" + (" (bootstrap)" if gradle is None else ""))
    print("Tier | Status | Check | Owner | Declared | Observed | Repair")
    for row in results:
        repair = row.repair if row.status != "PASS" and row.repair else "-"
        print(
            f"{row.tier} | {row.status} | {row.name} | {row.owner} | {row.declared} | {row.observed} | {repair}"
        )
    required_failure = any(
        row.tier == REQUIRED and row.status == "FAIL" for row in results
    )
    optional_failure = any(
        row.tier == ADDITIONAL and row.status == "FAIL" for row in results
    )
    print(
        "Required checks: "
        + (
            "repair needed"
            if required_failure
            else "bootstrap ready; continue with ./gradlew doctor"
            if gradle is None
            else "ready"
        )
    )
    print(
        "Additional checks: "
        + ("repair needed for the affected workflows" if optional_failure else "ready")
    )
    return int(required_failure)


class DoctorTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.env = dict(os.environ, PATH=str(self.directory), HOME=str(self.directory))
        for name in (
            "JAVA_HOME",
            "JAVA_OPTS",
            "JAVA_TOOL_OPTIONS",
            "_JAVA_OPTIONS",
            "JDK_JAVA_OPTIONS",
        ):
            self.env.pop(name, None)
        self.env["DOCKER_HOST"] = "tcp://synthetic-secret-doctor.invalid:1"
        (self.directory / "sh").symlink_to("/bin/sh")
        self.tool("git", "git version 2.52.0")
        self.tool("mise", "2026.11.14 macos-arm64")
        self.tool("ruff", "ruff 0.17.4")
        self.tool("taplo", "taplo 0.10.0")
        self.java()
        self.node()
        self.tool("npm-cli.js", "12.2.3")
        self.managed = {
            "gradle": "9.9.2",
            "worker": str(self.directory / "java"),
            "npm": {
                directory: [
                    str(self.directory / "node"),
                    str(self.directory / "npm-cli.js"),
                ]
                for directory in (
                    "tools/style",
                    "web",
                    "docs-site",
                    "probe/web",
                    "probe/typeid",
                )
            },
        }

    def tool(self, name, output, *, status=0):
        path = self.directory / name
        path.write_text(
            f"#!/bin/sh\nprintf '%s\\n' '{output}'\nexit {status}\n", encoding="utf-8"
        )
        path.chmod(0o700)

    def java(self, vendor="Eclipse Adoptium", release="25.0.5.1"):
        self.tool(
            "java",
            f"java.vendor = {vendor}\njava.version = {release}\njava.runtime.version = {release}+2-LTS",
        )

    def node(self, release="v26.13.1"):
        path = self.directory / "node"
        path.write_text(
            f'#!/bin/sh\ncase "$1" in --version) printf "%s\\n" "{release}";; *) "$@";; esac\n',
            encoding="utf-8",
        )
        path.chmod(0o700)

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
        for vendor, release in (
            ("Other Vendor", "25.0.1"),
            ("Eclipse Adoptium", "24.0.1"),
        ):
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
        (path_only / "node").write_text(
            "#!/bin/sh\nprintf 'v0.0.1\\n'\n", encoding="utf-8"
        )
        (path_only / "node").chmod(0o700)
        self.env["PATH"] = f"{path_only}{os.pathsep}{self.directory}"
        result = self.report()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"v26.13.1 ({self.directory / 'node'})", result.stdout)
        self.assertIn(f"12.2.3 ({self.directory / 'npm-cli.js'})", result.stdout)
        self.assertNotIn("v0.0.1", result.stdout)
        self.node("v0.0.2")
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


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        unittest.main(
            argv=[sys.argv[0], *[arg for arg in sys.argv[1:] if arg != "--self-test"]]
        )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gradle-input", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    raise SystemExit(report(json.load(sys.stdin) if arguments.gradle_input else None))
