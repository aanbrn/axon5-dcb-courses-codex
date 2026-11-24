---
phase: 01-axon-server-and-toolchain-feasibility
plan: "01"
subsystem: testing
tags: [axon-server, dcb, gradle, kotlin, testcontainers]
requires: []
provides:
  - A native ARM64 tracer that dispatches a remote command and reads its committed event by both tags.
  - A checksum-verified Gradle 9.9.2 wrapper and an opt-in JUnit integration suite.
affects: [01-02, 01-03, 01-04, 01-05]
actuals:
  tasks: 2
  commits: 4
tech-stack:
  added: [Gradle 9.9.2, Kotlin 2.4.21, Spring Boot 4.2.0, Axon Framework 5.4.2, Axon Server 2026.1.8, Testcontainers 2.0.5]
  patterns: [Isolated JVM Test Suite, independent DCB tag reads, immutable platform child selection]
key-files:
  created:
    - settings.gradle.kts
    - gradle/libs.versions.toml
    - probe/build.gradle.kts
    - probe/src/main/kotlin/probe/ProbeApplication.kt
    - probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt
    - gradlew
    - gradlew.bat
    - gradle/wrapper/gradle-wrapper.jar
    - gradle/wrapper/gradle-wrapper.properties
  modified: []
key-decisions:
  - Continue testing with Gradle 9.9.2 after successful native runs with Kotlin 2.4.21 and Temurin 25.
  - Await both the management endpoint and the default replication group leader before starting clients.
patterns-established:
  - Use server-side handler registrations and separate PIDs to prove traffic reached the remote command role.
  - Select and validate the native child from an immutable image index and record the AMD64 child as metadata.
requirements-completed: [FND-01]
coverage:
  - id: D1
    description: A remote command persists one event readable under both tags in a clean native server.
    requirement: FND-01
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :probe:integrationTest --tests 'probe.AxonProbeTest.a remote command persists a tagged event' --rerun-tasks"
        status: pass
    human_judgment: false
duration: 60min
completed: 2026-11-24
status: complete
---

# Plan 01-01 Summary

A separate command JVM committed the same event independently read under `courseId` and `studentId` through Axon Server on ARM64.

## Accomplishments

- The failing tracer reached the server and the remote handler, then found zero tagged events. The implementation replayed the test and returned the same new event identifier from both independent tag reads.
- The server and both JVMs started with clean state and without supplied vendor credentials. Both clients used the `default` DCB context and `AxonServerEventStorageEngine`. JUnit reported one test, zero skipped, zero failures, and zero errors in the final wrapper run.
- Gradle 9.9.2 used Temurin `25.0.5.1+2-LTS` and compiled Kotlin `2.4.21`. The wrapper JAR matched the published SHA-256 `621008afc4f5d59357fcf06ffa644dd5aade5e091bdc363742710445f73cdaf8`. A fresh Gradle home obtained and verified the distribution against `971fcd7150ca4ba04852c0b2ca0d2d0ab9468e14b03473eab19528809914c76b`. [Gradle release checksums](https://gradle.org/release-checksums/)
- Axon Server 2026.1.8 ran as the `linux/arm64` child of index `sha256:57b6ad30353cc0df1612d6a30be03a1df85b4b49b5f2feee218a70d1cb7794c2`. The ARM64 child was `sha256:463d3a60cecbe0301860924ea3eaef5b0d6e3b8a4fd26e8b9cc82e9df7ab7bf4`. The AMD64 child was `sha256:6c7646628da238d3e2ac5ff58e271e0ebbeab924f8027858eda711804d200a42` and was inspected as registry metadata.

## Task Commits

1. Remote tagged write tracer: `d80c8ad`, `9efbfe6`, and `cfde569`.
2. Verified wrapper: `508fa33`.

The prose test name and exact Gradle filter were changed together in `b72a951`. The final wrapper run verified the renamed test.

## Issues Encountered

- The management endpoint became ready before the `default` group elected a leader and the first run returned `AXONIQ-1302`. Readiness now checks both conditions.
- The AxonIQ starter brought `axoniq-testcontainer` into the command runtime. An exclusion on the starter dependency removes that single convenience module. Gradle `dependencyInsight` found no match on `:probe:runtimeClasspath`, and the isolated integration test still ran with Testcontainers.
- The server logged unregistered mode and a scheduled shutdown after 12 hours, consistent with vendor runtime documentation. The evaluation grant for designated unregistered software is separate from the shutdown timer. The commercial connector and starter carry Axoniq terms. Vendor development permission and anonymous egress behavior for licensed application modules are separate from the server behavior. The short tracer checks credential-free startup during its run. Renewal, no-egress behavior, the concurrent append, and remote subscription queries remain outside this tracer's evidence. [Axoniq Terms of Service](https://www.axoniq.io/legal/terms-of-service) · [Axoniq licensing](https://docs.axoniq.io/axoniq-platform-reference/licensing/) · [Rotation and expiry](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/)

## Next Plan Readiness

The wrapper and native DCB tracer are ready for the overlapping-append and remote subscription proof in Plan 01-02. FND-01 remains open until Phase 1 acceptance.

## Self-Check: PASSED

- The wrapper and all declared implementation files are committed.
- The filtered integration test executed and passed on ARM64 after the runtime graph change.
- The running image ID matched the published ARM64 configuration digest.
