---
phase: quick-261126-jp0
plan: "01"
subsystem: build-tooling
tags: [qodana, kotlin, spring, axon, docker]
requires:
  - phase: quick-261126-ink
    provides: Catalog-pinned Community launcher, Axon entry points and a clean diagnostic baseline
provides:
  - Native Kotlin entry-point recognition by the Spring Bean annotation's fully qualified name
  - Revision-scoped installation of verified entry-point settings and separate analysis state
affects: [local-quality-checks, maintainer-guide]
tech-stack:
  added: []
  patterns: [IntelliJ EntryPointsManager project state, configuration-keyed analysis cache]
key-files:
  created: [.qodana/profiles/spring-beans.xml]
  modified: [tools/qodana-scan.sh, docs/maintainer-guide.md]
key-decisions:
  - Install native EntryPointsManager XML only in the disposable archived project and retain the recommended profile.
  - Separate cached IDE project state by the archived entry-point XML blob while sharing Gradle and plugin caches.
requirements-completed: [QA-07]
commits: 1
plan_head_before: 01045e6e975293484d77a12c893ecd1cef41f35c
plan_head_after: b838a25320cdce2b3655d64a9026e1747e338486
actuals:
  tokens: 1977
  tasks: 3
  commits: 1
duration: 12m
completed: "2026-11-26"
status: complete
---

# Recognize Spring Bean entry points in Qodana Community

Qodana Community for JVM now recognizes `org.springframework.context.annotation.Bean` in the archived scan. The three probe factories and a temporary fourth factory cleared `UnusedSymbol`. The ordinary unused method and an unused method annotated with a different `Bean` remained reportable.

## Native setting

The installed Kotlin `UnusedSymbolInspection` uses IntelliJ's Java entry-point checks through `K2UnusedSymbolUtil`. IntelliJ serializes `EntryPointsManager.ADDITIONAL_ANNOTATIONS` in the `EntryPointsManager` component in `.idea/misc.xml`. The verified entry is one `java.lang.String` item with the exact fully qualified Spring annotation name. Profile selection still uses `--profile-name qodana.recommended`, which has priority over profile settings in `qodana.yaml`. JetBrains tracks a dedicated YAML option in QD-14001. [EntryPointsManager implementation](https://github.com/JetBrains/intellij-community/blob/master/java/java-analysis-impl/src/com/intellij/codeInspection/ex/EntryPointsManagerBase.java), [profile resolution](https://www.jetbrains.com/help/qodana/inspection-profiles.html#order-of-resolving-a-profile), [QD-14001](https://youtrack.jetbrains.com/issue/QD-14001)

The scratch candidate's Gradle import completed and its generated `misc.xml` contained the entry point alongside the generated Gradle and JDK settings. Qodana also persisted the component in its analysis cache. The launcher installs the XML inside the archived project, separates the analysis cache by its Git blob, and preserves the shared Gradle cache, existing plugin cache key and cache lock. A scratch archive with both settings files failed with the collision diagnostic before Docker startup and released its lock. The working checkout's `.idea/misc.xml` had the same SHA-256 before and after the runs. QD-13987 documents cached project settings and a separate merge-request import failure. Both local scratch imports succeeded. [QD-13987](https://youtrack.jetbrains.com/issue/QD-13987)

## Verification

All scans used Linux ARM64 Qodana Community for JVM 2026.3 (`QDJVM-263.8362`) with `jetbrains/qodana-jvm-community:2026.3@sha256:5420d961a4f3a850adc47fc6565916eb6fe558f3205f511ac7bc75b98812c37e`, Temurin 25, Gradle 9.9.2 and Axon Framework 0.10.1 (`io.axoniq.ide.intellij`). The installed plugin JAR matched the prior qualified SHA-256 `924cb8f1ba3c30e0d3970191d2adbbf2b2ab7e9d2012f355f100bdfa44181fef`. Baseline `c413c156594144b3aec546fbdca828e63c7c7b39` matched the starting revision for scanner inputs, including the catalog, Java feature, launcher and plugin configuration. The revision diff contained only planning metadata.

Every report had a matching revision marker, saved HTML, SARIF `configProfile: recommended` and `executionSuccessful: true`. The scratch pair and the first source scan completed full Gradle imports. The historical scan and source repeat loaded and synchronized their cached models. The normalized `Modules.json` structures matched across all six reports, with 20 modules and `org.springframework:spring-context:7.1.0` bound to `axon5-dcb-courses.probe.main`. The four Axon handlers `ready`, `enroll`, `course` and `enrolled` stayed recognized in each report.

| Run | `UnusedSymbol` | `UnstableApiUsage` | Total |
| --- | -------------: | -----------------: | ----: |
| Prior baseline and historical revision | 3 | 51 | 54 |
| Scratch control with ordinary, lookalike and genuine bean controls | 6 | 52 | 58 |
| Scratch candidate with `EntryPointsManager` | 2 | 52 | 54 |
| Source commit after fresh Gradle import | 0 | 52 | 52 |
| Source commit after historical scan, with warm analysis state | 0 | 51 | 51 |

The multiset comparison used rule, path, highlighted declaration or expression, and message. The scratch candidate removed exactly `enrollmentHandler`, `tokenStore`, `courseProjection` and `qodanaFreshSpringBean`, with zero additions. `qodanaLookalikeBean` and `qodanaOrdinaryUnused` remained. The historical revision restored the three original bean diagnostics and reproduced the prior baseline multiset. The warm source repeat differed from that baseline by exactly the three original factories. Fresh imports also showed the previously observed `TestingExtension.getSuites()` diagnostic at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:24`. All reports carried one separate `sanityFailure` for the generated `build-logic/build/pluginUnderTestMetadata` root in `build-logic.test`.

The checked-in pre-commit hook, `mise exec python ruff taplo -- ./gradlew --console=plain styleCheck`, managed ShellCheck, `sh -n tools/qodana-scan.sh` and `git diff --check` passed. `./gradlew --console=plain :probe:test :probe:integrationTest --rerun-tasks` passed against local Colima. The JUnit XML recorded one ordinary case and three Docker-backed cases, with zero failures, errors or skips.

### Local reports

The paths contain `qodana.sarif.json`, `report/index.html`, `log/idea.log` and `projectStructure/Modules.json`.

- Prior baseline `.gradle/qodana/runs/c413c156594144b3aec546fbdca828e63c7c7b39.AE9pCf/results/`
- Scratch control `.gradle/qodana/261126-jp0/control/.gradle/qodana/runs/009ef4629fb54e1d7d1e8588df5f224a54a948a9.un9fZ4/results/`
- Scratch candidate `.gradle/qodana/261126-jp0/candidate/.gradle/qodana/runs/62638ac8ae5b09421c363f0316ca3f69e617a480.NkLEwJ/results/`
- Fresh source scan `.gradle/qodana/runs/b838a25320cdce2b3655d64a9026e1747e338486.cItRLV/results/`
- Historical scan `.gradle/qodana/runs/01045e6e975293484d77a12c893ecd1cef41f35c.fa0PpZ/results/`
- Warm source scan `.gradle/qodana/runs/b838a25320cdce2b3655d64a9026e1747e338486.OYcBZO/results/`

Run `mise exec python -- sh tools/qodana-scan.sh b838a25320cdce2b3655d64a9026e1747e338486` to reproduce the committed behavior. New methods with Spring's exact `@Bean` are covered automatically. The maintainer guide records the control experiment and the Ultimate or Ultimate Plus license and `QODANA_TOKEN` required for full Spring inspections. [Maintainer guide](../../../docs/maintainer-guide.md#local-kotlin-inspections), [JetBrains JVM feature matrix](https://www.jetbrains.com/help/qodana/jvm.html#Supported+technologies+and+features)

## Task commits

- Scratch qualification and scan evidence are local artifacts.
- `b838a25` delivers the native project setting, cache isolation and maintainer guidance.

## Deviations from plan

**[Rule 2 - Correctness] Isolate cached project settings.** The native scratch scan wrote the project component into the analysis cache. The implementation keys analysis state by the archived XML and checks the historical revision after scanning the source commit. The two revisions retain their respective entry-point behavior while using the same Gradle and Axon plugin caches.

## Self-Check: PASSED
