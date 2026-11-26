---
phase: quick-261126-jsl
plan: "01"
subsystem: build-tooling
tags: [intellij-idea, gradle, qodana, inspections, git]
requires:
  - phase: quick-261126-jp0
    provides: Ordinary Qodana baseline with Spring and Axon entry-point recognition
provides:
  - IntelliJ IDEA project profile that excludes the Gradle incubation annotation
  - Ordinary Qodana archive with independent Gradle diagnostics
affects: [local-quality-checks, maintainer-guide]
tech-stack:
  added: []
  patterns: [IntelliJ IDEA project inspection profile, Git export-ignore]
key-files:
  created:
    - .idea/inspectionProfiles/Project_Default.xml
    - .gitattributes
  modified:
    - .gitignore
    - docs/maintainer-guide.md
key-decisions:
  - Retain the native Project Default profile in Git checkouts and exclude it from revision archives with an exact export-ignore rule.
requirements-completed: [QA-07]
commits: 3
plan_head_before: a06795cbfc0e56123d657c6a8eb4357dae45e095
plan_head_after: fff0b35755676ab15867460b8e0bb73449f9b2c8
actuals:
  tokens: 1204
  tasks: 2
  commits: 3
duration: 16m
completed: "2026-11-26"
status: complete
---

# Reduce Gradle incubation warnings in IntelliJ IDEA

The shared **Project Default** profile removes `org.gradle.api.Incubating` from `UnstableApiUsage`. Native IntelliJ IDEA and pinned Qodana controls both went from 97 Gradle findings to zero while continuing to report both Guava `@Beta` diagnostics. The ordinary Qodana scan on the delivery retained all 51 findings from its warm baseline.

## Native profile verification

The installed IntelliJ IDEA Ultimate 2026.3 build `IU-263.7307.200` bundles ten unstable API annotation names in `StaticAnalysisAnnotationManager`. The candidate retains nine in their bundled order and leaves the inspection enabled at `WARNING`. Both scratch copies were extracted from `b838a25320cdce2b3655d64a9026e1747e338486` and received the same cataloged Guava 33.8.0-android dependency and Kotlin control. The baseline retains the Gradle annotation. [Inspectopedia defaults](https://www.jetbrains.com/help/inspectopedia/UnstableApiUsage.html)

The first offline invocation on the bare baseline reported `This project contains no modules. Inspection cannot proceed.` Opening the candidate directly analyzed files without a Gradle model. The installed `warmup --project-dir=<copy> --configure-project=true` starter performed Gradle 9.9.2 import with Temurin 25. The initial candidate warmup reached successful model import before timing out during indexing. A fresh candidate seeded with only the tracked IDEA profile completed import and indexing with 243,723 indexed files. Its generated `gradle.xml` matched the warmed baseline byte for byte and linked the root, included `build-logic`, and the `bff`, `docs-site`, `fixtures`, `probe`, and `web` projects. Each run used isolated IDEA configuration, plugins, system and log directories.

The post-import `inspect.sh -v2` runs selected the XML profiles explicitly and analyzed the Gradle scripts and `axon5-dcb-courses.probe.main`. The XML comparison counted 52 authored and 45 generated Gradle findings in the baseline, with zero in the candidate. Both reports had the following identical `UnstableApiUsage` findings at `probe/src/main/kotlin/probe/UnstableApiControl.kt:5`.

- `'com.google.common.hash.Funnels' is marked unstable with @Beta`
- `'byteArrayFunnel()' is declared in unstable class 'com.google.common.hash.Funnels' marked with @Beta`

The native evidence covers clean Gradle import and explicit batch inspection. Live editor profile selection remains unverified. The maintainer guide describes how to select the shared project profile or apply the same edit to a custom project profile. [Maintainer guide](../../../docs/maintainer-guide.md#intellij-idea-inspection-profile)

## Qodana controls and ordinary scan

The scratch launcher copies changed only the profile selection to explicit XML paths. Both used the catalog-pinned Linux ARM64 Qodana Community for JVM 2026.3 (`QDJVM-263.8362`), Temurin 25, Gradle 9.9.2 and Axon Framework 0.10.1. Each completed a full Gradle import with a byte-identical 20-module report. Both SARIF reports have `configProfile: path`, `executionSuccessful: true`, and the same two Guava findings at line 5. The baseline has 97 Gradle findings and the candidate has zero.

The execution base `a06795cbfc0e56123d657c6a8eb4357dae45e095` differs from the Spring source commit `b838a25320cdce2b3655d64a9026e1747e338486` only in planning records, so the Spring task's warm and fresh reports supply the ordinary baselines. The final ordinary scan ran the unmodified launcher on `fff0b35755676ab15867460b8e0bb73449f9b2c8`. It synchronized the warm workspace into a fresh archived snapshot. Its SARIF identifies the recommended profile, successful execution and the same 20-module structure as the warm baseline. The launcher, image pin, Java feature, plugin declaration and Spring entry-point XML all match the baseline. [Spring verification](../261126-jp0-recognize-spring-bean-entry-points-in-qo/261126-jp0-SUMMARY.md)

The final and warm baseline findings matched by rule, path, line, column, highlighted token and diagnostic text. Of the 51 results, 35 cover the JVM Test Suites, 12 configuration roles, two the fixture build-tree path and two centralized repositories. Both have zero non-Gradle results and one separate existing `sanityFailure` for the generated `build-logic/build/pluginUnderTestMetadata` root in `build-logic.test`. The fresh Spring source scan observed one extra finding at the unchanged `suites` call at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:24`. The message names `getSuites()` and `org.gradle.testing.base.TestingExtension`.

### Local evidence

The native runs save `UnstableApiUsage.xml` below `.gradle/idea-inspection/261126-jsl/native-baseline-results/` and `.gradle/idea-inspection/261126-jsl/native-fresh-candidate-results/`. Their paired warmup and inspection logs are in the same scratch root. The Qodana result directories contain SARIF, HTML, `projectStructure/Modules.json`, and `log/idea.log`. Sibling `revision` files match the SHAs in their paths.

- Explicit baseline `.gradle/idea-inspection/261126-jsl/docker/baseline/.gradle/qodana/runs/cffdef73c8de3c5a5c28e9a87bed5be3f2c5a678.fQdu99/results/`
- Explicit candidate `.gradle/idea-inspection/261126-jsl/docker/candidate/.gradle/qodana/runs/3befab82745d2534198c6dfb9d3c03adf69581fe.I1u3rr/results/`
- Ordinary warm baseline `.gradle/qodana/runs/b838a25320cdce2b3655d64a9026e1747e338486.OYcBZO/results/`
- Ordinary fresh baseline `.gradle/qodana/runs/b838a25320cdce2b3655d64a9026e1747e338486.cItRLV/results/`
- Ordinary scan with the profile seeded in the archive `.gradle/qodana/runs/e434f250f5e3d729f789de1cb4dae2a5871080df.aLTXc4/results/`
- Ordinary final scan `.gradle/qodana/runs/fff0b35755676ab15867460b8e0bb73449f9b2c8.mBmOjq/results/`

## Deviations from plan

**[Rule 1 - Bug] Exclude the editor profile from revision archives.** The ordinary scan of `e434f25` saw the shared IDEA file and produced zero findings despite reporting the recommended profile, successful execution and the same module structure. Commit `fff0b35` uses Git's built-in `export-ignore` for the exact profile path. The committed archive excludes exactly that tracked file, and the profile remains available in Git checkouts. Qodana cached the seeded profile, so the byte-matched test copy was moved into the scratch evidence directory before the final ordinary run. The scan then reproduced every warm baseline result. [Git archive attributes](https://git-scm.com/docs/git-archive#_attributes)

## Repository checks

The committed `.idea` tree contains only `inspectionProfiles/Project_Default.xml`. Git ignores `workspace.xml`, `gradle.xml`, the IDE-generated `.gitignore`, sibling profiles, `profiles_settings.xml` and nested private paths. The exact tracked profile passed a byte comparison with the native test input. The checked-in pre-commit hook, `git diff --check`, and `mise exec python ruff taplo -- ./gradlew --console=plain styleCheck :docs-site:check` passed. The final docs check ran 14 tests.

## Task commits

- `0fd29a0` adds the qualified IntelliJ IDEA profile and narrow Git allowlist.
- `e434f25` documents project inspection profile selection.
- `fff0b35` excludes the single editor profile from revision archives and documents the effect.

## Self-Check: PASSED
