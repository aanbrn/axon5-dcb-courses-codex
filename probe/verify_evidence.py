"""Capture a fresh native Phase 01 acceptance run or verify its published record."""

import argparse
from datetime import datetime
import errno
import fcntl
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
import verify_secondary as secondary
from verify_secondary import (
    CORE_COMMAND,
    GRADLE,
    GROUPS,
    ROOT,
    STAGES,
    Store,
    file_sha,
    inside,
    instant,
    payload_sha,
    read_json,
    require,
    utc_now,
    write_json,
)


DEFAULT_EVIDENCE = Path(secondary.DEFAULT_DIR)
GUIDE = Path("probe/README.md")
REPORT = Path("docs/feasibility/phase-01.md")
MANIFEST = "manifest.json"
POINTER = "current-acceptance.json"
OFFLINE_DOCKER = "tcp://127.0.0.1:1"
REGISTRY = "https://registry-1.docker.io/v2/axoniq/axonserver"
REGISTRY_AUTH = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:axoniq/axonserver:pull"
OCI = "application/vnd.oci.image."
BUILD_COMMAND = (*GRADLE, "build", "--no-build-cache", "--rerun-tasks", "--info")
DRY_RUN = (*GRADLE, "build", "--dry-run")
OPT_IN_DRY_RUN = (
    *GRADLE,
    ":probe:integrationTest",
    ":probe:frontendImageProbe",
    "--dry-run",
)
SMOKE_REPORT = Path("probe/build/test-results/test/TEST-probe.ProbeContractsTest.xml")
RUNTIME_GRAPHS = (
    "runtimeClasspath",
    "testRuntimeClasspath",
    "integrationTestRuntimeClasspath",
)
CONTROL_GRAPHS = (
    "compileClasspath",
    "testCompileClasspath",
    "integrationTestCompileClasspath",
    "kotestProbeRuntimeClasspath",
    "typeIdJvmVectorsRuntimeClasspath",
    "kdocFormatter",
)
REPORT_SECTIONS = (
    "Reproduce the proof",
    "Selected versions",
    "Applicable terms",
    "Native ARM64 proof",
    "Secondary checks",
    "Dependency and image review",
    "Hosted AMD64 verification and retirement",
)
REPORT_CONTENT = {
    "Applicable terms": (
        "14 days",
        "12 hours",
        "24 hours",
        "development permission",
        "Individual",
    ),
    "Hosted AMD64 verification and retirement": (
        "GitHub Actions",
        "Testcontainers",
        "Playwright",
        "subscription",
    ),
}
ARCHS = ("arm64", "aarch64")


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root)


def input_tree(root):
    names = git(
        root, "ls-files", "--cached", "--others", "--exclude-standard", "-z"
    ).split(b"\0")
    inputs = {}
    for name in sorted(set(filter(None, names))):
        path = Path(os.fsdecode(name))
        if path.parts[0] == ".planning" or path in (GUIDE, REPORT):
            continue
        source = root / path
        if source.is_symlink():
            target = source.resolve()
            require(
                target.is_relative_to(root) and target.is_file(),
                f"Invalid execution input symlink: {path}",
            )
            inputs[path.as_posix()] = [os.readlink(source), file_sha(target)]
        elif source.is_file():
            inputs[path.as_posix()] = [
                stat.S_IMODE(source.stat().st_mode),
                file_sha(source),
            ]
        else:
            inputs[path.as_posix()] = None
    for path in ("probe/verify_evidence.py", "probe/verify_secondary.py"):
        require(inputs.get(path), f"Missing execution input: {path}")
    return payload_sha(inputs)


def collect_files(directory):
    files = {}
    for item in directory.rglob("*"):
        name = item.relative_to(directory)
        if name.parts[0] in (MANIFEST, "previous-build"):
            continue
        require(not item.is_symlink(), f"Unexpected evidence symlink: {name}")
        if item.is_file():
            files[name.as_posix()] = file_sha(item)
    return files


def set_aside_outputs(root, directory):
    generated = (
        "probe/build/classes",
        "probe/build/kdoc",
        "probe/build/kotlin",
        "probe/build/libs",
        "probe/build/test-results",
        "probe/build/tmp",
        "probe/build/typeid",
        "probe/build/reports/tests",
        "probe/web/build",
        "probe/web/node_modules",
        "probe/typeid/node_modules",
    )
    for name in generated:
        source = root / name
        if source.exists() or source.is_symlink():
            ignored = subprocess.run(
                ["git", "check-ignore", "--quiet", "--", name], cwd=root, check=False
            )
            require(ignored.returncode == 0, f"Expected ignored build output: {name}")
            target = directory / "previous-build" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)


def stage_commands(root, os_name):
    node = (root / ".nvmrc").read_text().strip()
    npm = read_json(root / "probe/web/package.json")["packageManager"].removeprefix(
        "npm@"
    )
    require(
        all(re.fullmatch(r"\d+\.\d+\.\d+", version) for version in (node, npm)),
        "Invalid Node/npm version owners",
    )
    require(
        os_name in ("darwin", "linux"), f"Unsupported native capture host: {os_name}"
    )
    fixture = (
        "bash",
        "-c",
        './gradlew --console=plain -p probe/web npmSetup && export PATH="$PWD/$1:$PWD/$2:$PATH"'
        " && node probe/web/build.mjs --verify-fixture",
        "frontend-fixture",
        f"probe/web/.gradle/npm/npm-v{npm}/bin",
        f"probe/web/.gradle/nodejs/node-v{node}-{os_name}-arm64/bin",
    )
    return {
        **{
            stage: (*GRADLE, task, "--rerun-tasks")
            for stage, (task, _) in STAGES.items()
        },
        "frontend-fixture": fixture,
    }


def graph_commands():
    commands = {
        f"dependencies-{configuration}": (
            *GRADLE,
            ":probe:dependencies",
            "--configuration",
            configuration,
        )
        for configuration in (*RUNTIME_GRAPHS, *CONTROL_GRAPHS)
    }
    for configuration in (*RUNTIME_GRAPHS, *CONTROL_GRAPHS[:3], "kdocFormatter"):
        for key, module in (
            ("guava", "com.google.guava:guava"),
            ("pgjdbc", "org.postgresql:postgresql"),
        ):
            commands[f"{key}-{configuration}"] = (
                *GRADLE,
                ":probe:dependencyInsight",
                "--configuration",
                configuration,
                "--dependency",
                module,
            )
    for key, configuration, module in (
        ("transport", "runtimeClasspath", "io.axoniq:axonserver-connector-java"),
        (
            "containers",
            "integrationTestRuntimeClasspath",
            "org.testcontainers:testcontainers",
        ),
        (
            "jupiter",
            "integrationTestRuntimeClasspath",
            "org.junit.jupiter:junit-jupiter-engine",
        ),
        ("kotlin", "runtimeClasspath", "org.jetbrains.kotlin:kotlin-stdlib"),
    ):
        commands[f"selection-{key}"] = (
            *GRADLE,
            ":probe:dependencyInsight",
            "--configuration",
            configuration,
            "--dependency",
            module,
        )
    return commands


class Run:
    def __init__(self, root, directory):
        self.root = root
        self.directory = directory
        self.run_id = directory.name
        self.revision = git(root, "rev-parse", "HEAD").decode().strip()
        self.inputs = input_tree(root)
        self.started_at = utc_now()
        self.producers = {}
        self.environment = {
            **os.environ,
            "PROBE_RUN_ID": self.run_id,
            "PROBE_EVIDENCE_DIR": str(directory),
        }

    def command(
        self, name, command, output=None, *, docker_unreachable=False, timeout=360
    ):
        output = output or f"commands/{name}.txt"
        log = self.directory / output
        log.parent.mkdir(parents=True, exist_ok=True)
        env = self.environment.copy()
        if docker_unreachable:
            for variable in (
                "DOCKER_CONTEXT",
                "TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE",
                "TESTCONTAINERS_HOST_OVERRIDE",
            ):
                env.pop(variable, None)
            env["DOCKER_HOST"] = OFFLINE_DOCKER
        started = utc_now()
        print(f"{self.run_id}: {name}", flush=True)
        code, stdout, launch_error = secondary.capture(command, self.root, env, timeout)
        log.write_text(stdout, encoding="utf-8")
        self.producers[name] = {
            "runId": self.run_id,
            "inputSha256": self.inputs,
            "argv": list(command),
            "exitCode": code,
            "launchError": launch_error,
            "output": output,
            "outputSha256": file_sha(log),
            "startedAt": started,
            "finishedAt": utc_now(),
            "dockerHost": OFFLINE_DOCKER if docker_unreachable else None,
        }
        write_json(self.directory / "commands.json", self.producers)
        require(
            code == 0 and launch_error is None,
            f"{name} failed (exit {code}); see {log}",
        )
        return stdout

    def junit(self, producer, original, output):
        source = self.root / original
        target = self.directory / output
        attempt = self.producers[producer]
        require(
            source.is_file()
            and source.stat().st_mtime > instant(attempt["startedAt"]).timestamp(),
            f"{producer}: missing or stale JUnit XML",
        )
        shutil.copyfile(source, target)


def result_text(directory, producers, name):
    return inside(directory, producers[name]["output"]).read_text(encoding="utf-8")


def check_build_graph(directory, producers):
    def tasks(name):
        output = result_text(directory, producers, name)
        return set(re.findall(r"(?m)^(:[\w:-]+) SKIPPED\s*$", output))

    ordinary = tasks("ordinary-dry-run")
    require(
        {":probe:build", ":probe:test"} <= ordinary,
        "Ordinary build graph omits the build or smoke test",
    )
    require(
        not any(
            re.search(r"integration|docker|container|image|packeto", path, re.I)
            for path in ordinary
        ),
        "Ordinary build graph contains an opt-in runtime or image task",
    )
    explicit = tasks("opt-in-dry-run")
    require(
        {":probe:integrationTest", ":probe:frontendImageProbe"} <= explicit,
        "Missing explicit integration or image task",
    )


def check_docker_unreachable(directory):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(2)
        result = connection.connect_ex(("127.0.0.1", 1))
    write_json(
        directory / "docker-unreachable.json",
        {
            "runId": directory.name,
            "endpoint": OFFLINE_DOCKER,
            "result": errno.errorcode.get(result),
        },
    )
    require(
        result == errno.ECONNREFUSED,
        "The deliberately unavailable Docker endpoint did not refuse the connection",
    )


def registry_artifacts(images):
    yield "index", "manifests", images["index"].split("@", 1)[1], OCI + "index.v1+json"
    for arch in ("arm64", "amd64"):
        yield (
            f"{arch}-manifest",
            "manifests",
            images[arch]["digest"],
            OCI + "manifest.v1+json",
        )
        yield f"{arch}-config", "blobs", images[arch]["config"], OCI + "config.v1+json"


def capture_registry(directory, images, input_hash):
    started = utc_now()
    with urlopen(REGISTRY_AUTH, timeout=25) as response:
        require(response.status == 200, "Anonymous registry authentication failed")
        token = json.load(response)["token"]
    records = {}
    for name, route, digest, accept in registry_artifacts(images):
        target = f"{REGISTRY}/{route}/{digest}"
        request = Request(target, headers={"Accept": accept})
        request.add_unredirected_header("Authorization", f"Bearer {token}")
        with urlopen(request, timeout=25) as response:
            require(response.status == 200, f"Registry did not return {name}")
            body = response.read()
        artifact = directory / "oci" / f"{name}.json"
        artifact.parent.mkdir(exist_ok=True)
        artifact.write_bytes(body)
        records[name] = {
            "url": target,
            "accept": accept,
            "httpStatus": 200,
            "sha256": file_sha(artifact),
        }
    return {
        "runId": directory.name,
        "inputSha256": input_hash,
        "startedAt": started,
        "finishedAt": utc_now(),
        "artifacts": records,
    }


def check_registry(directory, manifest, images, integration_end):
    registry = manifest["registry"]
    require(
        registry["runId"] == directory.name
        and registry["inputSha256"] == manifest["inputSha256"]
        and integration_end
        <= instant(registry["startedAt"])
        <= instant(registry["finishedAt"])
        <= instant(manifest["finishedAt"]),
        "Missing or foreign OCI registry acquisition",
    )
    records = registry["artifacts"]
    documents = {}
    for name, route, digest, accept in registry_artifacts(images):
        artifact = directory / "oci" / f"{name}.json"
        require(
            records[name]
            == {
                "url": f"{REGISTRY}/{route}/{digest}",
                "accept": accept,
                "httpStatus": 200,
                "sha256": file_sha(artifact),
            }
            and digest == "sha256:" + records[name]["sha256"],
            f"OCI response bytes do not match {name}",
        )
        documents[name] = read_json(artifact)
    require(set(records) == set(documents), "Unexpected OCI registry artifact")
    index = documents["index"]
    require(
        index["mediaType"] == OCI + "index.v1+json",
        "Expected the OCI image index media type",
    )
    for arch in ("arm64", "amd64"):
        descriptors = [
            item
            for item in index["manifests"]
            if item.get("platform", {}).get("os") == "linux"
            and item["platform"].get("architecture") == arch
            and item.get("annotations", {}).get("vnd.docker.reference.type")
            != "attestation-manifest"
        ]
        child = documents[f"{arch}-manifest"]
        config = documents[f"{arch}-config"]
        require(
            len(descriptors) == 1
            and descriptors[0]["digest"] == images[arch]["digest"]
            and child["mediaType"] == OCI + "manifest.v1+json"
            and child["config"]["digest"] == images[arch]["config"]
            and config["os"] == "linux"
            and config["architecture"] == arch
            and config["rootfs"]["diff_ids"],
            f"OCI index, manifest and config do not identify one runnable linux/{arch} image",
        )


def selected_jdks(directory, producers):
    versions = result_text(directory, producers, "gradle-version")
    daemon = re.search(r"(?m)^Daemon JVM:\s+(.+?)(?: \(.*\))?$", versions)
    require(daemon, "Gradle did not identify its daemon JVM")
    compilers = set()
    for name in ("ordinary-cold", "ordinary-warm"):
        output = result_text(directory, producers, name)
        homes = set(
            re.findall(r"(?m)Kotlin compilation 'jdkHome' argument: ([^\r\n]+)", output)
        )
        require(
            len(homes) == 1, f"{name}: Kotlin compilation did not identify a single JDK"
        )
        compilers.update(homes)
    require(
        len(compilers) == 1,
        "Kotlin compilation changed JDK between the cold and warm build",
    )
    return {"daemon-jvm": Path(daemon[1]), "compiler-jvm": Path(compilers.pop())}


def jdk_command(home):
    return (str(home / "bin/java"), "-XshowSettings:properties", "-version")


def jdk_fingerprints(homes):
    return {
        name: payload_sha(
            {file: file_sha(home / file) for file in ("bin/java", "release")}
        )
        for name, home in homes.items()
    }


def check_smoke(directory, producers, core):
    versions = result_text(directory, producers, "gradle-version")
    require(
        re.search(rf"(?m)^Gradle {re.escape(core['gradle'])}$", versions),
        "Gradle version differs from the wrapper",
    )
    require(
        re.search(r"(?m)^OS:\s+.*\b(?:arm64|aarch64)$", versions),
        "Gradle launcher host is not native ARM64",
    )
    launcher = re.search(r"(?m)^Launcher JVM:\s+(.+)$", versions)
    require(
        launcher
        and core["javaVersion"] in launcher[1]
        and core["javaVendor"] in launcher[1],
        "Gradle launcher JVM is missing or differs",
    )
    for name in ("daemon-jvm", "compiler-jvm"):
        observed = result_text(directory, producers, name)
        properties = dict(
            re.findall(
                r"(?m)^\s+(java\.runtime\.version|java\.vendor|os\.arch) = (.+)$",
                observed,
            )
        )
        require(
            properties.get("java.runtime.version") == core["javaVersion"]
            and properties.get("java.vendor") == core["javaVendor"]
            and properties.get("os.arch") in ARCHS,
            f"{name}: Java build, vendor or architecture differs from the test worker",
        )
    for run in ("ordinary-cold", "ordinary-warm"):
        group = producers[run]
        require(
            group["dockerHost"] == OFFLINE_DOCKER, f"{run}: Docker must be unreachable"
        )
        suite = ET.parse(directory / f"{run}-junit.xml").getroot()
        cases = suite.findall("testcase")
        require(
            suite.attrib.get("name") == "probe.ProbeContractsTest"
            and suite.attrib.get("tests") == "1"
            and all(
                suite.attrib.get(key) == "0"
                for key in ("errors", "skipped", "failures")
            )
            and len(cases) == 1
            and cases[0].attrib["name"].split("(", 1)[0]
            == "the enrollment contract preserves case sensitive tags"
            and not any(
                cases[0].find(tag) is not None
                for tag in ("failure", "error", "skipped")
            ),
            f"{run}: named smoke test did not pass",
        )
        require(
            instant(group["startedAt"])
            <= instant(suite.attrib["timestamp"])
            <= instant(group["finishedAt"]),
            f"{run}: unrelated smoke JUnit XML",
        )
        stdout = "\n".join(node.text or "" for node in suite.iter("system-out"))
        require(
            any(
                f"PROBE_JAVA vendor={core['javaVendor']} version={core['javaVersion']} arch={arch}"
                in stdout
                for arch in ARCHS
            ),
            f"{run}: smoke worker identity differs from native JVMs",
        )
        output = result_text(directory, producers, run)
        require(
            re.search(r"(?m)^> Task :probe:compileKotlin\s*$", output),
            f"{run}: Kotlin compilation did not execute",
        )
        require(
            re.search(r"(?m)^> Task :probe:test\s*$", output),
            f"{run}: smoke worker did not execute",
        )


def selected_version(configuration, output, module):
    selection = re.findall(
        rf"(?m)[+\\]--- {re.escape(module)}(?=[: ]|$)(?::(\S+))?(?: -> (\S+))?(.*)$",
        output,
    )
    selected = {
        replacement or declared
        for declared, replacement, flags in selection
        if "(c)" not in flags and "(n)" not in flags
    }
    require(
        len(selected) == 1 and "" not in selected,
        f"{configuration}: missing or ambiguous selection of {module}",
    )
    return selected.pop()


def check_graphs(directory, producers, core):
    expected = {
        "org.springframework.boot:spring-boot-dependencies": core["springBoot"],
        "org.axonframework:axon-framework-bom": core["axon"],
        "io.axoniq.framework:axoniq-framework-bom": core["axoniq"],
        "io.axoniq.framework:axoniq-spring-boot-starter": core["axoniq"],
        "io.axoniq.framework:axon-server-connector": core["axoniq"],
        "org.jetbrains.kotlin:kotlin-stdlib": core["kotlin"],
    }
    graphs = {}
    for configuration in (*RUNTIME_GRAPHS, *CONTROL_GRAPHS):
        output = result_text(directory, producers, f"dependencies-{configuration}")
        require(
            re.search(rf"(?m)^{configuration}\b", output) and " FAILED" not in output,
            f"Missing or unresolved graph for {configuration}",
        )
        graphs[configuration] = output
        if configuration in (
            "runtimeClasspath",
            "integrationTestRuntimeClasspath",
            "compileClasspath",
        ):
            for module, version in expected.items():
                require(
                    selected_version(configuration, output, module) == version,
                    f"{configuration}: unexpected resolved version of {module}",
                )
    runtime = "runtimeClasspath"
    integration = "integrationTestRuntimeClasspath"
    require(
        selected_version(
            integration, graphs[integration], "org.junit.jupiter:junit-jupiter-engine"
        )
        == core["junit"],
        "Integration Jupiter engine differs from the selected JUnit version",
    )
    modules = {
        "Axon Server Java transport": (runtime, "io.axoniq:axonserver-connector-java"),
        "Reactor Core": (runtime, "io.projectreactor:reactor-core"),
        "Testcontainers": (integration, "org.testcontainers:testcontainers"),
        "Runtime Guava": (runtime, "com.google.guava:guava"),
        "Formatter Guava": ("kdocFormatter", "com.google.guava:guava"),
    }
    return {
        key: selected_version(configuration, graphs[configuration], module)
        for key, (configuration, module) in modules.items()
    }


def classify_stage(store, stage, core, command, upstream):
    prerequisite = secondary.PREREQUISITES.get(stage)
    if prerequisite and upstream[prerequisite]["status"] != "Pass":
        prior = upstream[prerequisite]
        store.classify(
            stage,
            core,
            argparse.Namespace(
                prerequisite=prerequisite,
                status=prior["status"],
                pending_command=shlex.join(command),
                cause=prior.get("cause"),
                reason=f"Required stage {prerequisite} did not pass",
                retry=prior["retry"],
            ),
        )
    else:
        store.run_stage(stage, core, list(command))
        record = store.load_stage(stage, core)
        if record["status"] != "Pass":
            attempt = record["attempts"][-1]
            require(
                attempt["exitCode"] != 0,
                f"{stage}: even though the command exited zero, the claimed result was absent",
            )
            signature = attempt["signature"]
            retry = "Restore the dependency identified in the retained diagnostic and rerun this exact command."
            if secondary.environmental_failure(signature, attempt["launchError"]):
                store.classify(
                    stage,
                    core,
                    argparse.Namespace(
                        prerequisite=None,
                        status="Unverified",
                        cause=signature,
                        reason=None,
                        retry=retry,
                    ),
                )
            else:
                require(signature, f"{stage}: missing concrete failure diagnostic")
                store.run_stage(stage, core, list(command))
                if store.load_stage(stage, core)["status"] != "Pass":
                    store.classify(
                        stage,
                        core,
                        argparse.Namespace(
                            prerequisite=None,
                            status="Blocked",
                            cause=None,
                            reason=signature,
                            retry=retry,
                        ),
                    )
    store.check(stage, core)
    return store.load_stage(stage, core)


def check_secondaries(store, core, commands, started, finished):
    outcomes = {}
    for group, stages in GROUPS.items():
        records = []
        for stage in stages:
            record = store.load_stage(stage, core)
            store.validate_record(stage, core, record)
            for attempt in record["attempts"]:
                require(
                    attempt["argv"] == list(commands[stage])
                    and started
                    <= instant(attempt["startedAt"])
                    <= instant(attempt["finishedAt"])
                    <= finished,
                    f"{stage}: secondary command or time differs from the acceptance run",
                )
            if record.get("prerequisiteStage"):
                require(
                    shlex.split(record["pendingCommand"]) == list(commands[stage]),
                    f"{stage}: pending command differs from the acceptance run",
                )
            records.append(record)
        status = next(
            (record["status"] for record in records if record["status"] != "Pass"),
            "Pass",
        )
        result = read_json(store.directory / "secondary" / f"{group}.json")
        require(
            result
            == {
                "runId": core["runId"],
                "coreTupleSha256": core["coreTupleSha256"],
                "coreEvidenceSha256": core["coreEvidenceSha256"],
                "status": status,
                "stages": records,
            },
            f"{group}: grouped secondary outcomes differ from their stage records",
        )
        outcomes[group] = status
    return outcomes


def check_run(root, directory, manifest):
    started = instant(manifest["startedAt"])
    finished = instant(manifest["finishedAt"])
    require(
        manifest["schema"] == 1
        and manifest["runId"] == directory.name
        and re.fullmatch(r"acceptance-[a-z0-9_-]+", directory.name)
        and re.fullmatch(r"[a-f0-9]{40}", manifest["revision"])
        and started < finished <= datetime.now(finished.tzinfo),
        "Invalid acceptance run metadata",
    )
    require(
        manifest["inputSha256"] == input_tree(root),
        "Execution inputs differ from the captured input tree",
    )
    require(
        manifest["files"] == collect_files(directory),
        "An acceptance result is missing, foreign, or changed",
    )
    require(
        read_json(directory / "docker-unreachable.json")
        == {
            "runId": directory.name,
            "endpoint": OFFLINE_DOCKER,
            "result": "ECONNREFUSED",
        },
        "The ordinary build has no correlated proof of an unreachable Docker endpoint",
    )
    producers = read_json(directory / "commands.json")
    java_commands = {
        name: jdk_command(home)
        for name, home in selected_jdks(directory, producers).items()
    }
    commands = {
        "gradle-version": (*GRADLE, "--version"),
        "ordinary-dry-run": DRY_RUN,
        "opt-in-dry-run": OPT_IN_DRY_RUN,
        "ordinary-cold": BUILD_COMMAND,
        "ordinary-warm": BUILD_COMMAND,
        "integration": CORE_COMMAND,
        **java_commands,
        **graph_commands(),
    }
    require(
        manifest["producers"] == producers and producers.keys() == commands.keys(),
        "Missing or foreign producer record",
    )
    for name, command in commands.items():
        record = producers[name]
        require(
            record["runId"] == directory.name
            and record["inputSha256"] == manifest["inputSha256"]
            and record["argv"] == list(command)
            and record["exitCode"] == 0
            and record["launchError"] is None
            and started
            <= instant(record["startedAt"])
            <= instant(record["finishedAt"])
            <= finished
            and manifest["files"].get(record["output"]) == record["outputSha256"],
            f"{name}: invalid command, raw exit, input hash, or result hash",
        )
    check_build_graph(directory, producers)
    store = Store(root, directory, directory.name)
    proof = store.load_core()
    core, images = (
        read_json(directory / name) for name in ("core.json", "images.json")
    )
    integration = producers["integration"]
    integration_start = instant(integration["startedAt"])
    integration_end = instant(integration["finishedAt"])
    suite = ET.parse(directory / "integration-junit.xml").getroot()
    require(
        integration_start
        <= instant(suite.attrib["timestamp"])
        <= instant(core["startedAt"])
        < instant(core["finishedAt"])
        <= integration_end
        and integration_start <= instant(images["checkedAt"]) <= integration_end,
        "Native JUnit, OCI resolution and core transcript are not from the captured invocation",
    )
    image_index = images["index"].split("@", 1)[1]
    require(
        image_index not in (images["arm64"]["digest"], images["amd64"]["digest"]),
        "A child reuses the image index digest",
    )
    check_registry(directory, manifest, images, integration_end)
    for output, marker in (
        (core, "PROBE_CORE"),
        (read_json(directory / "tracer.json"), "PROBE_TRACER"),
        (read_json(directory / "cleanup.json"), "PROBE_CLEANUP"),
    ):
        events = re.findall(
            rf"(?m)^\s*{marker} (.+)$", result_text(directory, producers, "integration")
        )
        require(
            len(events) == 1 and json.loads(events[0]) == output,
            f"{marker}: transcript absent or inconsistent in the raw Gradle output",
        )
    check_smoke(directory, producers, proof["coreTuple"])
    resolved = check_graphs(directory, producers, proof["coreTuple"])
    host = manifest["host"]
    require(
        host["architecture"] in ARCHS and host["python"],
        "Missing native host tool identity",
    )
    require(
        set(manifest["jdkFingerprints"]) == set(java_commands)
        and all(
            secondary.valid_sha(value) for value in manifest["jdkFingerprints"].values()
        ),
        "Missing Gradle daemon or compiler JDK fingerprints",
    )
    outcomes = check_secondaries(
        store, proof, stage_commands(root, host["os"]), integration_end, finished
    )
    require(
        manifest["tuple"] == proof["coreTuple"]
        and manifest["resolved"] == resolved
        and manifest["images"] == images
        and manifest["outcomes"] == outcomes,
        "Acceptance tuple, images or secondary outcomes changed",
    )
    return outcomes


def capture_run(root, evidence):
    require(
        platform.machine() in ARCHS, "Acceptance capture requires a native ARM64 host"
    )
    runs = evidence / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="acceptance-", dir=runs))
    run = Run(root, directory)
    check_docker_unreachable(directory)
    set_aside_outputs(root, directory)
    run.command("gradle-version", (*GRADLE, "--version"))
    run.command("ordinary-dry-run", DRY_RUN, "build-graph.txt", docker_unreachable=True)
    run.command(
        "opt-in-dry-run",
        OPT_IN_DRY_RUN,
        "opt-in-build-graph.txt",
        docker_unreachable=True,
    )
    check_build_graph(directory, run.producers)
    for name in ("ordinary-cold", "ordinary-warm"):
        run.command(name, BUILD_COMMAND, docker_unreachable=True)
        run.junit(name, SMOKE_REPORT, f"{name}-junit.xml")
    homes = selected_jdks(directory, run.producers)
    fingerprints = jdk_fingerprints(homes)
    for name, home in homes.items():
        run.command(name, jdk_command(home))
    run.command("integration", CORE_COMMAND)
    run.junit("integration", secondary.REPORT, "integration-junit.xml")
    store = Store(root, directory, directory.name)
    proof = store.describe_core(directory)
    write_json(store.provenance, proof)
    check_smoke(directory, run.producers, proof["coreTuple"])
    images = read_json(directory / "images.json")
    registry = capture_registry(directory, images, run.inputs)
    for name, command in graph_commands().items():
        run.command(name, command)
    resolved = check_graphs(directory, run.producers, proof["coreTuple"])
    records = {}
    host = {
        "os": platform.system().lower(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
    }
    commands = stage_commands(root, host["os"])
    for stage in STAGES:
        records[stage] = classify_stage(store, stage, proof, commands[stage], records)
    finished = utc_now()
    outcomes = check_secondaries(
        store,
        proof,
        commands,
        instant(run.producers["integration"]["finishedAt"]),
        instant(finished),
    )
    require(
        run.inputs == input_tree(root) and fingerprints == jdk_fingerprints(homes),
        "Execution inputs changed during acceptance capture",
    )
    manifest = {
        "schema": 1,
        "runId": directory.name,
        "revision": run.revision,
        "inputSha256": run.inputs,
        "startedAt": run.started_at,
        "finishedAt": finished,
        "tuple": proof["coreTuple"],
        "host": host,
        "jdkFingerprints": fingerprints,
        "resolved": resolved,
        "images": images,
        "registry": registry,
        "outcomes": outcomes,
        "producers": run.producers,
        "files": collect_files(directory),
    }
    check_run(root, directory, manifest)
    write_json(directory / MANIFEST, manifest)
    write_json(
        evidence / POINTER,
        {"runId": directory.name, "manifestSha256": file_sha(directory / MANIFEST)},
    )
    return directory


def report_fields(manifest, manifest_sha):
    selected, images, outcomes = (
        manifest[key] for key in ("tuple", "images", "outcomes")
    )
    return {
        "Acceptance run": manifest["runId"],
        "Tested revision": manifest["revision"],
        "Input tree SHA-256": manifest["inputSha256"],
        "Manifest SHA-256": manifest_sha,
        "Gradle": selected["gradle"],
        "Kotlin": selected["kotlin"],
        "Spring Boot": selected["springBoot"],
        "Axon Framework": selected["axon"],
        "Axoniq Framework": selected["axoniq"],
        "JUnit": selected["junit"],
        "Temurin": selected["javaVersion"],
        "JVM architecture": selected["architecture"],
        "Docker platform": selected["dockerPlatform"],
        "Docker server": selected["docker"],
        "Axon Server index": images["index"],
        "ARM64 manifest": images["arm64"]["digest"],
        "ARM64 config": images["arm64"]["config"],
        "AMD64 manifest": images["amd64"]["digest"],
        "AMD64 config": images["amd64"]["config"],
        **manifest["resolved"],
        **{group: outcomes[group] for group in GROUPS},
    }


def read_report_fields(report):
    fields = {}
    for key, value in re.findall(
        r"(?m)^\| ([^|\r\n]+?) \| `([^`\r\n]+)` \|[ \t]*$", report
    ):
        require(key not in fields, f"Duplicate report field: {key}")
        fields[key] = value
    return fields


def check_report(root, path, manifest, manifest_sha):
    report = path.read_text(encoding="utf-8")
    fields = read_report_fields(report)
    for field, expected in report_fields(manifest, manifest_sha).items():
        require(
            fields.get(field) == expected, f"Report field differs or is absent: {field}"
        )
    sections = dict(re.findall(r"(?ms)^## ([^\r\n]+)\n(.*?)(?=^## |\Z)", report))
    for section in REPORT_SECTIONS:
        require(
            sections.get(section, "").strip(),
            f"Missing or empty report section: {section}",
        )
        for detail in REPORT_CONTENT.get(section, ()):
            require(
                detail.lower() in sections[section].lower(),
                f"Report section {section} omits {detail}",
            )
    guide = root / GUIDE
    links = re.findall(r"\]\(([^()\s]+)\)", guide.read_text(encoding="utf-8"))
    require(
        any(
            (guide.parent / link).resolve() == path.resolve()
            and not Path(link).is_absolute()
            for link in links
        ),
        "The probe guide lacks a relative link to this report",
    )


def locate_run(evidence, report):
    if report:
        run_id = read_report_fields(report.read_text(encoding="utf-8")).get(
            "Acceptance run"
        )
        require(
            run_id and re.fullmatch(r"acceptance-[a-z0-9_-]+", run_id),
            "Report has no valid acceptance run ID",
        )
        if (evidence / MANIFEST).is_file():
            require(
                evidence.name == run_id, "Report references a different acceptance run"
            )
            return evidence
        return inside(evidence, f"runs/{run_id}")
    if (evidence / MANIFEST).is_file():
        return evidence
    pointer = read_json(evidence / POINTER)
    directory = inside(evidence, f"runs/{pointer['runId']}")
    require(
        file_sha(directory / MANIFEST) == pointer["manifestSha256"],
        "Current acceptance manifest hash differs",
    )
    return directory


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--capture", action="store_true")
    modes.add_argument("--report", type=Path)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    args = parser.parse_args(argv)
    try:
        evidence = (ROOT / args.evidence).resolve()
        allowed = (ROOT / DEFAULT_EVIDENCE).resolve()
        require(
            evidence.is_relative_to(allowed),
            f"Evidence must be within {DEFAULT_EVIDENCE}",
        )
        if args.capture:
            require(
                evidence == allowed,
                f"Capture expects the evidence root {DEFAULT_EVIDENCE}",
            )
            evidence.mkdir(parents=True, exist_ok=True)
            with (evidence / ".verification.lock").open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                directory = capture_run(ROOT, evidence)
        else:
            report = (ROOT / args.report).resolve() if args.report else None
            directory = locate_run(evidence, report)
            manifest = read_json(directory / MANIFEST)
            check_run(ROOT, directory, manifest)
            if report:
                check_report(ROOT, report, manifest, file_sha(directory / MANIFEST))
        print(f"Acceptance evidence verified for {directory.name}")
        return 0
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        ET.ParseError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Acceptance evidence failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
