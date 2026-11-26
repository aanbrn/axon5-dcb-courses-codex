"""Verify the read-only pull request build policy and exercise failing controls."""

import argparse
import json
import platform
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/build.yml"
CHECKOUT = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
WRAPPER = "gradle/actions/wrapper-validation@8da46b539cd8fe6ab27ca75128919a18d757604c"
SETUP_JAVA = "actions/setup-java@d1374f8ac74474200d16ef8ecee22c7ae7a51880"
SETUP_MISE = "jdx/mise-action@924e7c586e33d7d4bae9c14e26c5d22e2beb6e78"
MISE_TOOLS = ("python", "aqua:rhysd/actionlint", "shellcheck", "ruff", "taplo")
WORKFLOW_LINT = (
    "mise exec aqua:rhysd/actionlint shellcheck -- "
    "actionlint -shellcheck=shellcheck -pyflakes="
)
STEPS = [
    {"uses": CHECKOUT, "with": {"persist-credentials": False}},
    {"uses": WRAPPER},
    {
        "uses": SETUP_JAVA,
        "with": {"distribution": "temurin", "java-version-file": ".java-version"},
    },
    {
        "uses": SETUP_MISE,
        "with": {
            "version": "2026.11.14",
            "install_args": " ".join(MISE_TOOLS),
            "cache": False,
        },
    },
    {
        "run": (
            "uname -sm\n"
            "java -version\n"
            "./gradlew --console=plain --version\n"
            "mise --version\n"
            "mise exec python -- python3 --version\n"
            "mise exec aqua:rhysd/actionlint shellcheck -- actionlint --version\n"
            "mise exec aqua:rhysd/actionlint shellcheck -- shellcheck --version\n"
            "mise exec ruff taplo -- ruff --version\n"
            "mise exec ruff taplo -- taplo --version\n"
        )
    },
    {"run": WORKFLOW_LINT},
    {"run": "mise exec python ruff taplo -- ./gradlew --console=plain styleCheck"},
    {"run": "./gradlew --console=plain clean build --no-build-cache"},
]
PARSE_YAML = """
const { readFileSync } = require("node:fs");
const { parseDocument } = require(process.argv[1]);
const document = parseDocument(readFileSync(0, "utf8"), { version: "1.2" });
const diagnostics = [...document.errors, ...document.warnings];
if (diagnostics.length) throw new Error(diagnostics.map(({ message }) => message).join("; "));
process.stdout.write(JSON.stringify(document.toJS({ maxAliasCount: 0 })));
"""


class WorkflowError(RuntimeError):
    pass


def expect(condition, message):
    if not condition:
        raise WorkflowError(message)


def read_workflow(path):
    system = {"Darwin": "darwin", "Linux": "linux"}.get(platform.system())
    arch = {
        "x86_64": "x64",
        "amd64": "x64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }.get(platform.machine().lower())
    node_release = (ROOT / ".nvmrc").read_text(encoding="utf-8").strip()
    node = ROOT / f"web/.gradle/nodejs/node-v{node_release}-{system}-{arch}/bin/node"
    parser = ROOT / "web/node_modules/yaml"
    expect(
        node.is_file() and (parser / "package.json").is_file(),
        "Run ./gradlew --console=plain :web:npmInstall to provision the locked YAML parser.",
    )
    result = subprocess.run(
        [node, "-e", PARSE_YAML, parser],
        input=path.read_text(encoding="utf-8"),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    expect(
        result.returncode == 0,
        f"{path.name} is not an accepted YAML document\n{result.stderr}",
    )
    return json.loads(result.stdout)


def check_workflow(path):
    workflow = read_workflow(path)
    expect(
        isinstance(workflow, dict)
        and set(workflow) == {"name", "on", "permissions", "jobs"},
        "Expected only name, on, permissions and jobs at workflow level.",
    )
    expect(workflow["name"] == "Build and style", "Unexpected workflow name.")
    expect(workflow["on"] == {"pull_request": None}, "Use only the pull_request event.")
    expect(
        workflow["permissions"] == {"contents": "read"}, "Grant only contents: read."
    )
    jobs = workflow["jobs"]
    expect(
        isinstance(jobs, dict) and set(jobs) == {"build-and-style"},
        "Expected one build-and-style job.",
    )
    job = jobs["build-and-style"]
    expect(
        isinstance(job, dict)
        and set(job) == {"runs-on", "timeout-minutes", "env", "steps"},
        "Use only the reviewed build job fields.",
    )
    expect(
        job["runs-on"] == "ubuntu-24.04" and job["timeout-minutes"] == 15,
        "Use the reviewed runner and time limit.",
    )
    expect(
        job["env"]
        == {
            "DOCKER_HOST": "tcp://127.0.0.1:1",
            "MISE_ENABLE_TOOLS": ",".join(MISE_TOOLS),
        },
        "Keep only the unreachable Docker endpoint and regular style tools in the job environment.",
    )
    steps = job["steps"]
    expect(
        isinstance(steps, list) and len(steps) == len(STEPS),
        "Use only the reviewed steps.",
    )
    for number, (actual, expected) in enumerate(
        zip(steps, STEPS, strict=True), start=1
    ):
        expect(isinstance(actual, dict), f"Step {number} must be a mapping.")
        name = actual.get("name")
        expect(
            isinstance(name, str) and name and "${{" not in name,
            f"Step {number} needs a literal name.",
        )
        expected_step = {**expected, "name": name}
        expect(
            json.dumps(actual, sort_keys=True)
            == json.dumps(expected_step, sort_keys=True),
            f"Step {number} must use the reviewed action, options or command in its assigned order.",
        )


def verify_controls(workflow):
    text = workflow.read_text(encoding="utf-8")
    controls = [
        ("contents: read", "contents: write", "Grant only contents: read."),
        (CHECKOUT, "actions/checkout@v7.0.1", "Step 1 must use the reviewed action"),
        (
            WORKFLOW_LINT,
            "mise exec aqua:rhysd/actionlint -- actionlint -shellcheck= -pyflakes=",
            "Step 6 must use the reviewed action",
        ),
    ]
    with tempfile.TemporaryDirectory(prefix="courses-pr-workflow-") as directory:
        fixture = Path(directory) / "build.yml"
        for original, mutation, reason in controls:
            expect(
                text.count(original) == 1, f"Missing unique control input {original!r}."
            )
            fixture.write_text(text.replace(original, mutation), encoding="utf-8")
            try:
                check_workflow(fixture)
            except WorkflowError as error:
                expect(reason in str(error), f"Unexpected control failure: {error}")
                print(f"Rejected {mutation!r}: {error}")
            else:
                raise WorkflowError(f"Accepted the unsafe fixture {mutation!r}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "workflow",
        type=Path,
        nargs="?",
        help="check a specific YAML file without creating controls",
    )
    args = parser.parse_args()
    try:
        check_workflow(args.workflow or WORKFLOW)
        if args.workflow is None:
            verify_controls(WORKFLOW)
    except (OSError, ValueError, WorkflowError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"{error}\n")
    print("Verified read-only pull request workflow and pinned build steps.")


if __name__ == "__main__":
    main()
