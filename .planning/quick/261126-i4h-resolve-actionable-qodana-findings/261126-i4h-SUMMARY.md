---
phase: quick-261126-i4h
plan: "01"
subsystem: build-tooling
tags: [qodana, gradle, kotlin-dsl, documentation]
requires:
  - phase: 02-build-and-ui-foundations
    provides: Shared Gradle conventions, documentation publication checks and repository style tooling
provides:
  - Explicit types for the lazy Java launchers in both JVM conventions
  - Ordered staging allowlist for documentation publication
  - Revision-scoped Qodana comparison and disposition of remaining results
affects: [build-logic, docs-site, local-quality-checks]
tech-stack:
  added: []
  patterns: [typed Gradle providers, Kotlin collection builders, Git archive scans]
key-files:
  modified:
    - build-logic/src/main/kotlin/courses.jvm.gradle.kts
    - build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts
    - docs-site/build.gradle.kts
key-decisions:
  - Keep the Gradle incubation diagnostics and framework-discovered declarations visible in the recommended profile.
commits: 2
plan_head_before: 13a3d7e94b92ee7bce18ef6267520a075a9743ed
plan_head_after: dcf35043eefa2111c0ca7c62995367e6d42e4f93
duration: 8m
completed: "2026-11-26"
status: complete
---

# Resolve actionable Qodana findings

The pinned Qodana rescan cleared both inferred Java launcher platform types and the concatenated documentation staging lists. The two `Provider<JavaLauncher>` declarations still select the project toolchain lazily. The `buildList` in `stageDocs` collects articles, templates and fonts in that order for the existing regular-file, canonical-path and report-byte checks.

## Verification

| Check                                                                                                 | Result                                                                                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain clean build --no-build-cache`                | Passed on the launcher commit in 18s and on the final source commit in 22s. The final build passed 6 BFF tests, 1 probe contract test, 19 generated-client tests, 14 docs tests, Steiger and the configured Kotlin/KDoc checks. |
| `./gradlew --console=plain :docs-site:check`                                                          | Passed 14 tests in 6s.                                                                                                                                                                                                          |
| `./gradlew --console=plain :docs-site:check -PdocsBase=/courses/ -PdocsAppUrl=http://127.0.0.1:5173/` | Passed 14 tests in 3s. Both publication runs verified the public file list and the staged feasibility report bytes.                                                                                                             |
| `mise exec python ruff taplo -- ./gradlew --console=plain styleCheck`                                 | Passed in 22s after applying the repository's ktfmt to `docs-site/build.gradle.kts`. Both source commits ran the checked-in pre-commit hook.                                                                                    |
| `mise exec python -- sh tools/qodana-scan.sh "$(git rev-parse HEAD)"`                                 | Exited 0 for the final source commit. Gradle import and code analysis completed, SARIF reported `executionSuccessful: true`, and the launcher saved SARIF and HTML.                                                             |

## Scan provenance

Both reports use Qodana Community for JVM 2026.3 (`QDJVM-263.8362`) and `qodana.recommended`. The rescan used the catalog image `jetbrains/qodana-jvm-community:2026.3@sha256:5420d961a4f3a850adc47fc6565916eb6fe558f3205f511ac7bc75b98812c37e` and Linux Temurin 25 selected from the archived revision. Each sibling `revision` marker matches the source SHA below. The generated reports remain under `.gradle/qodana/`.

- Baseline `e765a30a983d28a2ff6e2df8195ce523fc886230`
  - SARIF `.gradle/qodana/runs/e765a30a983d28a2ff6e2df8195ce523fc886230.OHyEMS/results/qodana.sarif.json`
  - HTML `.gradle/qodana/runs/e765a30a983d28a2ff6e2df8195ce523fc886230.OHyEMS/results/report/index.html`
- Final `dcf35043eefa2111c0ca7c62995367e6d42e4f93`
  - SARIF `.gradle/qodana/runs/dcf35043eefa2111c0ca7c62995367e6d42e4f93.HWo6Eg/results/qodana.sarif.json`
  - HTML `.gradle/qodana/runs/dcf35043eefa2111c0ca7c62995367e6d42e4f93.HWo6Eg/results/report/index.html`

## Inspection results

| Rule                                       | Baseline | Final | Changed location                                                                                                                                                                                                                                    |
| ------------------------------------------ | -------: | ----: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HasPlatformType`                          |        2 |     0 | Removed `testLauncher` at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:21` and `toolLauncher` at `build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts:84`.                                                                         |
| `CollectionConcatenationToBuildCollection` |        1 |     0 | Removed the `allowedSources` list concatenation at `docs-site/build.gradle.kts:86` in the baseline.                                                                                                                                                 |
| `UnstableApiUsage`                         |       51 |    52 | Added `suites` (`TestingExtension.getSuites()`) at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:24`. The `testing.suites.withType<JvmTestSuite>()` line is identical in both source revisions. The earlier pilot also reported the accessor. |
| `UnusedSymbol`                             |        7 |     7 | All seven declarations matched.                                                                                                                                                                                                                     |
| Total                                      |       61 |    59 | Three removals and one added observation at an existing accessor.                                                                                                                                                                                   |

The comparison matched rule ID, repository path, flagged symbol or expression, and diagnostic message. All 58 shared results also had identical line and column coordinates. The only new result points to the existing incubating suite accessor.

### Gradle incubation

- 36 findings concern `testing`, `suites`, `JvmTestSuite`, `dependencies`, `useJUnitJupiter`, `targets` and `testTask` in `courses.jvm.gradle.kts`, `bff/build.gradle.kts` and `probe/build.gradle.kts`. These call sites configure JUnit Jupiter and lazy test tasks, isolate fixture and schema-validator dependencies in BFF test suites, and define the probe's ordinary and opt-in suites with their own dependencies and settings.
- 12 findings concern configuration roles. `dependencyScope` and `resolvable` give the convention's ktfmt and detekt tools, the probe's KDoc formatter and the web build's OpenAPI and BFF JAR consumers separate declaration and resolution configurations. BFF's two `consumable` configurations publish the OpenAPI contract and executable JAR to those web consumers.
- Two `buildTreePath` findings in `bff/build.gradle.kts` identify the fixtures project when checking its test-fixtures variant and detecting fixture leakage into production runtime. The two `repositories` findings in the root and included-build `settings.gradle.kts` files are `dependencyResolutionManagement.repositories` calls that centralize dependency repositories. These are intentional Gradle 9.9.2 API uses.

### Spring and Axon discovery

`startProbeRole` registers `CommandRoleConfiguration` or `ProjectionRoleConfiguration` with Spring. Axon discovers the annotated handlers on the resulting beans.

| Declaration                                  | Runtime entry point and retained evidence                                                                                                                 |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ProbeApplication.kt:87` `enrollmentHandler` | Spring `@Bean` creates the handler for the command role. The probe checks that the writer registers both command names.                                   |
| `ProbeApplication.kt:101` `ready`            | Axon `@CommandHandler` handles `READY_COMMAND` while `ProbeFixture.startCommand` waits for the remote writer.                                             |
| `ProbeApplication.kt:107` `enroll`           | Axon `@CommandHandler` handles `WRITE_COMMAND`. The probe checks the tagged event and receipt returned by the remote writer.                              |
| `ProbeProjection.kt:32` `tokenStore`         | Spring `@Bean` supplies the projection role's in-memory `TokenStore`. The probe waits for the streaming processor and verifies the update it processes.   |
| `ProbeProjection.kt:35` `courseProjection`   | Spring `@Bean` creates the projection that supplies the Axon query and event handlers. The probe checks the remote projection registration and readiness. |
| `ProbeProjection.kt:44` `course`             | Axon `@QueryHandler` handles `READ_COURSE`. The probe checks the initial state and queries the updated state after the enrollment.                        |
| `ProbeProjection.kt:51` `enrolled`           | Axon `@EventHandler` handles `ENROLLED_EVENT` and emits a subscription update. The probe checks the one-enrollment update and its event ID.               |

These locations are under `probe/src/main/kotlin/probe/`. The integration assertions live in `probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt` and `ProbeFixture.kt`. `docs/feasibility/phase-01.md` records the earlier native execution of the three integration cases. The current clean build ran the ordinary probe suite with Docker unavailable.

### Gradle import notice

Each SARIF report carries one separate `toolExecutionNotifications` entry with `level: error` and `qodanaKind: sanityFailure` for the unresolved `build-logic/build/pluginUnderTestMetadata` root in `build-logic.test`. The archived `build-logic` project has no test sources and the scan log reports zero source roots for that module. `pluginUnderTestMetadata` is generated for Gradle TestKit, and its output directory is absent in the scanned snapshot. Gradle data import completed successfully, code analysis completed, and the reports contain findings from both production convention scripts and the probe's main Kotlin sources. The notice remains visible in the report. [Gradle Plugin Development Plugin](https://docs.gradle.org/current/userguide/java_gradle_plugin.html)

## Task commits

- `2c64bb43fbd370a07bb9b05bb7a957be7bacfdf9` typed the test and quality tool launchers.
- `dcf35043eefa2111c0ca7c62995367e6d42e4f93` built the ordered staging allowlist directly.

## Self-Check: PASSED
