---
phase: quick-261126-ink
plan: "01"
subsystem: build-tooling
tags: [qodana, kotlin, axon, spring, docker]
requires:
  - phase: 02-build-and-ui-foundations
    provides: Catalog-pinned Community scanner and the Kotlin Axon probe
provides:
  - Marketplace-backed Axon handler recognition in local Kotlin inspections
  - Installed plugin caches keyed by the scanned configuration
  - Requalification procedure and licensed Spring prerequisites
affects: [local-quality-checks, maintainer-guide]
tech-stack:
  added: []
  patterns: [Marketplace plugin resolution, revision-scoped plugin cache]
key-files:
  created:
    - qodana.yaml
  modified:
    - tools/qodana-scan.sh
    - docs/maintainer-guide.md
key-decisions:
  - Use the documented Marketplace ID for the Axon plugin and requalify when the resolved plugin or linter changes.
  - Keep Gradle and analysis state reusable while isolating installed plugins by archived Qodana configuration.
commits: 2
plan_head_before: c0006845dd626c484e904805610c84194f0342ad
plan_head_after: c413c156594144b3aec546fbdca828e63c7c7b39
actuals:
  tokens: 1131
  tasks: 2
  commits: 2
duration: 10m
completed: "2026-11-26"
status: complete
---

# Qualify Axon and Spring inspections in Qodana

Qodana Community for JVM recognized the two Axon command handlers, the query handler and the event handler in the Kotlin probe after loading Axon Framework plugin 0.10.1. It continued reporting the unannotated control and the three Spring bean methods as unused. The launcher selects the installed plugin cache from the inspected revision, so historical scans retain their original plugin behavior.

## Verification

The four principal scans used native Linux ARM64 Qodana Community for JVM 2026.3 (`QDJVM-263.8362`), `qodana.recommended` and the catalog image `jetbrains/qodana-jvm-community:2026.3@sha256:5420d961a4f3a850adc47fc6565916eb6fe558f3205f511ac7bc75b98812c37e`. The launcher supplied Temurin 25 from each revision's `.java-version` and used the repository's Gradle 9.9.2 wrapper. All four reached 100% analysis, saved HTML and SARIF, exited 0 and reported `executionSuccessful: true`.

The scratch repositories came from `c0006845dd626c484e904805610c84194f0342ad`. Their committed inputs matched byte for byte except for the candidate's Marketplace declaration. Both contained `qodanaQualificationUnusedControl`, a public unannotated method next to `EnrollmentHandler.ready`. Each scratch scan started with independent plugin and analysis caches and a copy of the existing Gradle cache. Both completed Gradle import successfully and produced byte-identical inspection structures containing 20 modules.

The implemented launcher then scanned `c413c156594144b3aec546fbdca828e63c7c7b39` and the historical base in that order from the same checkout. Both synchronized the cached workspace model successfully and produced byte-identical inspection structures. The final startup logged `Axon Framework (io.axoniq.ide.intellij, 0.10.1)`. The historical startup listed the two bundled-image custom plugins and no Axon plugin.

Both source commits passed the checked-in pre-commit hook. Managed ShellCheck, `sh -n tools/qodana-scan.sh` and `mise exec python ruff taplo -- ./gradlew --console=plain styleCheck` passed after the cache fix.

### Local reports

Each result directory contains `qodana.sarif.json`, `report/index.html` and `log/idea.log`. The sibling `revision` files match the SHA embedded in each path. Reports and scratch repositories are local and Git-ignored.

- Scratch control `.gradle/qodana/261126-ink/control/.gradle/qodana/runs/e16bcd72547b7ff88a2c9f115cf20541a6200a25.oF9xWw/results/`
- Scratch candidate `.gradle/qodana/261126-ink/candidate/.gradle/qodana/runs/086968cc12715099da7f0a6590cec297ccba03a3.TrUO5M/results/`
- Final source `.gradle/qodana/runs/c413c156594144b3aec546fbdca828e63c7c7b39.AE9pCf/results/`
- Historical base after the final source scan `.gradle/qodana/runs/c0006845dd626c484e904805610c84194f0342ad.SvWDba/results/`

### Diagnostics

The comparison matched result multiplicities by inspection ID, repository path, highlighted symbol or expression, and diagnostic message. The four handler rows below account for every removal in both the scratch comparison and the final-to-historical comparison. Both comparisons had zero additions.

| Declaration                        | Entry point           | Scratch control | Scratch candidate | Historical base | Final source |
| ---------------------------------- | --------------------- | --------------: | ----------------: | --------------: | -----------: |
| `ready`                            | Axon `@CommandHandler` |        Reported |           Cleared |        Reported |      Cleared |
| `enroll`                           | Axon `@CommandHandler` |        Reported |           Cleared |        Reported |      Cleared |
| `course`                           | Axon `@QueryHandler`   |        Reported |           Cleared |        Reported |      Cleared |
| `enrolled`                         | Axon `@EventHandler`   |        Reported |           Cleared |        Reported |      Cleared |
| `enrollmentHandler`                | Spring `@Bean`         |        Reported |          Reported |        Reported |     Reported |
| `tokenStore`                       | Spring `@Bean`         |        Reported |          Reported |        Reported |     Reported |
| `courseProjection`                 | Spring `@Bean`         |        Reported |          Reported |        Reported |     Reported |
| `qodanaQualificationUnusedControl` | Ordinary Kotlin method |        Reported |          Reported |   Scratch only | Scratch only |
| `UnusedSymbol` total                |                       |               8 |                 4 |               7 |            3 |
| `UnstableApiUsage` total            |                       |              52 |                52 |              51 |           51 |
| Total results                      |                       |              60 |                56 |              58 |           54 |

`ready`, `enroll`, `enrollmentHandler` and the control are in `probe/src/main/kotlin/probe/ProbeApplication.kt`. The other declarations are in `probe/src/main/kotlin/probe/ProbeProjection.kt`. All eight declaration diagnostics use the message `Function "<name>" is never used`.

The 51 common warm-run Gradle incubation results matched the corresponding scratch results. Both scratch reports also flagged `TestingExtension.getSuites()` at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:24`. The preceding quick task also observed variation at this unchanged Gradle accessor. Each principal SARIF report contained one separate `sanityFailure` for the unresolved generated `build-logic/build/pluginUnderTestMetadata` root of `build-logic.test`.

## Plugin provenance and Spring prerequisite

Marketplace resolved `io.axoniq.ide.intellij` to Axon Framework 0.10.1, update 1119101. The scratch download cache held the same bytes as the published signed ZIP, with SHA-256 `20836a04198db59ddb5e958076cb364d15ce85f6ca30055c839a47cd7ecb695f`. Both installed main plugin JARs matched the ZIP member SHA-256 `924cb8f1ba3c30e0d3970191d2adbbf2b2ab7e9d2012f355f100bdfa44181fef`. The descriptor registers `AxonImplicitUsageProvider` and depends on the platform, Java and Kotlin. The candidate and final startup logs confirm successful loading. A JetBrains build-server plugin index returned HTTP 401 in both control and candidate logs. Public Marketplace installation still succeeded and SARIF contained only the existing Gradle notice. [Marketplace update](https://plugins.jetbrains.com/plugin/download?updateId=1119101), [release source](https://github.com/AxonFramework/IdeaPlugin/tree/v0.10.1)

Qodana's documented Marketplace declaration and published YAML schema specify a plugin ID. Its compatible version can change when Marketplace publishes an update. The maintainer guide records how to validate a new resolved release with two disposable snapshots and independently initialized plugin caches. [Plugin configuration](https://www.jetbrains.com/help/qodana/configuration-reference.html#Manage+plugins), [YAML schema](https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/qodana-1.0.json)

Spring inspections require Qodana for JVM under Ultimate or Ultimate Plus and an authorized project `QODANA_TOKEN`. The variable was absent in this environment. The measured Spring behavior applies to Community only. [JVM feature matrix](https://www.jetbrains.com/help/qodana/jvm.html#Supported+technologies+and+features), [token requirements](https://www.jetbrains.com/help/qodana/docker-image-configuration.html)

## Deviations from plan

**[Rule 1 - Bug] Isolate cached plugins by inspected configuration.** A follow-up scan of the scratch control on the original candidate's warm cache loaded Axon 0.10.1 even though the examined commit had no `qodana.yaml`. Its four Axon warnings disappeared, and an internal JetBrains event-log shutdown exception appeared after analysis with exit 0. The reproducer is in `.gradle/qodana/261126-ink/candidate/.gradle/qodana/runs/e16bcd72547b7ff88a2c9f115cf20541a6200a25.po4F80/results/`. The launcher now mounts a dedicated directory at `/data/cache/plugins`, keyed by the archived configuration's Git blob or `no-config`. The final scan populated the keyed cache. The subsequent historical scan restored all four Axon warnings while the legacy unkeyed plugin copy was still present, demonstrating isolation with the shared Gradle cache.

## Task commits

- Scratch qualification created only the two disposable source snapshots and local reports.
- `c8b64ef` enabled the verified Axon plugin and documented framework behavior.
- `c413c15` isolated the installed plugin cache and documented the cache layout.

## Self-Check: PASSED
