---
phase: 01-axon-server-and-toolchain-feasibility
plan: "04"
subsystem: build
tags: [kotlin, junit, kotest, ktfmt, typeid, typescript, evidence]
requires:
  - phase: "01-02"
    provides: "Required native Axon DCB proof and the secondary evidence verifier."
  - phase: "01-03"
    provides: "Pinned Node/npm owners and the isolated Gradle Node entry point."
provides:
  - "Opt-in Jupiter/Kotest and ktfmt/KDoc probes with independent evidence."
  - "TypeID conformance against pinned official vectors and verified Kotlin and TypeScript exchanges."
affects: ["01-05", "02", "03"]
actuals:
  tokens: 18047
  tasks: 3
  commits: 6
commits: 6
plan_head_before: 93eac029ae2514500d083dfbee4342dcf98bc31f
plan_head_after: 109d6b11a1561683558d3780fdc51765bd252118
tech-stack:
  added: [Kotest 6.2.7, ktfmt 0.65, typeid-java 0.3.1, typeid-js 1.2.0, TypeScript 7.0.2]
  patterns: [Opt-in JVM suites, scratch-file formatter checks, independent run-bound TypeID exchanges]
key-files:
  created:
    - probe/kdoc/Specimen.kt
    - probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt
    - probe/src/typeIdProbe/kotlin/probe/TypeIdVectors.kt
    - probe/typeid/vectors.json
    - probe/typeid/check-vectors.ts
    - probe/typeid/package.json
    - probe/typeid/package-lock.json
  modified:
    - probe/build.gradle.kts
    - gradle/libs.versions.toml
key-decisions:
  - "Measure Kotlin/Jupiter/Kotest, ktfmt, and TypeID from explicit Gradle tasks with isolated JVM and npm dependencies."
  - "Scope the npm uuid advisory assessment to the temporary TypeID probe. Keep application adoption open and review by 2026-12-02."
patterns-established:
  - "Bind exchanges to the native evidence run and a fresh invocation marker. Validate fixed UUID bytes and exact tag/prefix pairs against independent fixture inputs."
requirements-completed: [FND-01]
coverage:
  - id: D1
    description: "Jupiter executes one named Kotlin test with Kotest assertions and a seeded property."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "python3 probe/verify_secondary.py check kotest"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two ktfmt passes wrap the KDoc and preserve its content and second-pass bytes."
    requirement: FND-01
    verification:
      - kind: other
        ref: "python3 probe/verify_secondary.py check kdoc"
        status: pass
    human_judgment: false
  - id: D3
    description: "The JVM TypeID probe validates the official vectors and emits tagged UUIDv7 pairs."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "python3 probe/verify_secondary.py check typeid-jvm"
        status: pass
    human_judgment: false
  - id: D4
    description: "Kotlin and TypeScript independently verify both directions of the TypeID exchange and reject changed and stale data."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "python3 probe/verify_secondary.py check typeid-exchange"
        status: pass
    human_judgment: false
duration: 21min
completed: 2026-11-25
status: complete
---

# Phase 01 Plan 04: Kotlin and TypeScript Toolchain Probes Summary

**One Jupiter test executed 32 seeded Kotest checks, ktfmt preserved the KDoc across two passes, and independent Kotlin and TypeScript processes exchanged exact TypeID bytes.**

## Performance

| Started (UTC) | Completed (UTC) | Tasks | Implementation files |
|---|---|---|---|
| 2026-11-24 22:57:10 | 2026-11-24 23:18:39 | 3 | 9 |

## Accomplishments

- The named Jupiter case `Jupiter runs a seeded Kotest property` ran on Eclipse Adoptium Temurin `25.0.5.1+2-LTS` (`aarch64`). The worker verified Kotlin `2.4.21`, and Gradle verified the resolved Jupiter engine and launcher `6.1.3` and Kotest assertions and property libraries `6.2.7`. The seeded property used `20261124` and executed all 32 checks.
- ktfmt `0.65` with the `kotlinlang` style wrapped the long paragraph in an ignored copy. The symbol link, separate list entries, fenced lines and spacing, and parameter/return tags were preserved. The first and second formatted copies both had SHA-256 `539206da981249e09a0f9d4aa9bea0dadcd3571d57e38c7127a6908bb4df8106`.
- JVM `de.fxlae:typeid-java:0.3.1` and `typeid-js:1.2.0` independently verified 9 valid and 21 invalid canonical vectors and rejected a valid student ID in the course slot. The source fixture includes its original Apache 2.0 license text. [Jetify TypeID specification and vectors](https://github.com/jetify-com/typeid/tree/cb20c6eeb4bc6e5a115fceffcbb22f331d4033f8/spec)
- The Kotlin and TypeScript sources each encoded separate deterministic UUIDv7 inputs for `courseId` and `studentId`. Each receiver checked the other producer's two original encodings and 16 UUID bytes. Both receivers detected modified prefix and UUID bytes and a stale invocation marker. The consumer requires the TypeScript file.
- Node `v26.13.1`, npm `12.2.3`, and the native `@typescript/typescript-darwin-arm64` compiler `7.0.2` came from the nested Gradle build. Its `npm ci` preserved the TypeID lock at SHA-256 `753722eff1265bec19bdc8b9d4107fb255baead9e2328655f1dd7132a6d57ef4`. The ordinary Gradle dry run scheduled the existing JVM test only. Dependency resolution confirmed that the probe role and Axon integration classpaths excluded the auxiliary libraries.

## Reproduction and Evidence

The current native Axon proof `core-a_nx8teq` anchors the four secondary stage records below. Each recorded a raw exit of `0` and passed artifact and fingerprint validation. The verifier wrote `kotest.json`, `kdoc.json`, and `typeid.json` in the feasibility evidence directory's `secondary` subdirectory.

| Stage | Raw diagnostic command | Evidence |
|---|---|---|
| `kotest` | `./gradlew --console=plain :probe:kotestProbe --rerun-tasks` | Named passing Jupiter case, 32 property checks and worker identity |
| `kdoc` | `./gradlew --console=plain :probe:kdocProbe --rerun-tasks` | Formatted bytes and first/second-pass agreement |
| `typeid-jvm` | `./gradlew --console=plain :probe:typeIdJvmVectors --rerun-tasks` | Canonical checks and Kotlin-origin exchange |
| `typeid-exchange` | `./gradlew --console=plain :probe:typeIdProbe --rerun-tasks` | Two distinct exchanges with 2 verified vectors per direction |

The evidence directory holds exact arguments, sanitized diagnostics and SHA-256 hashes of each captured artifact. JVM and npm verification artifacts stay in ignored build output. FND-01 remains open for the fresh phase verification in Plan 01-05.

## npm Advisory Assessment

On 2026-11-25 the npm registry confirmed Jetify's `typeid-js@1.2.0` and Microsoft's `typescript@7.0.2` as the current releases. Microsoft's TypeScript release pins the platform-specific compiler packages. Each locked npm artifact has SHA-512 integrity metadata and resolves to the official registry. The lock lists no package install scripts. [Jetify npm publisher profile](https://www.npmjs.com/~jetify.com) [Microsoft TypeScript release](https://github.com/microsoft/typescript-go/releases/tag/typescript%2Fv7.0.2)

`npm audit --ignore-scripts --json` exited `1` and returned two Moderate entries with a single underlying advisory, GHSA-w5hq-g745-h8pq / CVE-2026-41907. The report had zero High or Critical entries. The locked `uuid@10.0.0` is within Jetify's `^10.0.0` dependency range. That range contains no fixed release. [uuid upstream advisory](https://github.com/uuidjs/uuid/security/advisories/GHSA-w5hq-g745-h8pq)

The build maintainer owns this temporary assessment for `probe/typeid` and will review by 2026-12-02 at the latest. The installed Jetify ESM bundle imports only `uuid.stringify` and `uuid.v7`. The probe uses `TypeID.fromUUIDBytes`, `fromString`, `toUUIDBytes`, and `toString` on fixed byte inputs and parsed suffixes. The affected `v3`, `v5`, and `v6` APIs with caller-supplied output buffers are outside those paths. Reassess immediately if the probe's API or input surface changes. When a verified Jetify release selects a patched `uuid`, refresh the lock, rerun `npm audit --ignore-scripts --json` and `./gradlew --console=plain :probe:typeIdProbe --rerun-tasks`, and remove this assessment after confirming the finding is cleared. Application TypeScript TypeID dependency selection remains open.

## Task Commits

| Task | RED | GREEN |
|---|---|---|
| Jupiter/Kotest and ktfmt/KDoc | `077ebbb` | `db297a2` |
| JVM TypeID vectors | `36f8bd2` | `c3ecf8d` |
| Kotlin and TypeScript exchange | `d85cbec` | `109d6b1` |

## TDD Gate Compliance

- Task 1 returned `RED_EVIDENCE_OK` from JUnit XML. The named Jupiter test completed the seeded property and failed on the missing selected Kotlin version in the worker. GREEN supplied the selected version and verified the worker and JUnit artifact.
- Task 2 returned `RED_EVIDENCE_OK` from JUnit XML. The case verified the canonical fixtures and failed because the decoder accepted a valid student ID for the course slot. GREEN added the prefix check and exercised the exchange.
- Task 3 returned `RED_EVIDENCE_OK` from Node TAP. The compiled checker passed the canonical cases and rejected the real inbound exchange because the expected invocation marker was absent. GREEN supplied the independent marker and verified both directions.

## Deviations from Plan

Canonical evidence was captured once after the final build and dependency inputs stabilized. Each task's executable checks ran during implementation. The final capture refreshed the required native proof and ran all four diagnostics for the final fingerprint.

## Issues Encountered

The TypeID `uuid` advisory remains limited to the scope and review trigger above. The compatibility stages passed.

## Next Phase Readiness

Plan 01-05 can recapture all required and secondary evidence and publish the permanent feasibility report. The shared build and application dependency decisions belong to their later phases.

## Self-Check: PASSED

All nine declared implementation files exist, all six task commits are reachable, and all four evidence checks validated against the current native proof.
