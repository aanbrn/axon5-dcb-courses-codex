"""Exercise the generated client build in a disposable copy of the sources."""

import argparse
import hashlib
import json
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
DOCS_SETTING = "VITE_DOCS_BASE"
DOCS_DIAGNOSTIC = (
    "VITE_DOCS_BASE must be an absolute HTTP(S) documentation directory URL."
)
TASK_LINE = re.compile(r"^> Task (:[\w:.-]+)(?: ([A-Z-]+))?$", re.MULTILINE)
GENERATION_TASKS = {":web:nodeSetup", ":web:npmSetup", ":web:npmInstall", GENERATE}
INFRASTRUCTURE_TASKS = re.compile(
    r"bootRun|docker|browser|playwright|tracer|shellSmoke|integrationTest|imageProbe|bootBuildImage",
    re.IGNORECASE,
)
EXCLUDED_FILES = shutil.ignore_patterns(
    ".git",
    ".codex",
    ".gsd",
    ".planning",
    ".idea",
    ".aws",
    ".secrets",
    ".gradle",
    ".kotlin",
    ".ruff_cache",
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
)


def exclude_local_files(directory, names):
    return EXCLUDED_FILES(directory, names) | {
        name for name in names if (Path(directory) / name).is_symlink()
    }


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Candidate:
    def __init__(self, directory):
        self.project = directory / "source"
        shutil.copytree(
            ROOT,
            self.project,
            ignore=exclude_local_files,
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
        self.environment.pop(DOCS_SETTING, None)
        # Only public npm data is reusable. npm can write into its private copy.
        if cache_path := os.environ.get("npm_config_cache"):
            npm_cache = Path(cache_path) / "_cacache"
            if npm_cache.is_dir():
                shutil.copytree(npm_cache, directory / "npm-cache" / "_cacache")

    def gradle(
        self,
        label,
        *tasks,
        fails_with=(),
        excludes=(),
        generation_only=False,
        build_cache=False,
    ):
        command = [
            "./gradlew",
            "--console=plain",
            "--build-cache" if build_cache else "--no-build-cache",
            "--no-configuration-cache",
            *tasks,
        ]
        print(f"\n{label}\n{' '.join(command)}", flush=True)
        process = subprocess.run(
            command,
            cwd=self.project,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=360,
            check=False,
        )
        self.report(process.stdout, excludes)
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

    def frontend_assets(self, docs_base=None):
        distribution = self.project / "web/build/dist"
        html = (distribution / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(r'<script\b[^>]*\bsrc="(/assets/[^"/]+\.js)"', html)
        require(bool(scripts), "Vite index.html has no production script")
        entries = []
        for script in scripts:
            entry = distribution / script.lstrip("/")
            require(
                entry.stat().st_size > 0,
                f"Empty Vite asset {script}",
            )
            entries.append(entry)
        if docs_base is not None:
            literal = re.compile(rf"([`\"']){re.escape(docs_base)}\1")
            require(
                any(
                    literal.search(entry.read_text(encoding="utf-8"))
                    for entry in entries
                ),
                f"The Vite entry does not contain the normalized URL {docs_base}",
            )

    def reject_dev_startup(self, sentinel):
        web = self.project / "web"
        node_version = (self.project / ".nvmrc").read_text(encoding="utf-8").strip()
        executable = "node.exe" if os.name == "nt" else "bin/node"
        (node,) = (web / ".gradle/nodejs").glob(f"node-v{node_version}-*/{executable}")
        print(
            "\nReject invalid documentation base during development startup", flush=True
        )
        process = subprocess.run(
            [node, "node_modules/vite/bin/vite.js", "dev"],
            cwd=web,
            env=self.environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
            check=False,
        )
        self.report(process.stdout, (sentinel,))
        require(
            process.returncode != 0 and DOCS_DIAGNOSTIC in process.stdout,
            "Vite dev did not reject the invalid documentation base",
        )

    @staticmethod
    def report(output, excludes):
        require(
            not any(fragment in output for fragment in excludes),
            "The command disclosed the configured documentation base",
        )
        print(output, end="", flush=True)


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
        ":web:webCheck",
    ):
        require(outcomes.get(task) == "EXECUTED", f"Root build did not execute {task}")
    candidate.generated_files()
    candidate.frontend_assets("http://127.0.0.1:8081/")
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
    source = web_build.read_text(encoding="utf-8")
    disconnected, removed = re.subn(
        r'(tasks\.register<NodeTask>\("typecheck"\) \{\n)[ \t]*dependsOn\(generateClient\)\n',
        r"\1",
        source,
    )
    require(removed == 1, "Could not locate the typecheck generation dependency")
    shutil.rmtree(candidate.project / "web/build")
    web_build.write_text(disconnected, encoding="utf-8")
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


def verify_invalidation(candidate):
    outcomes = candidate.gradle(
        "Generate from the contract", GENERATE, generation_only=True
    )
    require(outcomes.get(GENERATE) == "EXECUTED", "Initial generation did not execute")
    original_files = candidate.generated_files()

    outcomes = candidate.gradle("Build with the unchanged contract", BUNDLE)
    require(
        outcomes.get(GENERATE) == "UP-TO-DATE",
        "Unchanged generation was not up-to-date",
    )
    require(
        candidate.generated_files() == original_files,
        "Unchanged generation changed the client bytes",
    )
    candidate.frontend_assets("http://127.0.0.1:8081/")

    shutil.rmtree(candidate.project / GENERATED)
    outcomes = candidate.gradle(
        "Regenerate a deleted output", GENERATE, generation_only=True
    )
    require(outcomes.get(GENERATE) == "EXECUTED", "Deleted generation did not execute")
    require(
        candidate.generated_files() == original_files,
        "Regeneration changed the client bytes",
    )
    candidate.frontend_assets()

    contract = candidate.project / CONTRACT
    original_contract = contract.read_bytes()
    document = json.loads(original_contract)
    operation = document["paths"]["/api/demo-roles"]["get"]
    require(
        operation["operationId"] == "listDemoRoles",
        "The fixture operation was unexpectedly renamed",
    )
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    original_reference = schema["$ref"]
    external_reference = "http://127.0.0.1:1/external.json#/DemoRoleDirectory"
    schema["$ref"] = external_reference
    contract.write_text(json.dumps(document), encoding="utf-8")
    candidate.gradle(
        "Reject an external reference",
        GENERATE,
        generation_only=True,
        fails_with=(
            f"{GENERATE} FAILED",
            "External $ref targets are not allowed",
            external_reference,
        ),
    )

    schema["$ref"] = original_reference
    operation["operationId"] = "listRenamedDemoRoles"
    contract.write_text(json.dumps(document), encoding="utf-8")
    outcomes = candidate.gradle(
        "Rename the contract operation",
        BUNDLE,
        fails_with=(f"{TYPECHECK} FAILED", "has no exported member 'listDemoRoles'"),
    )
    require(
        outcomes.get(GENERATE) == "EXECUTED",
        "Changed contract did not regenerate the client",
    )
    require(BUNDLE not in outcomes, "Bundling ran after the consumer failed typecheck")
    renamed_client = candidate.generated_files()["client.ts"]
    require(
        renamed_client != original_files["client.ts"]
        and b"export const listRenamedDemoRoles" in renamed_client,
        "The generated client did not change to the new operation",
    )

    contract.write_bytes(original_contract)
    shutil.rmtree(candidate.project / "web/build/dist")
    outcomes = candidate.gradle("Restore the contract and bundle", BUNDLE)
    require_build_order(outcomes)
    require(
        candidate.generated_files() == original_files,
        "Restored contract changed the client bytes",
    )
    candidate.frontend_assets()


def verify_docs_base(candidate):
    distribution = candidate.project / "web/build/dist"
    outcomes = candidate.gradle("Repeat the default production build", BUNDLE)
    require(
        outcomes.get(BUNDLE) == "UP-TO-DATE",
        f"The repeated default bundle reported {outcomes.get(BUNDLE)}",
    )
    candidate.frontend_assets("http://127.0.0.1:8081/")

    # An explicitly empty override must invalidate the existing default bundle.
    candidate.environment[DOCS_SETTING] = ""
    candidate.gradle(
        "Reject an explicitly empty documentation base",
        BUNDLE,
        fails_with=(f"{BUNDLE} FAILED", DOCS_DIAGNOSTIC),
    )

    sentinel = "invalid-port-sentinel"
    invalid_base = f"https://docs.example.test:{sentinel}/courses/"
    shutil.rmtree(distribution, ignore_errors=True)
    candidate.environment[DOCS_SETTING] = invalid_base
    candidate.gradle(
        "Reject a malformed documentation base from the process environment",
        BUNDLE,
        fails_with=(f"{BUNDLE} FAILED", DOCS_DIAGNOSTIC),
        excludes=(sentinel,),
    )
    require(
        not any(distribution.glob("*")), "An invalid documentation base produced output"
    )
    candidate.reject_dev_startup(sentinel)

    candidate.environment.pop(DOCS_SETTING)
    production_env = candidate.project / "web/.env.production"
    production_env.write_text(f"{DOCS_SETTING}={invalid_base}\n", encoding="utf-8")
    candidate.gradle(
        "Reject a malformed documentation base from the production env file",
        BUNDLE,
        fails_with=(f"{BUNDLE} FAILED", DOCS_DIAGNOSTIC),
        excludes=(sentinel,),
    )
    require(
        not any(distribution.glob("*")),
        "An invalid production env file produced output",
    )

    docs_base = "https://docs.example.test/courses"
    candidate.environment[DOCS_SETTING] = docs_base
    candidate.gradle(
        "Override the production env file in the process environment", BUNDLE
    )
    candidate.frontend_assets(f"{docs_base}/")

    candidate.environment.pop(DOCS_SETTING)
    production_env.write_text(
        f"{DOCS_SETTING}=https://docs.example.test:${{DOCS_PORT}}/${{DOCS_PREFIX}}/\n",
        encoding="utf-8",
    )
    candidate.environment.update(DOCS_PORT="443", DOCS_PREFIX="first")
    outcomes = candidate.gradle(
        "Build with expanded production dotenv values", BUNDLE, build_cache=True
    )
    require(outcomes.get(BUNDLE) == "EXECUTED", "The initial bundle did not execute")
    candidate.frontend_assets("https://docs.example.test/first/")

    candidate.environment["DOCS_PREFIX"] = "second"
    outcomes = candidate.gradle(
        "Change only the inherited documentation path", BUNDLE, build_cache=True
    )
    require(
        outcomes.get(BUNDLE) == "EXECUTED",
        f"The bundle reported {outcomes.get(BUNDLE)} after the inherited path changed",
    )
    candidate.frontend_assets("https://docs.example.test/second/")

    expanded_port_sentinel = "expanded-port-private-sentinel"
    candidate.environment["DOCS_PORT"] = expanded_port_sentinel
    candidate.gradle(
        "Reject a change to only the inherited documentation port",
        BUNDLE,
        fails_with=(f"{BUNDLE} FAILED", DOCS_DIAGNOSTIC),
        excludes=(expanded_port_sentinel,),
        build_cache=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--clean", action="store_true", help="verify a clean root build")
    mode.add_argument(
        "--invalidation",
        action="store_true",
        help="verify client invalidation and recovery",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="courses-client-graph-") as scratch:
        candidate = Candidate(Path(scratch))
        if args.clean:
            verify_clean(candidate)
        else:
            verify_invalidation(candidate)
            verify_docs_base(candidate)
        print(
            f"Verified unchanged web lock SHA-256 {hashlib.sha256(candidate.lock_bytes).hexdigest()}"
        )


if __name__ == "__main__":
    main()
