"""Capture and verify ignored evidence for the Phase 01 secondary checks.

A producer emits one line beginning with PROBE_SECONDARY followed by a JSON
object with its stage name and measured assertions. See validate_observations
for the fields consumed for each stage. The runner binds that line and any
relative supporting files to the command attempt.
"""

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
GRADLE = ("./gradlew", "--console=plain")
CORE_COMMAND = (*GRADLE, ":probe:integrationTest", "--rerun-tasks")
CASES = {
    "PROBE_TRACER": "a remote command persists a tagged event",
    "PROBE_CORE": "overlapping writes leave one winner and notify the remote subscriber",
    "PROBE_CLEANUP": "a forced failure closes the subscription and owned resources",
}
REPORT = "probe/build/test-results/integrationTest/TEST-probe.AxonProbeTest.xml"
CORE_FILES = ("core.json", "tracer.json", "cleanup.json", "images.json", "integration-junit.xml")
STAGES = {
    "frontend-fixture": ("npm", ("probe/web/package.json", "probe/web/package-lock.json", "probe/web/build.mjs")),
    "frontend-assets": (":probe:frontendAssets", ("probe/web/build.gradle.kts", "probe/web/settings.gradle.kts")),
    "frontend-image": (":probe:frontendImageProbe", ("probe/web/build.gradle.kts", "mise.toml")),
    "kotest": (":probe:kotestProbe", ("probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt",)),
    "kdoc": (":probe:kdocProbe", ("probe/kdoc/Specimen.kt",)),
    "typeid-jvm": (":probe:typeIdJvmVectors", ("probe/src/typeIdProbe/kotlin/probe/TypeIdVectors.kt", "probe/typeid/vectors.json")),
    "typeid-exchange": (":probe:typeIdProbe", ("probe/typeid/check-vectors.ts", "probe/typeid/package.json", "probe/typeid/package-lock.json")),
}
PREREQUISITES = {"frontend-assets": "frontend-fixture", "frontend-image": "frontend-assets", "typeid-exchange": "typeid-jvm"}
GROUPS = {
    "frontend": ("frontend-fixture", "frontend-assets", "frontend-image"),
    "typeid": ("typeid-jvm", "typeid-exchange"),
    "kotest": ("kotest",),
    "kdoc": ("kdoc",),
}
ARCHITECTURES = {"arm64", "aarch64"}
NODE_STAGES = {"frontend-fixture", "frontend-assets", "frontend-image", "typeid-exchange"}
TOOL_VERSION = r"v?\d+\.\d+\.\d+(?:[-+][\w.+-]+)?"
ENVIRONMENT_ERROR = re.compile(
    r"command not found|network is unreachable|"
    r"temporary failure in name resolution|could not resolve host|connection refused|"
    r"UnknownHostException|name or service not known|nodename nor servname provided|"
    r"certificate verify failed|no space left on device|connection timed? ?out", re.I
)
PERMISSION_ERROR = re.compile(r"operation not permitted|permission denied|approval (?:denied|required)", re.I)
CORE_FAILURE = re.compile(r"> Task :probe:(?:compileKotlin|compileJava|integrationTest|test) FAILED")
GENERIC_FAILURE = re.compile(
    r"^(?:Task .+ FAILED|FAILURE: Build failed.*|BUILD FAILED.*|Execution failed for task .*|"
    r"A problem occurred .+|There were failing tests.*|Process .+ finished with non-zero exit value .+|"
    r"\d+ tests? (?:completed|failed).*)$", re.I
)
DEFAULT_DIR = "probe/build/reports/feasibility"


class EvidenceError(ValueError):
    """A recorded claim cannot be established from its evidence."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(path.read_bytes())


def payload_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")
    Path(output.name).replace(path)


def read_json(path):
    with path.open(encoding="utf-8") as source:
        value = json.load(source)
    require(isinstance(value, dict), f"{path.name} must be a JSON object")
    return value


def inside(base, name):
    path = (base / name).resolve()
    require(path.is_relative_to(base), "Evidence path leaves the run directory")
    return path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def instant(value):
    # Java Instant can report nine fractional digits. Python 3.9 parses three or six.
    normalized = re.sub(r"\.(\d{1,9})(?=Z$|[+-]\d{2}:\d{2}$)",
                        lambda match: "." + match[1][:6].ljust(6, "0"), value)
    result = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    require(result.utcoffset() == timezone.utc.utcoffset(result), "Evidence timestamp must be UTC")
    return result


def valid_sha(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def digest_paths(root, paths):
    hashes = {}
    for name in paths:
        path = root / name
        if path.is_file():
            hashes[name] = file_sha(path)
        elif path.is_dir():
            for item in sorted(path.rglob("*")):
                if item.is_file() and not set(item.relative_to(path).parts).intersection(
                    {"build", "node_modules", ".gradle", "dist", "__pycache__"}
                ):
                    hashes[item.relative_to(root).as_posix()] = file_sha(item)
    return payload_sha(hashes)


def validate_cleanup(cleanup, pids=None):
    exited = cleanup["exitedPids"]
    require(cleanup["containerRemoved"] is True and valid_sha(cleanup["containerId"]), "Container was not removed")
    require(len(set(exited)) == 2 and all(type(pid) is int and pid > 0 for pid in exited), "Two child PIDs must exit")
    if pids is not None:
        require(set(exited) == set(pids), "Exited PIDs differ from the command and projection JVMs")
    require(cleanup["cancelledSubscriptions"] == 1, "The opened subscription was not cancelled")
    timings = cleanup["timingsMs"]
    require(0 < timings["serverReadyMs"] <= 90_000 and 0 <= timings["cleanupMs"] < 300_000,
            "Readiness or cleanup exceeded its budget")


def validate_core(directory, feature, image_pin):
    documents = {name: read_json(directory / name) for name in CORE_FILES[:-1]}
    core, tracer, forced, images = (documents[name] for name in CORE_FILES[:-1])
    run_id = core["runId"]
    require(re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id), "Invalid core run ID")
    require(len({run_id, tracer["runId"], forced["runId"]}) == 3, "Core cases reused run IDs")
    require(core["context"] == "default" and core["dcb"] is True and core["credentialFree"] is True,
            "Missing credential-free default DCB context")
    require(all(record["initialEvents"] == 0 for record in (core, tracer, forced)), "A case did not begin empty")
    require(core["marker"] == 0, "Missing server marker from empty history")
    roles = [core[key] for key in ("worker", "command", "projection")]
    require(len({role["pid"] for role in roles}) == 3 and all(role["pid"] > 0 for role in roles),
            "Core roles must have distinct process IDs")
    clients = core["registeredClients"]
    require(len(clients) == 3 and len(set(clients.values())) == 3
            and set(clients) == {role["clientId"] for role in roles}, "Core registrations are missing or shared")
    versions = {role["javaVersion"] for role in roles}
    require(len(versions) == 1 and re.match(rf"^{feature}(?!\d)", next(iter(versions))), "Unexpected Java runtime version")
    for role in roles:
        require(role["architecture"] in ARCHITECTURES and role["javaFeature"] == feature
                and role["javaVendor"] == "Eclipse Adoptium", "Core role did not use native Temurin")
        require(role["engine"].endswith(".AxonServerEventStorageEngine")
                and role["commandBus"].endswith(".DistributedCommandBus")
                and role["queryBus"].endswith(".DistributedQueryBus"), "Core role used different messaging components")
    receipt = core["receipt"]
    winner = receipt["eventId"]
    require(receipt["role"] == core["command"] and receipt["runId"] == run_id and winner != core["losingEventId"],
            "Winning command receipt does not match the remote writer")
    require(core["studentId"] != core["losingStudentId"], "The stale append did not use an independent student")
    tag_reads = core["tagReads"]
    require(all(tag_reads[key] == [winner] for key in ("course", "winnerStudent", "courseAndStudent", "history"))
            and tag_reads["loserStudent"] == [], "Independent durable reads do not prove the sole winner")
    require(core["rejection"] == {
        "type": "AppendEventsTransactionRejectedException", "status": "CANCELLED",
        "serverReason": "ConsistencyConditionException",
    }, "Stale append did not receive the typed server refusal")
    for state, count in (("before", 0), ("initial", 0), ("update", 1), ("after", 1)):
        observed = core[state]
        require(observed["runId"] == run_id and observed["courseId"] == core["courseId"]
                and observed["role"] == core["projection"] and observed["processorReady"] is True
                and observed["enrollments"] == count and observed["eventId"] == (winner if count else None),
                f"Remote query observation {state} is inconsistent")
    validate_cleanup(core["cleanup"], [role["pid"] for role in roles[1:]])
    validate_cleanup(forced["cleanup"])
    require(forced["cleanup"]["containerId"] != core["cleanup"]["containerId"]
            and forced["unrelatedNetworkPreserved"] is True
            and forced["reason"] == "controlled failure after subscription startup", "Missing scoped failure cleanup")
    require(tracer["courseEventId"] == tracer["studentEventId"] == tracer["receipt"]["eventId"],
            "Tracer reads no longer agree")
    require(images["runId"] == run_id and images["index"] == image_pin and images["runningArchitecture"] in ARCHITECTURES
            and images["daemon"] in {"linux/" + arch for arch in ARCHITECTURES}, "Image evidence is foreign or non-native")
    children = [images["arm64"], images["amd64"]]
    for child, architecture in zip(children, ("arm64", "amd64")):
        require(child["architecture"] == architecture and all(
            isinstance(child[key], str) and child[key].startswith("sha256:") and valid_sha(child[key][7:])
            for key in ("digest", "config")
        ), "Missing runnable OCI child evidence")
    require(len({child["digest"] for child in children}) == len({child["config"] for child in children}) == 2
            and images["runningImageId"] == images["arm64"]["config"], "Running image does not match the native OCI child")

    suite = ET.parse(directory / "integration-junit.xml").getroot()
    require(suite.tag == "testsuite" and suite.attrib.get("name") == "probe.AxonProbeTest"
            and all(suite.attrib.get(key) == "0" for key in ("errors", "failures", "skipped"))
            and suite.attrib.get("tests") == str(len(CASES)), "JUnit did not pass the complete core suite")
    cases = suite.findall("testcase")
    require(len(cases) == len(CASES) and {case.attrib["name"].split("(", 1)[0] for case in cases} == set(CASES.values())
            and all(case.attrib.get("classname") == "probe.AxonProbeTest"
                    and not list(case.iterfind("failure")) and not list(case.iterfind("error"))
                    and not list(case.iterfind("skipped")) for case in cases), "Required JUnit cases are absent or nonpassing")
    require(instant(suite.attrib["timestamp"]) <= instant(core["startedAt"]) < instant(core["finishedAt"]),
            "Core transcript does not follow the JUnit start time")
    stdout = "\n".join(node.text or "" for node in suite.iter("system-out"))
    for marker, evidence in zip(("PROBE_CORE", "PROBE_TRACER", "PROBE_CLEANUP"), (core, tracer, forced)):
        matches = [json.loads(line.strip().removeprefix(marker + " ")) for line in stdout.splitlines()
                   if line.strip().startswith(marker + " ")]
        require(matches == [evidence] and evidence["test"] == "probe.AxonProbeTest." + CASES[marker],
                f"JUnit output did not match {marker}")
    return core, images


class Store:
    def __init__(self, root, directory, requested_run=None):
        self.root = root.resolve()
        self.directory = directory.resolve()
        self.requested_run = requested_run
        self.provenance = self.directory / "core-provenance.json"

    def core_inputs(self):
        return digest_paths(self.root, (
            ".java-version", "settings.gradle.kts", "build.gradle.kts", "gradle.properties", "gradlew", "gradlew.bat",
            "gradle", "probe/build.gradle.kts", "probe/src/main", "probe/src/integrationTest", "probe/src/test",
            "probe/verify_secondary.py",
        ))

    def stage_inputs(self, stage):
        shared = ("gradle", "probe/build.gradle.kts", "probe/verify_secondary.py")
        if stage.startswith("frontend"):
            paths = (".nvmrc", "mise.toml", "probe/web")
        elif stage.startswith("typeid"):
            paths = (".nvmrc", "probe/typeid", "probe/src/typeIdProbe")
        else:
            paths = STAGES[stage][1]
        return digest_paths(self.root, (*shared, *paths))

    def describe_core(self, directory):
        directory = directory.resolve()
        feature = int((self.root / ".java-version").read_text().strip())
        catalog = (self.root / "gradle/libs.versions.toml").read_text()
        pins = dict(re.findall(r'^([\w-]+)\s*=\s*"([^"]+)"', catalog, re.M))
        core, images = validate_core(directory, feature, pins["axon-server-image"])
        wrapper = (self.root / "gradle/wrapper/gradle-wrapper.properties").read_text()
        distribution = re.search(r"gradle-([0-9.]+)-bin.zip", wrapper).group(1)
        tuple_values = {
            "gradle": distribution, "kotlin": pins["kotlin"], "springBoot": pins["spring-boot"],
            "axon": pins["axon"], "axoniq": pins["axoniq"], "junit": pins["junit"], "serverIndex": images["index"],
            "arm64Image": images["arm64"]["digest"], "runningImageId": images["runningImageId"],
            "docker": images["daemonVersion"], "dockerPlatform": images["daemon"],
            "javaFeature": feature, "javaVendor": core["worker"]["javaVendor"],
            "javaVersion": core["worker"]["javaVersion"], "architecture": core["worker"]["architecture"],
        }
        hashes = {name: file_sha(directory / name) for name in CORE_FILES}
        return {
            "runId": core["runId"], "coreInputSha256": self.core_inputs(), "coreTuple": tuple_values,
            "coreTupleSha256": payload_sha(tuple_values), "coreEvidenceSha256": payload_sha(hashes),
            "files": hashes, "path": directory.relative_to(self.directory).as_posix(),
        }

    def load_core(self):
        recorded = read_json(self.provenance)
        path = inside(self.directory, recorded["path"])
        current = self.describe_core(path)
        require(recorded == current, "Core provenance is stale or corrupted")
        require(not self.requested_run or self.requested_run == current["runId"], "Core proof belongs to a different run")
        return current

    def ensure_core(self):
        try:
            return self.load_core()
        except (OSError, AttributeError, ValueError, KeyError, TypeError, ET.ParseError):
            pass
        self.directory.mkdir(parents=True, exist_ok=True)
        start_inputs = self.core_inputs()
        directory = Path(tempfile.mkdtemp(prefix="core-", dir=self.directory))
        run_id = self.requested_run or directory.name
        require(re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id), "Invalid requested run ID")
        env = {**os.environ, "PROBE_RUN_ID": run_id, "PROBE_EVIDENCE_DIR": str(directory)}
        started = datetime.now(timezone.utc)
        try:
            code, output, launch_error = capture(CORE_COMMAND, self.root, env, 360)
            (directory / "gradle-diagnostic.txt").write_text(sanitize(output, self.root), encoding="utf-8")
            require(code == 0 and launch_error is None,
                    f"Required native Axon suite failed (exit {code}); see {directory / 'gradle-diagnostic.txt'}")
            report = self.root / REPORT
            require(report.is_file() and report.stat().st_mtime > started.timestamp(), "Native integration JUnit output is stale")
            shutil.copyfile(report, directory / "integration-junit.xml")
            record = self.describe_core(directory)
            require(record["runId"] == run_id and record["coreInputSha256"] == start_inputs, "Core inputs changed during execution")
            for name in CORE_FILES:
                shutil.copyfile(directory / name, self.directory / name)
            write_json(self.provenance, record)
            return record
        except (OSError, AttributeError, ValueError, KeyError, TypeError, ET.ParseError) as error:
            raise EvidenceError(f"Required native Axon proof is invalid: {error}") from error

    def stage_path(self, stage):
        return self.directory / "stages" / f"{stage}.json"

    def stage_metadata(self, stage, core):
        return {
            "runId": core["runId"], "stage": stage, "inputSha256": self.stage_inputs(stage),
            "coreTupleSha256": core["coreTupleSha256"], "coreEvidenceSha256": core["coreEvidenceSha256"],
        }

    def load_stage(self, stage, core):
        record = read_json(self.stage_path(stage))
        require(all(record.get(key) == value for key, value in self.stage_metadata(stage, core).items()),
                f"Stage {stage} evidence is stale; recollect it for the current core proof and inputs")
        return record

    def ensure_implementation(self, stage):
        task, sources = STAGES[stage]
        require(all((self.root / source).is_file() and (self.root / source).stat().st_size > 0 for source in sources),
                f"Stage {stage} implementation is missing")
        if task.startswith(":probe:"):
            require(re.search(r"\b" + re.escape(task.split(":")[-1]) + r"\b",
                              (self.root / "probe/build.gradle.kts").read_text()),
                    f"Stage {stage} Gradle entry point is missing")

    def run_stage(self, stage, core, argv):
        self.ensure_implementation(stage)
        validate_argv(stage, argv)
        try:
            record = self.load_stage(stage, core)
        except (OSError, ValueError):
            record = {**self.stage_metadata(stage, core), "attempts": []}
        start = utc_now()
        env = {**os.environ, "PROBE_RUN_ID": core["runId"], "PROBE_EVIDENCE_DIR": str(self.directory), "PROBE_STAGE": stage}
        code, output, launch_error = capture(argv, self.root, env, 900)
        finish = utc_now()
        clean = sanitize(output, self.root)
        observations = decode_observations(clean, stage) if code == 0 else {}
        label = diagnostic_signature(clean, launch_error) if code != 0 else ""
        directory = self.directory / "diagnostics"
        directory.mkdir(exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix=f"{stage}-", dir=directory))
        diagnostic = directory / "output.txt"
        diagnostic.write_text(clean, encoding="utf-8")
        tools = {"python": sys.version.split()[0], "core": core["coreTuple"], **stage_tools(stage, clean)}
        require(self.stage_metadata(stage, core)["inputSha256"] == record["inputSha256"], "Secondary inputs changed during execution")
        artifacts = observations.get("artifacts", [])
        snapshots = {}
        if isinstance(artifacts, list) and all(isinstance(name, str) for name in artifacts):
            for i, name in enumerate(dict.fromkeys(artifacts)):
                source = inside(self.directory, name)
                if source.is_file():
                    snapshot = directory / f"artifact-{i}"
                    shutil.copyfile(source, snapshot)
                    snapshots[name] = {"path": snapshot.relative_to(self.directory).as_posix(), "sha256": file_sha(snapshot)}
        attempt = {
            "argv": argv, "startedAt": start, "finishedAt": finish, "toolVersions": tools,
            "exitCode": code, "launchError": launch_error, "diagnostic": diagnostic.relative_to(self.directory).as_posix(),
            "diagnosticSha256": file_sha(diagnostic), "signature": label, "artifacts": snapshots,
        }
        fresh = {**self.stage_metadata(stage, core), "status": "Pending",
                 "attempts": [*record["attempts"], attempt], "observations": observations}
        if code == 0:
            try:
                validate_observations(stage, observations, {name: data["sha256"] for name, data in snapshots.items()})
                self.check_stage_tools(stage, observations, tools)
            except (ValueError, KeyError, TypeError):
                pass
            else:
                fresh["status"] = "Pass"
        write_json(self.stage_path(stage), fresh)
        print(f"{stage} captured exit {code}")

    def validate_record(self, stage, core, record, chain=()):
        self.ensure_implementation(stage)
        require(stage not in chain, "Cyclic prerequisite records")
        status = record["status"]
        require(status in {"Pass", "Blocked", "Unverified"}, f"Stage {stage} has no supported classification")
        attempts = record["attempts"]
        require(isinstance(attempts, list), "Invalid attempt history")
        for attempt in attempts:
            validate_argv(stage, attempt["argv"])
            require(instant(attempt["startedAt"]) <= instant(attempt["finishedAt"]) and attempt["toolVersions"],
                    "Invalid attempt timing or tool versions")
            code = attempt["exitCode"]
            require(type(code) is int or (code is None and attempt["launchError"]), "Missing raw subprocess exit or launch error")
            diagnostic = inside(self.directory, attempt["diagnostic"])
            require(file_sha(diagnostic) == attempt["diagnosticSha256"], "Secondary diagnostic was changed")
            diagnostic_text = diagnostic.read_text()
            versions = attempt["toolVersions"]
            require(nonempty(versions.get("python")) and versions.get("core") == core["coreTuple"]
                    and {name: value for name, value in versions.items() if name not in ("python", "core")}
                    == stage_tools(stage, diagnostic_text), "Secondary tool versions differ from captured output")
            signature = diagnostic_signature(diagnostic_text, attempt["launchError"]) if code != 0 else ""
            require(attempt["signature"] == signature, "Secondary failure signature changed")
            for artifact in attempt["artifacts"].values():
                require(file_sha(inside(self.directory, artifact["path"])) == artifact["sha256"],
                        "Secondary supporting artifact was changed")
        if status != "Pass":
            require(nonempty(record.get("retry")), "A non-pass must include a concrete retry condition")
        if record.get("prerequisiteStage"):
            prerequisite = record["prerequisiteStage"]
            require(not attempts and status != "Pass" and prerequisite == PREREQUISITES.get(stage)
                    and record["reason"].strip(), "Unsubstantiated prerequisite disposition")
            validate_argv(stage, shlex.split(record["pendingCommand"]))
            path = self.stage_path(prerequisite)
            require(record["prerequisiteRecordSha256"] == file_sha(path), "Prerequisite record changed")
            upstream = self.load_stage(prerequisite, core)
            self.validate_record(prerequisite, core, upstream, (*chain, stage))
            require(upstream["status"] == status, "Prerequisite status does not support this disposition")
            return
        require(attempts, f"Stage {stage} did not run")
        latest = attempts[-1]
        diagnostic_text = inside(self.directory, latest["diagnostic"]).read_text()
        if status == "Pass":
            require(latest["exitCode"] == 0, "Pass must have a successful raw exit")
            observed = decode_observations(diagnostic_text, stage)
            require(observed == record["observations"], "Recorded observations differ from captured output")
            validate_observations(stage, observed, {name: data["sha256"] for name, data in latest["artifacts"].items()})
            self.check_stage_tools(stage, observed, latest["toolVersions"])
            self.check_pass_artifacts(stage, observed, latest["artifacts"])
        else:
            require(not PERMISSION_ERROR.search(diagnostic_text) and latest["exitCode"] != 0,
                    "A successful invocation or a permission gate cannot be classified as a secondary non-pass")
            require(not CORE_FAILURE.search(diagnostic_text), "A core build or test failure cannot be a secondary non-pass")
            require(not latest["launchError"] or status == "Unverified", "A missing executable is an environmental result")
            if status == "Blocked":
                require(nonempty(record.get("reason")) and latest["signature"], "Blocked requires a concrete measured failure")
                keys = ("argv", "toolVersions", "signature", "exitCode")
                comparable = [attempt for attempt in attempts if all(attempt[key] == latest[key] for key in keys)]
                require(len({attempt["startedAt"] for attempt in comparable}) >= 2, "Blocked needs two independent matching failures")
            else:
                require(nonempty(record.get("cause")) and environmental_failure(latest["signature"], latest["launchError"]),
                        "Unverified requires a captured environmental cause")

    def check_stage_tools(self, stage, observed, tools):
        if stage in NODE_STAGES:
            node = "v" + (self.root / ".nvmrc").read_text().strip()
            npm = read_json(self.root / "probe/web/package.json")["packageManager"].removeprefix("npm@")
            require(tools.get("node") == node and tools.get("npm") == npm,
                    "The measured Node and npm executables differ from the version owners")
            if stage in ("frontend-assets", "typeid-exchange"):
                require(observed["nodeVersion"] == node and observed["npmVersion"] == npm,
                        "The secondary observation disagrees with the measured Node and npm executables")
        if stage == "frontend-image":
            owner = re.search(r'(?m)^pack = "([0-9.]+)"$', (self.root / "mise.toml").read_text())
            require(owner and tools.get("pack", "").partition("+")[0] == owner[1],
                    "The measured Pack executable differs from mise.toml")

    def check_pass_artifacts(self, stage, observed, artifacts):
        hashes = {item["sha256"] for item in artifacts.values()}
        if stage in ("frontend-fixture", "frontend-assets"):
            require(observed["lockfileSha256"] == file_sha(self.root / "probe/web/package-lock.json"), "Fixture lockfile fingerprint differs")
        if stage == "frontend-image":
            require(all(item["bodySha256"] in hashes for item in observed["responses"]), "Captured native HTTP response bytes are absent")
        if stage == "kdoc":
            require(observed["beforeSha256"] == file_sha(self.root / "probe/kdoc/Specimen.kt")
                    and observed["afterSha256"] in hashes, "The KDoc fixture or formatted bytes differ")
        if stage == "typeid-jvm":
            require(observed["kotlinOriginSha256"] in hashes, "JVM-origin exchange output is absent")
        if stage == "typeid-exchange":
            require({observed[key]["sha256"] for key in ("jvmToTs", "tsToJvm")} <= hashes,
                    "Both language-origin exchange files must be retained")
        if stage == "kotest":
            suites = [ET.parse(inside(self.directory, item["path"])).getroot()
                      for name, item in artifacts.items() if name.endswith(".xml")]
            cases = [case for suite in suites for case in suite.iter("testcase")]
            require(len(cases) == observed["testCount"]
                    and any(case.attrib["name"].split("(", 1)[0] == observed["junitCase"] for case in cases)
                    and all(not any(case.find(tag) is not None for tag in ("skipped", "error", "failure")) for case in cases),
                    "Kotest's supporting JUnit result does not match its claimed execution")

    def classify(self, stage, core, options):
        record = (self.load_stage(stage, core) if not options.prerequisite else
                  {**self.stage_metadata(stage, core), "attempts": [], "observations": {}})
        candidate = {key: value for key, value in record.items()
                     if key not in ("prerequisiteStage", "prerequisiteRecordSha256", "pendingCommand", "cause", "retry", "reason")}
        candidate.update(status=options.status)
        for attribute in ("cause", "retry", "reason"):
            value = getattr(options, attribute)
            if value:
                candidate[attribute] = value
        if options.prerequisite:
            require(options.pending_command and options.reason, "A prerequisite requires its cause and exact pending command")
            candidate.update(prerequisiteStage=options.prerequisite, pendingCommand=options.pending_command,
                             prerequisiteRecordSha256=file_sha(self.stage_path(options.prerequisite)))
        self.validate_record(stage, core, candidate)
        write_json(self.stage_path(stage), candidate)

    def check(self, stage, core):
        record = self.load_stage(stage, core)
        self.validate_record(stage, core, record)
        for group, stages in GROUPS.items():
            if stage in stages and all(self.stage_path(member).is_file() for member in stages):
                try:
                    records = [self.load_stage(member, core) for member in stages]
                    for member, entry in zip(stages, records):
                        self.validate_record(member, core, entry)
                except (OSError, ValueError, KeyError, TypeError):
                    continue
                status = next((entry["status"] for entry in records if entry["status"] != "Pass"), "Pass")
                write_json(self.directory / "secondary" / f"{group}.json", {
                    "runId": core["runId"], "coreTupleSha256": core["coreTupleSha256"],
                    "coreEvidenceSha256": core["coreEvidenceSha256"], "status": status, "stages": records,
                })
        print(f"{stage}: {record['status']}")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def capture(argv, root, env, timeout):
    try:
        with subprocess.Popen(argv, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding="utf-8", errors="replace", start_new_session=True) as process:
            try:
                output, _ = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                output, _ = process.communicate()
                output += "\nProcess timed out\n"
            return process.returncode, output, None
    except OSError as error:
        message = error.strerror or type(error).__name__
        return None, f"Launch error: {message}\n", message


def sanitize(output, root):
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    output = output.replace(str(root), "<repo>").replace(str(Path.home()), "<home>")
    output = re.sub(r"(https?://)[^/\s@]+:[^/\s@]+@", r"\1<redacted>@", output)
    output = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1<redacted>", output)
    return re.sub(r"(?i)((?:token|password|secret|authorization|api[_-]?key)[\"']?\s*[:=]\s*)[^\s,}]+",
                  r"\1<redacted>", output)


def diagnostic_signature(text, launch_error):
    if launch_error:
        return f"Launch error: {launch_error}"
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    causes = []
    if "* What went wrong:" in lines:
        for line in lines[lines.index("* What went wrong:") + 1:]:
            if line.startswith("* "):
                break
            causes.append(line.lstrip("> "))
    explicit = re.compile(r"\berror(?:\[[^]]+\])?:|\w(?:Error|Exception):|^Caused by:|^Process timed out$", re.I)
    causes = [line for line in causes if line and not GENERIC_FAILURE.fullmatch(line)]
    if not causes:
        causes = [line for line in lines if not GENERIC_FAILURE.fullmatch(line)
                  and (ENVIRONMENT_ERROR.search(line) or explicit.search(line))][:1]
    normalized = re.sub(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", "<id>", " | ".join(causes))
    return normalized if len(normalized) <= 400 else f"{normalized[:320]} [SHA-256 {sha(normalized.encode())}]"


def environmental_failure(signature, launch_error):
    return launch_error == "No such file or directory" or bool(ENVIRONMENT_ERROR.search(signature))


def stage_tools(stage, text):
    expected = ("node", "npm", "pack") if stage == "frontend-image" else ("node", "npm") if stage in NODE_STAGES else ()
    versions = {}
    for tool, version in re.findall(rf"(?m)^\s*PROBE_TOOL (node|npm|pack) ({TOOL_VERSION})[ \t]*$", text):
        if tool in expected:
            require(tool not in versions or versions[tool] == version, f"Conflicting {tool} versions in one stage")
            versions[tool] = version
    return versions


def validate_argv(stage, argv):
    require(isinstance(argv, list) and argv and all(nonempty(arg) for arg in argv), "Missing exact diagnostic command")
    task = STAGES[stage][0]
    if task == "npm":
        require((argv[0] == "npm" or argv[:2] in (["bash", "-c"], ["sh", "-c"]))
                and any("probe/web" in arg for arg in argv), f"Unexpected command for {stage}")
    else:
        require(argv[:2] == list(GRADLE) and task in argv and "--rerun-tasks" in argv, f"Unexpected command for {stage}")
        require(not any(arg in (":probe:integrationTest", ":probe:test", "build") for arg in argv),
                "The required Axon runtime and ordinary build have separate evidence")


def decode_observations(text, stage):
    prefix = "PROBE_SECONDARY "
    try:
        candidates = [json.loads(line.strip().removeprefix(prefix)) for line in text.splitlines()
                      if line.strip().startswith(prefix)]
    except ValueError:
        return {}
    matches = [value for value in candidates if isinstance(value, dict) and value.get("stage") == stage]
    return matches[0] if len(matches) == 1 else {}


def validate_observations(stage, observed, artifacts):
    paths = observed.get("artifacts", [])
    require(observed.get("stage") == stage and len(paths) == len(artifacts) and set(paths) == set(artifacts),
            f"Stage {stage} is missing its captured observation or supporting artifacts")
    require(artifacts and all(valid_sha(value) for value in artifacts.values()), "Pass requires measured supporting files")
    if stage == "frontend-fixture":
        markers = observed["markers"]
        require(len(markers) == 2 and all(nonempty(marker) for marker in markers) and len(set(markers)) == 2
                and observed["repeatIdentical"] is True and valid_sha(observed["lockfileSha256"]),
                "The static fixture needs two distinct markers, a reproducible build and an intact lockfile")
    elif stage == "frontend-assets":
        require(all(re.fullmatch(r"v?\d+\.\d+\.\d+", observed[key]) for key in ("nodeVersion", "npmVersion"))
                and valid_sha(observed["stagedSha256"]) and valid_sha(observed["lockfileSha256"])
                and observed["stagedTreeValidated"] is True, "Gradle assets lack tool, lockfile or staged-tree observations")
        require(artifacts.get("frontend-assets.html") == observed["stagedSha256"],
                "Staged HTML does not match its captured SHA-256")
    elif stage == "frontend-image":
        responses = observed["responses"]
        require(observed["architecture"] in ARCHITECTURES and len(responses) == 2
                and len({item["marker"] for item in responses}) == len({item["bodySha256"] for item in responses}) == 2
                and all(item["status"] == 200 and valid_sha(item["bodySha256"])
                        and item["bodySha256"] == item["sourceSha256"] for item in responses),
                "Two distinct native HTTP results must match their staged bytes")
    elif stage == "kotest":
        require(nonempty(observed["junitCase"]) and observed["testCount"] > 0 and type(observed["propertySeed"]) is int
                and observed["propertyChecks"] > 0, "Kotest must execute a named Jupiter test and seeded checks")
    elif stage == "kdoc":
        before, after, second = (observed[key] for key in ("beforeSha256", "afterSha256", "secondSha256"))
        require(all(map(valid_sha, (before, after, second))) and before != after == second
                and observed["contentPreserved"] is True, "KDoc must change once, preserve content and settle")
    elif stage == "typeid-jvm":
        require(observed["positiveVectors"] > 0 and observed["negativeVectors"] > 0
                and valid_sha(observed["kotlinOriginSha256"]), "Missing canonical JVM vectors or their exchange output")
    else:
        forward, reverse = (observed[key] for key in ("jvmToTs", "tsToJvm"))
        require(all(item["vectorCount"] > 0 and item["validatedBytesAndPrefix"] is True and valid_sha(item["sha256"])
                    for item in (forward, reverse)) and forward["sha256"] != reverse["sha256"],
                "TypeID must validate two independently produced exchanges")


def get_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ensure-core")
    commands.add_parser("self-test")
    run = commands.add_parser("run")
    run.add_argument("stage", choices=STAGES)
    run.add_argument("argv", nargs=argparse.REMAINDER)
    classify = commands.add_parser("classify")
    classify.add_argument("stage", choices=STAGES)
    classify.add_argument("status", choices=("Pass", "Blocked", "Unverified"))
    classify.add_argument("--reason")
    classify.add_argument("--cause")
    classify.add_argument("--retry")
    classify.add_argument("--prerequisite", choices=STAGES)
    classify.add_argument("--pending-command")
    check = commands.add_parser("check")
    check.add_argument("stage", choices=STAGES)
    return parser.parse_args(argv)


def main(argv=None, root=ROOT, directory=None):
    options = get_arguments(argv)
    try:
        if options.command == "self-test":
            self_test()
            return 0
        path = Path(directory or os.environ.get("PROBE_EVIDENCE_DIR", DEFAULT_DIR))
        store = Store(root, root / path, os.environ.get("PROBE_RUN_ID"))
        require(directory is not None or store.directory.is_relative_to((root / DEFAULT_DIR).resolve()),
                "Set PROBE_EVIDENCE_DIR within the ignored probe evidence directory")
        locks = root / "probe/build/reports/feasibility"
        locks.mkdir(parents=True, exist_ok=True)
        with (locks / ".verification.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            core = store.ensure_core()
            if options.command == "ensure-core":
                print(f"Core proof {core['runId']} verified ({core['coreEvidenceSha256']})")
            elif options.command == "run":
                # argparse removes the "--" delimiter before REMAINDER on some Python versions.
                store.run_stage(options.stage, core, options.argv[1:] if options.argv[:1] == ["--"] else options.argv)
            elif options.command == "classify":
                store.classify(options.stage, core, options)
            else:
                store.check(options.stage, core)
        return 0
    except (OSError, AttributeError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        print(f"Evidence verification failed: {error}", file=sys.stderr)
        return 1


def fixture_core(directory, feature, image_pin):
    run_id = "self-test-core"
    child = {"architecture": "arm64", "javaVendor": "Eclipse Adoptium", "javaVersion": f"{feature}.0.1+2",
             "javaFeature": feature, "engine": "test.AxonServerEventStorageEngine",
             "commandBus": "test.DistributedCommandBus", "queryBus": "test.DistributedQueryBus"}
    worker, writer, projection = ({**child, "pid": i, "clientId": name}
                                  for i, name in enumerate(("driver", "command", "projection"), 1))
    cleanup = {"containerRemoved": True, "containerId": "1" * 64, "exitedPids": [2, 3], "cancelledSubscriptions": 1,
               "timingsMs": {"serverReadyMs": 20_000, "cleanupMs": 333}}
    receipt = {"eventId": "winner", "role": writer, "runId": run_id}
    base = {"runId": run_id, "courseId": "course", "role": projection, "processorReady": True}
    before = {**base, "eventId": None, "enrollments": 0}
    after = {**base, "eventId": "winner", "enrollments": 1}
    core = {
        "test": "probe.AxonProbeTest." + CASES["PROBE_CORE"], "runId": run_id,
        "startedAt": "2026-01-01T00:00:20Z", "finishedAt": "2026-01-01T00:00:32Z",
        "context": "default", "dcb": True, "credentialFree": True, "initialEvents": 0, "marker": 0,
        "worker": worker, "command": writer, "projection": projection,
        "registeredClients": {"driver": "D", "command": "C", "projection": "P"},
        "receipt": receipt, "courseId": "course", "studentId": "winner-student", "losingStudentId": "loser-student",
        "losingEventId": "loser", "before": before, "initial": before, "update": after, "after": after,
        "rejection": {"type": "AppendEventsTransactionRejectedException", "status": "CANCELLED",
                      "serverReason": "ConsistencyConditionException"},
        "tagReads": {**{key: ["winner"] for key in ("course", "winnerStudent", "courseAndStudent", "history")}, "loserStudent": []},
        "cleanup": cleanup,
    }
    tracer = {"test": "probe.AxonProbeTest." + CASES["PROBE_TRACER"], "runId": "tracer",
              "initialEvents": 0, "courseEventId": "winner", "studentEventId": "winner", "receipt": receipt}
    forced = {"test": "probe.AxonProbeTest." + CASES["PROBE_CLEANUP"], "runId": "forced", "initialEvents": 0,
              "cleanup": {**cleanup, "containerId": "2" * 64}, "unrelatedNetworkPreserved": True,
              "reason": "controlled failure after subscription startup"}
    images = {
        "runId": run_id, "index": image_pin, "daemon": "linux/arm64", "daemonVersion": "1", "runningArchitecture": "arm64",
        "arm64": {"architecture": "arm64", "digest": "sha256:" + "3" * 64, "config": "sha256:" + "4" * 64},
        "amd64": {"architecture": "amd64", "digest": "sha256:" + "5" * 64, "config": "sha256:" + "6" * 64},
        "runningImageId": "sha256:" + "4" * 64,
    }
    for name, record in zip(CORE_FILES, (core, tracer, forced, images)):
        write_json(directory / name, record)
    suite = ET.Element("testsuite", name="probe.AxonProbeTest", errors="0", failures="0", skipped="0",
                       tests="3", timestamp="2026-01-01T00:00:00Z")
    for name in CASES.values():
        ET.SubElement(suite, "testcase", name=name + "()", classname="probe.AxonProbeTest")
    ET.SubElement(suite, "system-out").text = "\n".join(
        f"{marker} {json.dumps(record)}" for marker, record in zip(CASES, (tracer, core, forced))
    )
    ET.ElementTree(suite).write(directory / "integration-junit.xml", encoding="utf-8")


def self_test():
    for fraction, micros in (("", 0), (".123", 123000), (".123456", 123456), (".123456789", 123456)):
        require(instant(f"2026-01-01T00:00:00{fraction}Z").microsecond == micros,
                "The verifier must accept Java Instant precision on Python 3.9")
    with tempfile.TemporaryDirectory(prefix="probe-evidence-check-") as path:
        root = Path(path).resolve()
        evidence = root / "evidence"
        program = Path(__file__).resolve()
        script = (
            "import pathlib,runpy,sys;"
            "cli=runpy.run_path(sys.argv[1]);"
            "raise SystemExit(cli['main'](sys.argv[4:],root=pathlib.Path(sys.argv[2]),directory=sys.argv[3]))"
        )
        env = {key: value for key, value in os.environ.items() if key not in ("PROBE_EVIDENCE_DIR", "PROBE_RUN_ID")}

        def fixture_file(name, content):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return target

        def invoke(*args, expected=0, result=None, message=None):
            p = subprocess.run([sys.executable, "-c", script, str(program), str(root), str(evidence), *args],
                               env={**env, "EVIDENCE_TEST_RESULT": result or ""}, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            require(p.returncode == expected and (message is None or message in p.stdout),
                    f"self-test {args}: expected exit {expected}, got {p.returncode}: {p.stdout.strip()}")

        feature = 25
        image_pin = "axoniq/axonserver:1@sha256:" + "a" * 64
        fixture_file(".java-version", f"{feature}\n")
        fixture_file("gradle/libs.versions.toml", f'axon-server-image = "{image_pin}"\n' +
                     "".join(f'{key} = "1"\n' for key in ("axon", "axoniq", "kotlin", "spring-boot", "junit")))
        fixture_file("gradle/wrapper/gradle-wrapper.properties", "distributionUrl=gradle-9.9.2-bin.zip\n")
        fixture_file("probe/build.gradle.kts", "\n".join(task.split(":")[-1] for task, _ in STAGES.values()))
        for _, files in STAGES.values():
            for name in files:
                fixture_file(name, "selected fixture input\n")
        fixture_file(".nvmrc", "26.13.1\n")
        fixture_file("probe/web/package.json", '{"packageManager":"npm@12.2.3"}\n')
        fixture_file("gradlew", """#!/bin/sh
case "$2:$EVIDENCE_TEST_RESULT" in
  :probe:integrationTest:*) echo 'Required tuple failed'; exit 42 ;;
  *:pass) cat evidence/observed.txt ;;
  *:blocked) echo 'error: selected tooling fixture failed'; exit 7 ;;
  *:unverified) echo 'error: could not resolve host'; exit 8 ;;
  *:missing-fixture) echo 'error: specimen.kt: No such file or directory'; exit 8 ;;
  *:first-cause|*:second-cause)
    printf '> Task %s FAILED\n\n* What went wrong:\nExecution failed for task %s.\n> %s\n' \
      "$2" "$2" "$EVIDENCE_TEST_RESULT"
    exit 7 ;;
esac
""").chmod(0o700)

        proof = evidence / "known-good"
        fixture_core(proof, feature, image_pin)
        store = Store(root, evidence)
        write_json(store.provenance, store.describe_core(proof))
        formatted = fixture_file("evidence/formatted.kt", "example\n")
        specimen = file_sha(root / "probe/kdoc/Specimen.kt")
        fixture_file("evidence/observed.txt", "PROBE_SECONDARY " + json.dumps({
            "stage": "kdoc", "artifacts": ["formatted.kt"], "beforeSha256": specimen,
            "afterSha256": file_sha(formatted), "secondSha256": file_sha(formatted), "contentPreserved": True,
        }) + "\n")

        def run(stage, outcome):
            invoke("run", stage, "--", *GRADLE, STAGES[stage][0], "--rerun-tasks", result=outcome)

        run("kdoc", "pass")
        invoke("classify", "kdoc", "Pass")
        invoke("check", "kdoc")
        run("kotest", "blocked")
        invoke("classify", "kotest", "Blocked", "--reason", "Fixture failed", "--retry", "Change the formatter",
               expected=1, message="two independent matching failures")
        run("kotest", "blocked")
        invoke("classify", "kotest", "Blocked", "--reason", "Fixture failed", "--retry", "Re-run with the corrected tool")
        invoke("check", "kotest")
        run("kotest", "first-cause")
        run("kotest", "second-cause")
        invoke("classify", "kotest", "Blocked", "--reason", "Fixture failed", "--retry", "Re-run the same task",
               expected=1, message="two independent matching failures")
        run("kotest", "blocked")
        invoke("classify", "kotest", "Blocked", "--reason", "Fixture failed", "--retry", "Re-run with the corrected tool")
        run("typeid-jvm", "unverified")
        invoke("classify", "typeid-jvm", "Unverified", "--cause", "Registry DNS unavailable", "--retry", "Retry once DNS works")
        invoke("check", "typeid-jvm")
        invoke("classify", "typeid-exchange", "Unverified", "--prerequisite", "typeid-jvm",
               "--pending-command", "./gradlew --console=plain :probe:typeIdProbe --rerun-tasks",
               "--reason", "Kotlin-origin exchange cannot be generated", "--retry", "Retry once DNS works")
        invoke("check", "typeid-exchange")
        run("typeid-jvm", "missing-fixture")
        invoke("classify", "typeid-jvm", "Unverified", "--cause", "Missing input", "--retry", "Restore the file",
               expected=1, message="captured environmental cause")
        record = read_json(store.stage_path("typeid-exchange"))
        write_json(store.stage_path("typeid-exchange"), {**record, "prerequisiteStage": "typeid-exchange"})
        invoke("check", "typeid-exchange", expected=1, message="prerequisite")
        record = read_json(store.stage_path("kdoc"))
        write_json(store.stage_path("kdoc"), {**record, "status": "Skipped"})
        invoke("check", "kdoc", expected=1, message="no supported classification")
        write_json(store.stage_path("kdoc"), record)
        snapshot = record["attempts"][-1]["artifacts"]["formatted.kt"]["path"]
        fixture_file(f"evidence/{snapshot}", "tampered\n")
        invoke("check", "kdoc", expected=1, message="supporting artifact was changed")

        html = fixture_file("evidence/frontend-assets.html", "<p>fixture</p>\n")
        observed = {"stage": "frontend-assets", "artifacts": [html.name], "nodeVersion": "v26.13.1",
                    "npmVersion": "12.2.3", "stagedTreeValidated": True, "stagedSha256": "0" * 64,
                    "lockfileSha256": file_sha(root / "probe/web/package-lock.json")}
        fixture_file("evidence/observed.txt", "PROBE_TOOL node v26.13.1\nPROBE_TOOL npm 12.2.3\n"
                     "PROBE_SECONDARY " + json.dumps(observed) + "\n")
        run("frontend-assets", "pass")
        invoke("classify", "frontend-assets", "Pass", expected=1, message="Staged HTML")
        observed["stagedSha256"] = file_sha(html)
        fixture_file("evidence/observed.txt", "PROBE_TOOL node v26.13.1\nPROBE_TOOL npm 12.2.3\n"
                     "PROBE_SECONDARY " + json.dumps(observed) + "\n")
        run("frontend-assets", "pass")
        invoke("check", "frontend-assets")
        record = read_json(store.stage_path("frontend-assets"))
        record["attempts"][-1]["toolVersions"]["node"] = "v24.20.0"
        write_json(store.stage_path("frontend-assets"), record)
        invoke("check", "frontend-assets", expected=1, message="tool versions differ")

        fixture_file("probe/kdoc/Specimen.kt", "changed input\n")
        invoke("check", "kdoc", expected=1, message="evidence is stale")
        (proof / "integration-junit.xml").write_text("<testsuite failures='1'/>")
        invoke("check", "kotest", expected=1, message="Required native Axon proof is invalid")
    print("Secondary verifier self-test passed")


if __name__ == "__main__":
    raise SystemExit(main())
