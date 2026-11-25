"""Exercise the generated client build in a disposable copy of the sources."""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("bff/src/main/resources/static/openapi.json")
LOCK = Path("web/package-lock.json")
GENERATED = Path("web/build/generated")
GENERATE = ":web:generateClient"
TYPECHECK = ":web:typecheck"
BUNDLE = ":web:webBuild"
TASK_LINE = re.compile(r"^> Task (:[\w:.-]+)(?: ([A-Z-]+))?$", re.MULTILINE)
GENERATION_TASKS = {":web:nodeSetup", ":web:npmSetup", ":web:npmInstall", GENERATE}
INFRASTRUCTURE_TASKS = re.compile(
    r"bootRun|docker|browser|playwright|tracer|shellSmoke|integrationTest|imageProbe|bootBuildImage",
    re.IGNORECASE,
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Candidate:
    def __init__(self, directory):
        self.project = directory / "source"
        shutil.copytree(
            ROOT,
            self.project,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git",
                ".codex",
                ".gsd",
                ".planning",
                ".idea",
                ".aws",
                ".secrets",
                ".gradle",
                ".kotlin",
                ".venv",
                ".env",
                ".env.*",
                "build",
                "dist",
                "out",
                "node_modules",
                ".vite",
                "coverage",
                "storybook-static",
                "playwright-report",
                "test-results",
                "__pycache__",
                ".DS_Store",
            ),
        )
        self.lock_bytes = (ROOT / LOCK).read_bytes()
        self.browser_cache = directory / "browsers"
        self.environment = {
            **os.environ,
            "DOCKER_HOST": "tcp://127.0.0.1:1",
            "PLAYWRIGHT_BROWSERS_PATH": str(self.browser_cache),
            "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
            "npm_config_cache": str(directory / "npm-cache"),
        }
        self.environment.pop("DOCKER_CONTEXT", None)
        # Only public npm data is reusable. npm can write into its private copy.
        npm_cache = (
            Path(os.environ.get("npm_config_cache", Path.home() / ".npm")) / "_cacache"
        )
        if "npm_config_cache" in os.environ and npm_cache.is_dir():
            shutil.copytree(npm_cache, directory / "npm-cache" / "_cacache")

    def gradle(self, label, *tasks, fails_with=(), generation_only=False):
        print(f"\n{label}\n./gradlew {' '.join(tasks)}", flush=True)
        process = subprocess.run(
            [
                str(self.project / "gradlew"),
                "--console=plain",
                "--no-build-cache",
                "--no-configuration-cache",
                *tasks,
            ],
            cwd=self.project,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=360,
            check=False,
        )
        print(process.stdout, end="", flush=True)
        require(
            (self.project / LOCK).read_bytes() == self.lock_bytes,
            "npm changed the lockfile bytes",
        )
        require(not self.browser_cache.exists(), "The build provisioned a browser")
        require(
            "loaded multiple times in different subprojects" not in process.stdout,
            "Kotlin plugins were loaded separately in the subprojects",
        )
        outcomes = {
            task: outcome or "EXECUTED"
            for task, outcome in TASK_LINE.findall(process.stdout)
        }
        require(
            not any(INFRASTRUCTURE_TASKS.search(task) for task in outcomes),
            f"Application build included infrastructure tasks: {list(outcomes)}",
        )
        if generation_only:
            require(
                {task for task in outcomes if not task.startswith(":build-logic:")}
                == GENERATION_TASKS,
                f"Generation included unexpected tasks: {list(outcomes)}",
            )
        if fails_with:
            require(
                process.returncode != 0
                and all(fragment in process.stdout for fragment in fails_with),
                f"{label} did not fail with {fails_with!r}",
            )
        else:
            require(
                process.returncode == 0,
                f"{label} failed with exit code {process.returncode}",
            )
        return outcomes

    def generated_files(self):
        output = self.project / GENERATED
        files = {
            "client.ts",
            "schemas/index.ts",
            "schemas/administratorRole.zod.ts",
            "schemas/demoRoleDirectory.zod.ts",
            "schemas/studentRole.zod.ts",
        }
        for name in files:
            require(
                (output / name).is_file() and (output / name).stat().st_size > 0,
                f"Missing generated file {name}",
            )
        return {name: (output / name).read_bytes() for name in files}

    def frontend_assets(self):
        distribution = self.project / "web/build/dist"
        html = (distribution / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(r'<script\b[^>]*\bsrc="(/assets/[^"/]+\.js)"', html)
        require(bool(scripts), "Vite index.html has no production script")
        for script in scripts:
            require(
                (distribution / script.lstrip("/")).stat().st_size > 0,
                f"Empty Vite asset {script}",
            )


def require_build_order(outcomes):
    tasks = list(outcomes)
    require(
        all(outcomes.get(task) == "EXECUTED" for task in (GENERATE, TYPECHECK, BUNDLE)),
        f"Expected executed generation, native typecheck and bundle: {outcomes}",
    )
    require(
        tasks.index(GENERATE) < tasks.index(TYPECHECK) < tasks.index(BUNDLE),
        "Gradle did not generate and typecheck before bundling",
    )


def verify_clean(candidate):
    require(
        not (candidate.project / GENERATED).exists(),
        "The candidate has prebuilt client files",
    )
    outcomes = candidate.gradle("Clean root build", ":clean", ":build")
    require_build_order(outcomes)
    for task in (
        ":bff:bootJar",
        ":bff:test",
        ":bff:componentTest",
        ":bff:verifyFixtureIsolation",
    ):
        require(outcomes.get(task) == "EXECUTED", f"Root build did not execute {task}")
    candidate.generated_files()
    candidate.frontend_assets()
    jars = list((candidate.project / "bff/build/libs").glob("*.jar"))
    boot_jar = next((jar for jar in jars if not jar.name.endswith("-plain.jar")), None)
    require(boot_jar is not None, "No executable BFF JAR was assembled")
    with ZipFile(boot_jar) as packaged:
        require(
            packaged.read("BOOT-INF/classes/static/openapi.json")
            == (candidate.project / CONTRACT).read_bytes(),
            "BFF JAR did not package the exact contract",
        )

    shutil.rmtree(candidate.project / GENERATED)
    outcome = candidate.gradle("Generation alone", GENERATE, generation_only=True)
    require(
        outcome.get(GENERATE) == "EXECUTED",
        "Generation did not run from an empty output",
    )
    candidate.generated_files()

    web_build = candidate.project / "web/build.gradle.kts"
    dependency = "    dependsOn(generateClient)\n"
    source = web_build.read_text(encoding="utf-8")
    start = source.index('val typecheck = tasks.register<NodeTask>("typecheck")')
    require(
        source.index(dependency, start) == source.index("\n", start) + 1,
        "Could not locate the typecheck generation dependency",
    )
    shutil.rmtree(candidate.project / "web/build")
    web_build.write_text(
        source[:start] + source[start:].replace(dependency, "", 1), encoding="utf-8"
    )
    candidate.gradle(
        "Disconnected generation",
        TYPECHECK,
        fails_with=(
            f"{TYPECHECK} FAILED",
            "Cannot find module",
            "build/generated/client",
        ),
    )
    require(
        not (candidate.project / GENERATED).exists(),
        "Disconnected typecheck still generated the client",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean", action="store_true", required=True, help="verify a clean root build"
    )
    parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="courses-client-graph-") as scratch:
        candidate = Candidate(Path(scratch))
        verify_clean(candidate)
        print(
            f"Verified unchanged web lock SHA-256 {hashlib.sha256(candidate.lock_bytes).hexdigest()}"
        )


if __name__ == "__main__":
    main()
