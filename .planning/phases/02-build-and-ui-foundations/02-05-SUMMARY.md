---
phase: 02-build-and-ui-foundations
plan: "05"
subsystem: build
tags: [gradle, kotlin, kdoc, ktfmt, detekt, dokka, test-fixtures]
requires:
  - phase: 02-02
    provides: Shared Kotlin JVM convention, BFF test suites, and fixture producer
  - phase: 02-10
    provides: Root Gradle lifecycle connected to the BFF verification tasks
provides:
  - Check-only Kotlin formatting and comments tasks for BFF and fixtures
  - Dokka HTML publication that fails on warnings in the BFF and fixture API source sets
  - Shared ktfmt and detekt command prefixes for repository-wide style tooling
  - Disposable positive, negative, and repair checks for all three tools
affects: [02-07, 02-08, 02-09, 03]
tech-stack:
  added: [detekt CLI 1.23.8, Dokka Gradle plugin 2.3.0]
  patterns: [isolated formatter and analyzer classpaths, source-set-aware Kotlin checks, warning-failing Dokka publication, disposable quality controls]
key-files:
  created:
    - build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts
    - config/detekt/comments.yml
    - tools/check_kotlin_quality.py
  modified:
    - gradle/libs.versions.toml
    - build-logic/build.gradle.kts
    - bff/build.gradle.kts
    - bff/src/main/kotlin/courses/bff/BffApplication.kt
    - fixtures/build.gradle.kts
    - fixtures/src/testFixtures/kotlin/courses/fixtures/DirectoryFixtures.kt
key-decisions:
  - "Share Kotlin formatting and comments commands through the JVM convention and scope the Guava JRE floor to ktfmtTool."
  - "Publish BFF main and public fixture helpers from testFixtures with reportUndocumented and failOnWarning enabled."
patterns-established:
  - "`kotlinQualityRuntime` writes the same tool prefixes used by the module checks for repository tooling."
  - Disposable controls assert task results and named diagnostics before testing repairs.
requirements-completed: [QA-07, QA-08, FND-02]
coverage:
  - id: D1
    description: ktfmt rejects unformatted Kotlin and preserves KDoc content across two formatting passes.
    requirement: QA-07
    verification:
      - kind: integration
        ref: "python3 tools/check_kotlin_quality.py format-comments"
        status: pass
    human_judgment: false
  - id: D2
    description: detekt comments rules catch missing sentence punctuation in production, fixture, and Gradle Kotlin DSL code.
    requirement: QA-07
    verification:
      - kind: integration
        ref: "python3 tools/check_kotlin_quality.py format-comments"
        status: pass
    human_judgment: false
  - id: D3
    description: Both Dokka publications fail on an undocumented declaration and generate HTML after its KDoc is repaired.
    requirement: QA-07
    verification:
      - kind: integration
        ref: "python3 tools/check_kotlin_quality.py publication"
        status: pass
      - kind: integration
        ref: "./gradlew --console=plain :bff:check :fixtures:check"
        status: pass
    human_judgment: false
  - id: D4
    description: The module checks and repository tooling can resolve the same isolated formatter and comments commands.
    requirement: QA-08
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :bff:kotlinQualityRuntime"
        status: pass
      - kind: integration
        ref: "./gradlew --console=plain :bff:dependencyInsight --configuration ktfmtTool --dependency com.google.guava:guava"
        status: pass
    human_judgment: false
actuals:
  tokens: 7019
  tasks: 2
  commits: 3
commits: 3
plan_head_before: 127766f0c5194b018b1446d3e6fa5abaacc9166c
plan_head_after: 74f6753b42099bf33fbb64ab22de4efb5e382037
duration: 13m55s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 05: Kotlin Documentation Quality Summary

**BFF and fixture checks now reject ktfmt differences, detekt KDoc findings, and Dokka warnings, with disposable tests that prove each failure and the repaired HTML publication.**

## Performance

- Started at 2026-11-25T13:38:29Z and completed execution evidence at 2026-11-25T13:52:24Z.
- Completed two tasks covering nine files.

## Accomplishments

- The shared JVM quality convention checks each Kotlin source set plus the module's Gradle Kotlin DSL scripts. ktfmt uses `--kotlinlang-style --dry-run --set-exit-if-changed`. The isolated detekt CLI enables `DeprecatedBlockTag`, `EndOfSentenceFormat`, `KDocReferencesNonPublicProperty`, and `OutdatedDocumentation`.
- `:bff:kotlinQualityRuntime` writes `bff/build/kotlin-quality/commands.json` with the Temurin executable, isolated tool classpaths, main classes, ktfmt style, and detekt config path. The harness uses those command prefixes directly.
- Dokka v2 generates HTML for BFF `main` and fixture `testFixtures` with `reportUndocumented`, `failOnWarning`, and offline link resolution. Both actual publication tasks run through the respective module's `check`.
- The checks and their repair controls run in disposable project copies with independent build directories and Gradle project caches. ktfmt checks the original bytes without modifying them, and the harness formats only the copied specimen.

## Task Commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-05-01 | `b0f35ed` | Shared ktfmt checks, detekt comments rules, and command export |
| 02-05-02 RED | `e9d49d8` | Disposable verification harness |
| 02-05-02 GREEN | `74f6753` | Warning-failing BFF and fixture publications |

## Verification

The tools resolved and ran with Eclipse Temurin 25.0.5.1+2-LTS, Gradle wrapper 9.9.2, KGP 2.4.21, ktfmt 0.65, detekt CLI 1.23.8, and Dokka 2.3.0. detekt's published stable compatibility row lists Kotlin 2.0.21, Gradle 8.12.1, and a maximum JDK of 21. Its isolated CLI ran syntax-only comments checks on the current corpus with its own embedded Kotlin 2.0.21. The current Dokka Gradle release generated both actual publications with the repository's tuple before the catalog pin. [ktfmt release](https://github.com/Kotlin/ktfmt/releases/tag/v0.65), [detekt release](https://github.com/detekt/detekt/releases/tag/v1.23.8), [detekt compatibility](https://detekt.dev/docs/introduction/compatibility/), [Dokka Gradle Plugin Portal](https://plugins.gradle.org/plugin/org.jetbrains.dokka), [Dokka release](https://github.com/Kotlin/dokka/releases/tag/v2.3.0)

| Command | Observed result |
| --- | --- |
| `./gradlew --console=plain :bff:ktfmtCheck :bff:detektComments` | Passed before and after the tracer commit. The BFF analyzed four Kotlin files, including the component suite and module build script. |
| `python3 tools/check_kotlin_quality.py format-comments` | Passed in 19.043 seconds. `KdocFormatWitness.kt` was reported by the Gradle ktfmt task with CLI exit 1 and its bytes were unchanged. Two actual formatter passes retained the KDoc paragraph, list, link, example and tags, and produced identical bytes on the second pass. Clean modules passed after restoring the original files. |
| `python3 tools/check_kotlin_quality.py publication` | Passed in 20.469 seconds. The BFF and fixture HTML tasks both emitted the named warning, failed with `warningCount=1 and errorCount=0`, and generated HTML containing the added KDoc after repair. |
| `./gradlew --console=plain :bff:dokkaGeneratePublicationHtml :fixtures:dokkaGeneratePublicationHtml` | Both publications generated nonempty `build/dokka/html/index.html` with no undocumented-declaration warnings. |
| `./gradlew --console=plain :bff:check :fixtures:check` | Both module checks passed with Docker pointed at `tcp://127.0.0.1:1`. BFF ran 2 unit and 4 component tests with zero skips or failures, and fixture variant isolation passed. |

detekt returned CLI exit 2 for `The first sentence of this KDoc does not end with the correct punctuation. [EndOfSentenceFormat]` on three paths covering BFF code, fixture code and the BFF Gradle script. Both module Gradle tasks failed with the same rule. An invalid configuration returned CLI exit 3 and `Property 'unrecognizedRuleSet' is misspelled or does not exist.` The formatter and detekt harness rejected separate candidate runs with the formatter's failure flag and `EndOfSentenceFormat` individually disabled. [detekt CLI exit codes](https://detekt.dev/docs/1.23.8/gettingstarted/cli/), [detekt comments rules](https://detekt.dev/docs/1.23.8/rules/comments/)

Dokka emitted `Undocumented: courses.bff/kdocPublicationWitness/#/ (jvm)` and `Undocumented: courses.fixtures/kdocPublicationWitness/#/ (testFixtures)`. The corresponding documentation exists in each repaired publication. [Dokka publication and source set settings](https://kotlinlang.org/docs/dokka-gradle-configuration-options.html)

Gradle `dependencyInsight --dependency com.google.guava:guava` provided the following isolation evidence.

| Configuration | Selection |
| --- | --- |
| `:bff:ktfmtTool`, `:fixtures:ktfmtTool`, `:probe:kdocFormatter` | Catalog constraint selects `33.8.0-jre` over the ktfmt request for `33.5.0-jre` and google-java-format's request for `32.1.3-jre`. |
| `:bff:runtimeClasspath`, `:bff:testRuntimeClasspath`, `:bff:componentTestRuntimeClasspath` | No matching Guava dependencies. |
| `:probe:runtimeClasspath` | Existing gRPC constraint selects `33.8.0-android` over `33.6.0-android`. |

### TDD evidence

- RED ran `test_publication` against Dokka 2.3.0 with `reportUndocumented` enabled and `failOnWarning` unset. It generated both warning lines and succeeded as a Gradle command, so unittest failed on the assertion requiring a nonzero publication result. GSD accepted the single test failure as `RED_EVIDENCE_OK`.
- GREEN reran the same test after enabling the publication gate. Both warning-bearing Gradle tasks failed, and the corrected Kotlin declarations generated the expected HTML.

## Decisions Made

- Shared configuration and launcher settings keep the future staged and full-repository drivers aligned with the Gradle Kotlin checks.
- The BFF and fixture projects publish API documentation from their distinct primary source sets. The offline publication keeps documentation verification independent of remote package lists.

## Deviations from Plan

**[Rule 3 - Blocking] Documented existing public declarations and formatted the BFF build script.** Dokka qualification exposed undocumented public declarations and constructor properties in both intended source sets. The KDoc-only corrections in `BffApplication.kt` and `DirectoryFixtures.kt` allow the configured publications to succeed. ktfmt also reformatted the required BFF build script and the touched build-logic script. The corrections are in `b0f35ed` and `74f6753`.

## Toolchain Observations

- The isolated detekt compiler emits the Temurin warning about `sun.misc.Unsafe::objectFieldOffset`. detekt still returned the expected success, finding, and invalid-configuration exit codes.
- Dokka 2.3.0 emits a Gradle deprecation warning for `Configuration.setVisible(boolean)`. Both publications and module checks completed on the pinned Gradle version.

## Next Phase Readiness

Plan 02-07 owns the staged hook and full-repository style driver that consume the formatter and analyzer policy. Plans 02-08 and 02-09 own the remaining toolchain inventory and phase verification. The shared requirements keep their existing global status until the declaring sibling plans finish.

## Self-Check: PASSED

All nine changed files are present. All three task commits are ancestors of the execution branch. The commit count matches the plan ledger.
