"""Reproduce the public dependency observations in the maintainer guide."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
GUAVA = "com.google.guava:guava"
DRIVER = "org.postgresql:postgresql"
BOM = "org.springframework.boot:spring-boot-dependencies"
RUNTIME = ("compileClasspath", "runtimeClasspath")
UNIT = ("testCompileClasspath", "testRuntimeClasspath")
INTEGRATION = ("integrationTestCompileClasspath", "integrationTestRuntimeClasspath")
COMPONENT = ("componentTestCompileClasspath", "componentTestRuntimeClasspath")
CONFIGURATIONS = {
    ":bff": (*RUNTIME, *UNIT, *COMPONENT, "ktfmtTool", "detektCommentsTool"),
    ":probe": (
        *RUNTIME,
        *UNIT,
        *INTEGRATION,
        "kdocFormatter",
        "kotestProbeRuntimeClasspath",
        "typeIdJvmVectorsRuntimeClasspath",
    ),
}
ANDROID = {f":probe:{name}" for name in (*RUNTIME, *UNIT, *INTEGRATION)}
FORMATTERS = {":bff:ktfmtTool", ":probe:kdocFormatter"}
BFF = {f":bff:{name}" for name in (*RUNTIME, *UNIT, *COMPONENT)}
TESTS = (
    ":bff:test",
    ":bff:componentTest",
    ":bff:verifyFixtureIsolation",
    ":bff:ktfmtCheck",
    ":probe:test",
    ":probe:kdocProbe",
)

# Use Gradle's report tasks and resolution model against the same configurations. Files stay
# inside the disposable snapshot, and the command prints only the targeted public findings.
INIT_SCRIPT = """\
import groovy.json.JsonOutput
import org.gradle.api.artifacts.result.ResolvedDependencyResult
import org.gradle.api.tasks.diagnostics.DependencyInsightReportTask
import org.gradle.api.tasks.diagnostics.DependencyReportTask

gradle.projectsEvaluated {
    if (gradle.parent != null) return
    def root = gradle.rootProject
    def scopes = __SCOPES__
    def reports = []
    scopes.each { path, names ->
        def project = root.project(path)
        names.each { name ->
            def classpath = project.configurations.getByName(name)
            def suffix = name.capitalize()
            reports << project.tasks.register("publicDependencies${suffix}", DependencyReportTask) {
                configurations = [classpath] as Set
            }
            reports << project.tasks.register("publicDependencyInsight${suffix}", DependencyInsightReportTask) {
                configuration = classpath
                showingAllVariants.set(false)
                setDependencySpec("com.google.guava:guava")
            }
        }
    }
    root.tasks.register("publicDependencyEvidence") {
        dependsOn(reports)
        doLast {
            def graphs = [:]
            scopes.each { path, names ->
                def project = root.project(path)
                names.each { name ->
                    def graph = project.configurations.getByName(name).incoming.resolutionResult
                    def components = graph.allComponents.collectEntries { component ->
                        [(component.id.displayName): [
                            variants: component.variants*.displayName.sort(),
                            reasons: component.selectionReason.descriptions*.description.sort(),
                        ]]
                    }
                    def edges = graph.allDependencies.collect { edge ->
                        if (!(edge instanceof ResolvedDependencyResult)) {
                            throw new GradleException("A public dependency did not resolve in ${path}:${name}")
                        }
                        [
                            edge.from.id.displayName,
                            edge.requested.displayName,
                            edge.selected.id.displayName,
                            edge.constraint,
                            edge.resolvedVariant.displayName,
                        ]
                    }
                    graphs["${path}:${name}"] = [components: components, edges: edges]
                }
            }
            def boot = root.extensions.getByName("versionCatalogs").named("libs")
                .findVersion("spring-boot").get().requiredVersion
            def bff = root.project(":bff")
            def pom = bff.configurations.detachedConfiguration(
                bff.dependencies.create("org.springframework.boot:spring-boot-dependencies:${boot}@pom")
            )
            pom.transitive = false
            new File(root.rootDir, "boot-dependencies.pom").bytes = pom.singleFile.bytes
            new File(root.rootDir, "public-graphs.json").text = JsonOutput.toJson(graphs)
        }
    }
}
"""

# The historical baseline removes just the ordinary Guava constraints. The catalogue,
# plugins, platform imports, source code and all controls stay at this checkout's versions.
BOUNDS = {
    "probe/build.gradle.kts": (
        "implementation(libs.guava.android)",
        "add(kdocFormatterImplementation.name, libs.guava.jre)",
    ),
    "build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts": (
        'add(ktfmtDependencies.name, catalog.findLibrary("guava-jre").get())',
    ),
}


class EvidenceError(Exception):
    """The current public selections disagree with the published evidence."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def invoke(args, directory, *, env=None, timeout=240):
    result = subprocess.run(
        args,
        cwd=directory,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
        check=False,
        env=env,
    )
    if result.returncode:
        # Gradle and npm output can contain environment-specific details. Keep the diagnostic
        # targeted and use the published commands for local investigation.
        raise EvidenceError(
            f"{Path(args[0]).name} exited {result.returncode} during {' '.join(args[1:])}"
        )
    return result.stdout


def snapshot_sources(directory):
    paths = invoke(
        [
            "git",
            "ls-files",
            "-z",
            "--",
            "build.gradle.kts",
            "settings.gradle.kts",
            "gradle.properties",
            "gradlew",
            ".java-version",
            ".nvmrc",
            "gradle",
            "build-logic",
            "bff",
            "fixtures",
            "probe",
            "web",
            "docs-site",
            "config",
            "tools/style",
        ],
        ROOT,
    ).split("\0")
    for name in filter(None, paths):
        source = ROOT / name
        require(
            source.is_file() and not source.is_symlink(),
            f"Invalid public build input {name}",
        )
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    scopes = json.dumps(CONFIGURATIONS).replace("{", "[", 1).removesuffix("}") + "]"
    (directory / "public-evidence.init.gradle").write_text(
        INIT_SCRIPT.replace("__SCOPES__", scopes), encoding="utf-8"
    )


def gradle(directory, label, *tasks, offline):
    command = [
        "./gradlew",
        "--console=plain",
        *(["--offline"] if offline else []),
        *tasks,
    ]
    print(label, flush=True)
    return invoke(
        command, directory, env={**os.environ, "DOCKER_HOST": "tcp://127.0.0.1:1"}
    )


def read_graphs(directory, label, *, offline):
    output = gradle(
        directory,
        f"{label}: full Gradle graphs and dependencyInsight",
        "--init-script",
        "public-evidence.init.gradle",
        "publicDependencyEvidence",
        offline=offline,
    )
    graphs = json.loads((directory / "public-graphs.json").read_text(encoding="utf-8"))
    for name in graphs:
        configuration = name.split(":")[-1]
        suffix = configuration[0].upper() + configuration[1:]
        require(
            f"{name.removesuffix(configuration)}publicDependencyInsight{suffix}"
            in output,
            f"Missing dependencyInsight for {name}",
        )
        require(
            f"{name.removesuffix(configuration)}publicDependencies{suffix}" in output,
            f"Missing dependency report for {name}",
        )
    return graphs


def without_bounds(directory, original):
    for name, declarations in BOUNDS.items():
        source = original[name]
        for declaration in declarations:
            pattern = rf"(?m)^([ ]+){re.escape(declaration)} \{{\n(?:(?!\1\}}\n)[^\n]*\n)*\1\}}\n"
            source, count = re.subn(pattern, "", source)
            require(
                count == 1, f"Expected one scoped constraint in {name}: {declaration}"
            )
        (directory / name).write_text(source, encoding="utf-8")


def selection(graph, coordinate):
    found = [
        name.rsplit(":", 1)[-1]
        for name in graph["components"]
        if name.startswith(coordinate + ":")
    ]
    require(len(found) <= 1, f"Multiple selections for {coordinate}")
    return found[0] if found else None


def verify_selection(graphs, name, coordinate, expected):
    observed = selection(graphs[name], coordinate)
    require(
        observed == expected,
        f"{name} selected {coordinate} {observed or 'absent'}, expected {expected or 'absent'}",
    )


def verify_incoming(graph, version, paths, *, constrained):
    coordinate = f"{GUAVA}:{version}"
    incoming = {
        edge[0] for edge in graph["edges"] if edge[2] == coordinate and not edge[3]
    }
    for path in paths:
        require(
            any(edge.startswith(path) for edge in incoming),
            f"Missing incoming edge {path} for {coordinate}",
        )
    # A constraint edge is distinct from a direct production dependency.
    require(
        any(edge[2] == coordinate and edge[3] for edge in graph["edges"])
        == constrained,
        f"Unexpected constraint edges for {coordinate}",
    )
    reasons = graph["components"][coordinate]["reasons"]
    require(
        any("GHSA-xxph-c9ww-hj94" in reason for reason in reasons) == constrained,
        f"Unexpected selection reason for {coordinate}",
    )


def compare(checked_in, baseline):
    for name in sorted(checked_in):
        current, earlier = checked_in[name], baseline[name]
        if name in ANDROID:
            expected = ("33.8.0-android", "33.6.0-android")
            incoming = ("io.grpc:grpc-stub:1.84.1",)
            if name.endswith(("runtimeClasspath", "RuntimeClasspath")):
                incoming += ("io.grpc:grpc-api:1.84.1",)
        elif name in FORMATTERS:
            expected = ("33.8.0-jre", "33.5.0-jre")
            incoming = (
                "org.jetbrains.kotlinx:ktfmt:0.65",
                "com.google.googlejavaformat:google-java-format:1.23.0",
            )
        else:
            require(current == earlier, f"Control graph changed: {name}")
            print(
                f"{name}: control graph unchanged; Guava {selection(current, GUAVA) or 'absent'}"
            )
            continue
        for graph, version, constrained in zip(
            (current, earlier), expected, (True, False), strict=True
        ):
            verify_selection({name: graph}, name, GUAVA, version)
            verify_incoming(graph, version, incoming, constrained=constrained)
        before = set(earlier["components"])
        after = set(current["components"])
        changed = {component.rsplit(":", 1)[0] for component in before ^ after}
        require(
            GUAVA in changed
            and changed
            <= {
                GUAVA,
                "com.google.errorprone:error_prone_annotations",
                "org.jspecify:jspecify",
            },
            f"Unexpected selected-component changes in {name}: {sorted(changed)}",
        )
        print(
            f"{name}: {expected[1]} -> {expected[0]}; changed {', '.join(sorted(changed))}"
        )


def verify_driver_metadata(directory, graphs):
    pom = ElementTree.parse(directory / "boot-dependencies.pom").getroot()
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    require(
        pom.findtext("m:version", namespaces=ns) == "4.2.0"
        and pom.findtext("m:properties/m:postgresql.version", namespaces=ns)
        == "42.7.14",
        "Unexpected Boot 4.2.0 pgJDBC metadata",
    )
    for name in sorted(ANDROID | BFF):
        verify_selection(graphs, name, DRIVER, None)
        verify_selection(graphs, name, BOM, "4.2.0")
    print(
        "Boot 4.2.0 POM: pgJDBC 42.7.14 metadata; pgJDBC absent in the application and probe graphs"
    )


def verify_guide():
    guide = (ROOT / "docs/maintainer-guide.md").read_text(encoding="utf-8")
    for marker in (
        "2026-11-24",
        "2026-11-25",
        "2026-12-01",
        "2026-12-02",
        "01-13-PLAN.md#b17-reference-scoped-transitive-review",
        "01-09-PLAN.md#b8-reference-private-jvm-advisory-check",
        "/feasibility/phase-01/#dependency-and-image-review",
        "33.8.0-android",
        "33.8.0-jre",
        "42.7.14",
        "42.7.15",
        "B8 status: incomplete",
        "`:bff:runtimeClasspath`",
        "`:probe:testRuntimeClasspath`",
        "`:probe:integrationTestRuntimeClasspath`",
        "authorized external local directory",
        "High or Critical",
        "unrated",
    ):
        require(marker in guide, f"Missing evidence in maintainer guide: {marker}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use already cached public Gradle artifacts.",
    )
    parser.add_argument(
        "--expect-bff-runtime-guava",
        choices=["0.0.0"],
        help="Supply an intentionally false public graph expectation to verify nonzero exit.",
    )
    args = parser.parse_args()
    try:
        verify_guide()
        with TemporaryDirectory(prefix="courses-public-dependencies-") as work:
            directory = Path(work)
            snapshot_sources(directory)
            current = read_graphs(directory, "Checked-in", offline=args.offline)
            verify_selection(
                current, ":bff:runtimeClasspath", GUAVA, args.expect_bff_runtime_guava
            )
            for name in BFF:
                verify_selection(current, name, GUAVA, None)
            verify_driver_metadata(directory, current)
            gradle(
                directory,
                "Checked-in: BFF, probe unit and formatter checks",
                *TESTS,
                offline=args.offline,
            )
            original = {
                name: (directory / name).read_text(encoding="utf-8") for name in BOUNDS
            }
            without_bounds(directory, original)
            baseline = read_graphs(
                directory, "Without Guava bounds", offline=args.offline
            )
            compare(current, baseline)
            gradle(
                directory,
                "Without bounds: repeat targeted checks",
                *TESTS,
                offline=args.offline,
            )
            for name, contents in original.items():
                (directory / name).write_text(contents, encoding="utf-8")
            restored = read_graphs(directory, "Restored bounds", offline=args.offline)
            require(
                current == restored,
                "Restored public graph differs from the checked-in graph",
            )
            gradle(
                directory,
                "Restored: repeat targeted checks",
                *TESTS,
                offline=args.offline,
            )
    except (EvidenceError, OSError, subprocess.TimeoutExpired, ValueError) as error:
        print(f"Public dependency evidence failed: {error}", file=sys.stderr)
        return 1
    print("Public dependency evidence passed. B8 status: incomplete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
