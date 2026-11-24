---
phase: 01-axon-server-and-toolchain-feasibility
plan: "02"
subsystem: testing
tags: [axon-server, dcb, subscription-query, gradle, temurin, evidence]
requires:
  - phase: "01-01"
    provides: "The checksum-verified wrapper and native remote tagged-write tracer."
provides:
  - "Native two-tag DCB rejection, remote projection and subscription query proof."
  - "Bounded success and controlled-failure cleanup with a public probe guide."
  - "Docker-free serialization smoke test and renewable secondary evidence preflight."
affects: [01-03, 01-04, 01-05]
actuals:
  tokens: 30378
  tasks: 3
  commits: 6
commits: 6
plan_head_before: da45a18228f14d8df27aea3e2f586ec9e473212a
plan_head_after: aaac408af73f306fb85b4f1f07f39cc509fa9445
tech-stack:
  added: [Reactor Core 3.9.0]
  patterns: [Explicit probe roles, scoped resource cleanup, versioned evidence fingerprints]
key-files:
  created:
    - .java-version
    - probe/README.md
    - probe/src/main/kotlin/probe/ProbeProjection.kt
    - probe/src/integrationTest/kotlin/probe/ProbeFixture.kt
    - probe/src/test/kotlin/probe/ProbeContractsTest.kt
    - probe/verify_secondary.py
  modified:
    - gradle/libs.versions.toml
    - probe/build.gradle.kts
    - probe/src/main/kotlin/probe/ProbeApplication.kt
    - probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt
key-decisions:
  - "Give the phased projection an isolated token store and resolve its pooled processor from the Axon event processor module."
  - "Use .java-version as the Temurin feature owner and validate each secondary stage against a complete current native core proof."
patterns-established:
  - "Hold a remote subscription open before dispatching a winner, then await the exact stale commit refusal."
  - "Pair core case transcripts with original JUnit output and archive every secondary stage attempt with hashed evidence."
requirements-completed: [FND-01]
coverage:
  - id: D1
    description: "A native server rejects a partially overlapping append and the pre-existing remote subscription observes its sole persisted winner."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :probe:integrationTest --tests 'probe.AxonProbeTest.overlapping writes leave one winner and notify the remote subscriber' --rerun-tasks"
        status: pass
    human_judgment: false
  - id: D2
    description: "Success and a forced exception cancel subscriptions and release the owned JVMs and container."
    requirement: FND-01
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :probe:integrationTest --rerun-tasks"
        status: pass
    human_judgment: false
  - id: D3
    description: "A Docker-unreachable ordinary build executes the case-sensitive serializer smoke test, and the evidence CLI verifies native core provenance."
    requirement: FND-01
    verification:
      - kind: unit
        ref: "env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain build --rerun-tasks"
        status: pass
      - kind: other
        ref: "python3 probe/verify_secondary.py self-test"
        status: pass
      - kind: integration
        ref: "python3 probe/verify_secondary.py ensure-core"
        status: pass
    human_judgment: false
duration: 82min
completed: 2026-11-24
status: complete
---

# Phase 01 Plan 02: Native DCB Probe Summary

**Three Temurin JVMs observed one durable winner, an explicit stale append refusal and the winning update on an already-open remote subscription.**

## Performance

- Started at 2026-11-24T14:54:51Z and finished at 2026-11-24T16:16:50Z.
- Completed three tasks across ten files in 82 minutes, including verification and approval waits.

## Accomplishments

- The driver read an empty `default` DCB context and observed terminal marker `0`. The command committed the two-tag winner before the driver's stale append reached its own commit boundary. The server returned `AppendEventsTransactionRejectedException`, gRPC `CANCELLED` and `ConsistencyConditionException`. The course, winning student, joint criterion and full history each returned the same sole winner. The losing student's history was empty.
- The remote worker, writer and projection had distinct PIDs and server client registrations. The direct baseline, original subscription initial result, live update and final direct query reported counts `0, 0, 1, 1`, with the winning event ID on both updated results. The fixture used clean role homes and no supplied Axoniq credentials for the short functional proof. Publisher terms and renewal behavior remain separate evidence for the final report.
- Two full ARM64 runs after the cleanup work took 90 and 87 seconds, each with three executed tests and zero skips, errors or failures. The success and forced-failure cases began empty in four distinct containers. Startup took roughly 20 seconds per server and cleanup took 2.7–3.8 seconds. The forced case preserved a separate Docker network.
- The ordinary build ran one passing Jupiter contract test with Docker pointed at an unreachable loopback endpoint. Its dry-run included `:probe:test` and omitted integration and image tasks. Kotlin emitted Java 25 class files. The Gradle launcher, ordinary worker and three native probe roles used Temurin `25.0.5.1+2-LTS`. Native proof ran on Linux/ARM64 Docker 29.5.2 during cleanup verification and 29.10.0 after the final toolchain change.
- The application and ordinary test runtime graphs had no Testcontainers. The integration graph resolved Testcontainers. The resolved KGP version and Gradle 9.9.2's embedded Kotlin each reported 2.4.21 through their separate version owners.
- The final native suite passed after the toolchain change. The helper then regenerated a passing live proof under run `core-pn0zboz1` and reused its validated provenance from the sandbox. It verified the original JUnit, the three matched transcripts and native image identities. The self-test exercised passing, repeated blocker, environmental and prerequisite dispositions, along with stale inputs, a single failed attempt, unsupported status, corruption and a failing required core.

## Task Commits

| Task | RED | GREEN |
| --- | --- | --- |
| Remote stale overlap and subscription | `05f5d0e` | `dd863d8` |
| Bounded cleanup and guide | `8eb2e7b` | `070b4f9` |
| Build isolation and evidence checker | `7a60926` | `aaac408` |

## TDD Gate Evidence

- Task 1 failed the planned assertion after a real server dispatch because the distinct projection had no registration. The completed test proved the separate projection, actual server refusal and live update. JUnit evidence returned `RED_EVIDENCE_OK`.
- Task 2 opened the remote subscription and failed after the controlled exception because fixture cleanup omitted upstream cancellation. The completed suite observed cancellation and the owned resource exits in both paths. JUnit evidence returned `RED_EVIDENCE_OK`.
- Task 3 round-tripped the real Axon Jackson contracts, then failed because the ordinary worker lacked the toolchain-owner value. The completed case proved case-sensitive tags and the selected isolated worker. JUnit evidence returned `RED_EVIDENCE_OK`.

## Deviations from Plan

- **[Rule 3 — Runtime dependency]** Axon 5.4.2 reached the real subscription path and threw `NoClassDefFoundError: reactor/core/publisher/FluxSink`. Added the scoped `reactor-core` alias and runtime dependency in `dd863d8`. The Spring Boot 4.2.0 BOM resolved Reactor 3.9.0 and the live subscription passed.
- **[Rule 3 — Processor readiness]** Spring's pooled processor required an explicit token store and registered in module `EventProcessor[probe]`. The projection now waits for that processor's real status in `dd863d8`. The runtime identity check follows the active intercepting bus wrappers to their actual distributed delegates.
- **[Rule 2 — Version ownership]** The Task 3 toolchain change removed the obsolete JDK feature entry from the catalog and derived the integration role comparison from the configured worker feature in `aaac408`. No catalog JDK consumers remain.

## Next Plan Readiness

The stage CLI reads the stage-specific `PROBE_SECONDARY` JSON line and snapshots its listed supporting files inside the active evidence directory. The producer fields are documented in `verify_secondary.py`. Scoped build and image evidence is in ignored `probe/build/reports/feasibility/`. FND-01 remains open for the secondary plans and final Phase 01 verification.

## Self-Check: PASSED

All six RED and GREEN commits are reachable and the ten changed files exist. The final core provenance validates its three passing case transcripts and JUnit XML against the current checkout.
