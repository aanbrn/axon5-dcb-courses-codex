---
phase: 01-axon-server-and-toolchain-feasibility
plan: "05"
subsystem: testing
tags: [axon-server, dcb, arm64, evidence, supply-chain]
requires:
  - phase: 01-04
    provides: Independent Kotlin, Kotest, KDoc, and bidirectional TypeID stages alongside the frontend probe.
provides:
  - A fresh native ARM64 acceptance capture verified from original JUnit, command and OCI evidence.
  - A permanent feasibility record for the selected toolchain, entitlement scope, and future AMD64 replacement.
affects: [build-foundations, core-enrollment, container-delivery, hosted-verification]
commits: 4
plan_head_before: 9622a4aac89e0ddc4af9fa23a60741a62624f2cd
plan_head_after: 64075aaa425e1dc83274ff8e0246fa30d7676987
actuals:
  tokens: 17565
  tasks: 2
  commits: 4
tech-stack:
  added: []
  patterns: [Run-bound evidence manifest, Scoped Gradle constraints, Immutable OCI platform correlation]
key-files:
  created: [probe/verify_evidence.py, docs/feasibility/phase-01.md]
  modified: [probe/README.md, probe/build.gradle.kts, gradle/libs.versions.toml, .planning/PROJECT.md]
key-decisions:
  - Record a native acceptance tuple with its tested revision, input SHA-256, and manifest SHA-256.
  - Constrain Guava in the consuming runtime and formatter graphs with separate scoped, catalog-backed lower bounds.
  - Preserve the permanent report and require hosted AMD64 Testcontainers and Playwright coverage before probe retirement.
patterns-established:
  - Bind real producer commands and raw exits to a single freshness-checked acceptance directory.
  - Separate runtime proof, publisher terms, public advisory review, and private advisory coverage.
requirements-completed: [FND-01]
coverage:
  - id: D1
    description: Fresh credential-free native DCB and Docker-free ordinary smoke build.
    requirement: FND-01
    verification:
      - kind: integration
        ref: "python3 probe/verify_evidence.py --capture --evidence probe/build/reports/feasibility"
        status: pass
    human_judgment: false
  - id: D2
    description: Permanent feasibility report reconciles the actual tuple, OCI children and four secondary dispositions.
    requirement: FND-01
    verification:
      - kind: other
        ref: "python3 probe/verify_evidence.py --evidence probe/build/reports/feasibility --report docs/feasibility/phase-01.md"
        status: pass
    human_judgment: false
duration: 47min
completed: 2026-11-25
status: complete
---

# Phase 01 Plan 05: Final Feasibility Record Summary

**One immutable ARM64 acceptance run links the real DCB winner and rejected overlap to passing frontend, TypeID, Kotest, and KDoc checks.**

## Execution

- Started 2026-11-24T23:21:11Z. The original implementation and report commits were complete at approximately 2026-11-25T00:08:28Z.
- The post-review capture `acceptance-nvahwpkb` ran from 2026-11-25T00:22:18Z through 00:27:08Z in 290.05 seconds. It captured tested revision `0f3101a5d7195f2c5d9d26d42e95849232a8028d`, input SHA-256 `d4cccac9e0439c65fce4dbfb7bdd41803dbed864aaf4b179228ff6ddb21ca198`, and manifest SHA-256 `7e658ac02d887445d2846e32716ec3de1acba3b7de199628e0cff90be644b948`. It supersedes `acceptance-5zjznvdt`.
- Both ordinary builds executed the contract smoke case with the Docker endpoint unreachable. The cold and warm invocations took 6.86 and 2.76 seconds. Three integration cases executed in a 96.07-second wrapper invocation, with 91.961 seconds reported by JUnit and zero skips, errors or failures. The verifier correlated three JVMs, independent durable reads, the typed rejection, the remote subscription update and the cleanup path. The winner was event `de75dc0a-f9f8-4a3f-9ea4-98d8f3c487f4`.
- Gradle 9.9.2, Kotlin 2.4.21, Spring Boot 4.2.0, both Axon Framework distributions 5.4.2, Temurin 25.0.5.1+2-LTS, Axon Server 2026.1.8 and Linux/ARM64 Docker 29.10.0 passed together. The OCI index and both runnable children were independently measured. Docker's running config matched the ARM64 registry config.
- All seven secondary stages exited zero and all four groups passed. The stage diagnostics confirm Node 26.13.1, npm 12.2.3, and Pack 0.40.11 for the applicable stages. The staged HTML was 138 bytes, and the two native HTTP bodies were 144 and 145 bytes. The refreshed report passed verification on Python 3.9.6 and 3.12.1. Local preflight rejected a changed OCI config, an integration task added to the ordinary dry-run graph, a mismatched report digest, missing terms, and a broken guide link.

## Task Commits

| Commit | Task |
| --- | --- |
| `079f39d` | Correct affected role and test Guava selection before capture. |
| `0ea8753` | Correct the independent formatter Guava selection before capture. |
| `3b5f0ef` | Capture and verify native feasibility evidence. |
| `64075aa` | Publish the verified report and reproduction guide. |

## Deviations from Plan

1. **[Rule 2 - Security]** The scoped review reproduced GHSA-xxph-c9ww-hj94 in the role and test graphs at Guava 33.6.0-android and in the formatter graph at 33.5.0-jre. The existing BOMs did not select a fixed release. Catalog-backed lower bounds selected 33.8.0-android and 33.8.0-jre in their consuming configurations. Affected and control graph comparisons, the ordinary build, native integration and KDoc checks passed. Commits `079f39d` and `0ea8753` capture the version-owner corrections.
2. **[Rule 3 - Reproduction]** The checker source was committed after local preflight and before the fresh capture so the tested revision itself contains the acceptance command. Final task acceptance used the live capture after that commit.
3. **[Rule 1 - Verification]** Post-review commit `0f3101a` corrected failure classification, took Node, npm, and Pack identity from the diagnostic producers, made timestamp parsing compatible with Python 3.9, and validated the staged HTML digest. The live rerun passed with the same runtime tuple and OCI digests.

## Remaining Review Scope

- The public advisory and dependency graph comparison is complete for the examined graphs. The private JVM advisory result is incomplete because the historical procedure and authorized feed were unavailable, and the later application modules were absent. The maintainer received this status. The project policy retains the weekly and relevant-change recheck.
- The TypeID compatibility check passed. The separate scoped npm audit exited 1 for one underlying Moderate advisory with no High or Critical entries. The sample-only hold is reviewed by 2026-12-02. Application TypeScript dependency selection remains open.
- The first actual AMD64 execution belongs on a hosted GitHub Actions AMD64 runner. Probe retirement requires passing replacement Testcontainers and Playwright coverage. Account-based Platform use and extended license behavior remain outside the measured local run.
- The phase verifier owns the independent FND-01 and phase completion sign-off.

## Self-Check: PASSED

All three declared files exist, the original implementation and report commits and the post-review correction are reachable, and the report matches the retained post-review acceptance manifest.
