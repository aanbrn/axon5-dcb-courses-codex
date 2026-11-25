---
phase: 02-build-and-ui-foundations
plan: "08"
subsystem: build
tags: [doctor, gradle, jvm, npm, dependency-maintenance, documentation]
requires:
  - phase: 02-02
    provides: BFF worker and JVM suite configurations
  - phase: 02-04
    provides: Public docs publication and feasibility record
  - phase: 02-05
    provides: Isolated shared Kotlin formatter configuration
  - phase: 02-07
    provides: Version owners and reproducible repository style entry points
  - phase: 02-11
    provides: Measured Steiger package extension and removal criteria
provides:
  - Toolchain readiness report with required, additional and deferred observations
  - Public version inventory and verified dependency-maintenance procedures
  - Reproducible public Gradle controls and documented B8 procedure
affects: [02-09, 03, 07]
tech-stack:
  added: []
  patterns: [observed executable checks, disposable dependency comparison, public publication allowlist]
key-files:
  created:
    - tools/doctor.py
    - tools/verify_dependency_evidence.py
  modified:
    - build.gradle.kts
    - docs/maintainer-guide.md
    - docs-site/test/site.test.mjs
key-decisions:
  - Doctor probes existing managed executables and identifies the setup command for an unprovisioned consumer.
  - Preserve each existing Guava constraint on its owning configuration and compare changes using the current tooling with just those constraints removed.
  - Keep the B8 private result incomplete and publish only the scoped procedure and public evidence.
requirements-completed: [FND-02, DOC-06]
requirements-pending: [CQRS-04, QA-08]
coverage:
  - id: D1
    description: Doctor verifies the configured toolchain and assigns optional failures only to affected workflows.
    requirement: FND-02
    verification:
      - kind: integration
        ref: "python3 tools/doctor.py --self-test && env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain doctor"
        status: pass
      - kind: other
        ref: "python3 tools/doctor.py"
        status: pass
    human_judgment: false
  - id: D2
    description: The public maintainer guide reproduces selected dependency evidence and publishes the incomplete private procedure.
    requirement: DOC-06
    verification:
      - kind: integration
        ref: "python3 tools/verify_dependency_evidence.py && ./gradlew --console=plain :docs-site:check"
        status: pass
    human_judgment: false
duration: 17m50s
completed: 2026-11-25
status: complete
commits: 3
plan_head_before: 146f48cc970e9ec8447499fb836c0505ef08cb0c
plan_head_after: a22138c6d48fb569ae9347da45604c84c771b1b1
actuals:
  tokens: 16840
  tasks: 2
  commits: 3
---

# Phase 02 Plan 08: Toolchain Doctor and Dependency Evidence Summary

**The root doctor verifies the launcher, BFF worker and managed Node/npm with independent infrastructure statuses, and the published guide reproduces scoped Gradle dependency choices while recording the incomplete private advisory result.**

## Performance

- **Duration** 17m50s
- **Started** 2026-11-25T15:36:59Z
- **Completed** 2026-11-25T15:54:49Z
- **Tasks** 2
- **Files changed** 5

## Task commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-08-01 RED | `1436d2a` | Intentional missing-Git readiness failure and diagnostic fixtures |
| 02-08-01 GREEN | `e988bf2` | Gradle and bootstrap doctor, version inventory, setup and style entry points |
| 02-08-02 | `a22138c` | Disposable public dependency comparisons, maintenance procedures and rendered-guide coverage |

## Verification

| Command | Observed result |
| --- | --- |
| `python3 tools/doctor.py --self-test` | Five tests passed. The fixtures cover missing required Git, wrong Java vendor and feature in both modes, a wrong managed Node, a conflicting PATH Node, an unreachable daemon, missing Compose and Pack, and synthetic secret suppression. |
| `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain doctor` | Passed twice with Gradle `9.9.2`, launcher and actual BFF toolchain Eclipse Adoptium `25.0.5.1 (25.0.5.1+2-LTS)`, Python `3.12.1`, Git `2.54.0`, Ruff `0.17.4` and Taplo `0.10.0`. Each managed Node/npm executable reported `v26.13.1` and `12.2.3`. Docker daemon and architecture reported additional failures. Compose `2.32.1` and Pack `0.40.11` were available. GitHub Actions were deferred to 02-09. |
| `python3 tools/doctor.py` | Bootstrap passed and deferred observations that depend on Gradle. A real Gradle invocation before docs-site tool provisioning exited 1 and printed both suggested repair commands. `:docs-site:npmSetup` succeeded and the next report observed its managed tools. |
| `python3 tools/verify_dependency_evidence.py && ./gradlew --console=plain :docs-site:check` | Passed. Full reports, actual dependency insight and normalized edge snapshots were collected for 17 public configurations across checked-in, unconstrained and restored states. The BFF unit and component tests, fixture isolation, ktfmt and probe unit and KDoc checks passed in all three states. All 14 docs tests passed, including the rendered B8 scope and synthetic-input exclusion test. |
| `python3 tools/verify_dependency_evidence.py --offline --expect-bff-runtime-guava 0.0.0` | Exited 1. The real Gradle graph reported Guava absent in `:bff:runtimeClasspath`, rejecting the invented version. |
| Managed `npm ls --all --json --offline` | Exit 0 with no reported problems in all five installed trees. Web has 28 direct packages. Docs uses Eleventy `3.1.8`. Style uses Prettier `3.10.1` and git-format-staged `4.0.2`. The static probe has zero direct packages and the TypeID probe has two. |

TDD RED ran `DoctorTests.test_missing_required_tool_exits_nonzero_with_repair`. It reached the exit-status assertion with Git missing and observed exit 0 where the expected status was 1. GSD classified the genuine test assertion as `RED_EVIDENCE_OK`. The same fixture passed after GREEN. No separate refactor commit was required.

## Reproduced public findings

- The six probe main, unit and integration compile/runtime graphs selected `33.8.0-android` instead of the `33.6.0-android` selected after removing the bound. Runtime incoming paths included `grpc-api` and `grpc-stub` at `1.84.1`. Compile exposed the `grpc-stub` incoming edge. Gradle reported the JRE compile/runtime variant names for the Android-suffixed component coordinate. Error Prone annotations changed alongside Guava.
- Both formatter graphs selected `33.8.0-jre` instead of `33.5.0-jre`, through ktfmt `0.65` and google-java-format `1.23.0`. Error Prone annotations and JSpecify changed with the formatter selection. The nine BFF classpath, detekt, Kotest and TypeID controls stayed equal. Restoring the bounds reproduced the checked-in graphs exactly.
- The Boot `4.2.0` BOM resolved as POM metadata with pgJDBC `42.7.14`. Examined BFF and probe application/test classpaths selected no driver. The guide records `42.7.15` or a verified newer fix as the target for a future consumer.
- The guide identifies the original B17 and B8 references as unavailable, records the dated Phase 1 evidence and applicable image/terms boundaries, and carries the TypeID and Steiger tool-only holds through their 2026-12-02 review.

## Deviations and evidence limits

The planned files and constraints were preserved. The first public BOM artifact query needed online access to its public Maven repository. The offline negative control succeeded using the resulting cache. The pre-existing site test formatting baseline remains part of 02-09.

B8 remains incomplete without the authorized feed, scanner and inputs. Its open disposition is recorded in the published guide and requires follow-up by the build maintainer. Probe integration evidence here covers the selected graphs. Docker-backed DCB execution, hosted AMD64 runtime, GitHub Actions execution and hosted advisory or image scanning require their respective verification.

## Self-Check: PASSED

All five implementation files and this summary exist. The three measured task commits are reachable from the phase branch and the GSD evaluation scope resolves them.
