---
phase: "01"
slug: axon-server-and-toolchain-feasibility
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-24"
---

# Phase 01 Validation Strategy

## Test Infrastructure

| Property | Value |
| --- | --- |
| Framework | JUnit Jupiter 6 and Testcontainers. Kotlin, npm, ktfmt, and Pack secondary samples run through explicit Gradle tasks. |
| Config file | Root Gradle Wrapper and `probe/build.gradle.kts`, provisioned by the first plan. |
| Quick run | `./gradlew --console=plain :probe:test` once the task and tests are present. |
| Required full run | `./gradlew --console=plain :probe:integrationTest` on native ARM64 with clean state. |
| Docker-free graph | `./gradlew --console=plain build --dry-run` omits `:probe:integrationTest` and Docker image tasks. |
| Runtime | Target a warm integration run within five minutes once dependencies and images are present. Measure and report cold setup separately. |

## Sampling Rate

- Run the affected compile, test, or tool task after each runnable change. Use deterministic source checks before the wrapper is provisioned.
- Run the core Docker command after any change to its wiring, selected dependencies, or runtime image, with hard bounds and fixture cleanup.
- Before FND-01 verification, rerun the required command from the public instructions and reconcile the secondary outcomes with the report.
- Optional tooling checks may produce a successful result, reproducible blocker, or environmental `Unverified` outcome with a retry trigger. An environmental change or deterministic failure in the required DCB proof blocks phase sign-off until the proof passes.

## Per-Plan Verification Map

Bind the following checks to concrete plan/task IDs in the finalized plan files. Each task provides its own `<automated>` verification and `<fails_when>` criterion.

| Check | Requirement | Secure Behavior | Test Type | Automated Command or Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| Candidate input, terms, and architecture | FND-01, D-04, D-11–D-13 | Official inputs, immutable image evidence, no ambient credential claims | Registry and source inspection | Resolve the OCI index and runnable ARM64/AMD64 child manifests. Inspect candidate metadata, license and connector terms and preserve public links. | Pending |
| Clean DCB proof | FND-01, D-01–D-04, D-11 | Disposable state and bounded cleanup. Real multi-tag commit and stale conflict. | Integration | `./gradlew --console=plain :probe:integrationTest` | Pending |
| Docker-free ordinary build | FND-01, D-01 | Docker-backed checks stay opt-in | Build graph | `./gradlew --console=plain build --dry-run` | Pending |
| TypeID interoperability | D-07–D-08 | Reject malformed encodings and wrong expected prefix in the sample | Cross-language fixture | `./gradlew --console=plain :probe:typeIdProbe` | Pending |
| JUnit and Kotest interop | D-07–D-08 | Confirm a real Jupiter test executed with a bounded seeded property | JVM test | `./gradlew --console=plain :probe:kotestProbe` | Pending |
| ktfmt KDoc | D-07–D-08 | Preserve documentation content and establish idempotence | Formatting fixture | `./gradlew --console=plain :probe:kdocProbe` | Pending |
| Frontend static packaging | D-07–D-10 | Lockfile unchanged, produced assets served by the generated image | Build and local smoke | `./gradlew --console=plain :probe:frontendAssets :probe:frontendImageProbe` | Pending |
| Durable evidence and handoff | FND-01, D-03, D-05–D-06, D-12–D-13 | Public report contains redacted evidence and differentiates ARM64 runtime from AMD64 metadata | Report review and fresh rerun | Match actual commands, graph, terms, platform digests, results, and future retirement conditions to the committed artifacts. | Pending |

## Wave 0 Requirements

- [ ] Add a checksummed Gradle Wrapper and minimal Kotlin/Spring build for the probe.
- [ ] Provision the JUnit suite, clean scoped Testcontainers launcher, application role fixtures, readiness checks, and cleanup.
- [ ] Add the secondary fixture tasks before running their verification commands.

## Manual-Only Verifications

| Behavior | Requirement | Why manual | Instructions |
| --- | --- | --- | --- |
| Confirm intended use of the exact image and connector | FND-01, D-11–D-13 | Publisher terms and entitlement interpretation require source review. | Check exact publisher terms, date, resolved artifacts, and runtime evidence. Record the unlicensed limit and any detected network dependency. |
| Evaluate evidence for a non-passing secondary | D-07–D-08 | Classification depends on the first observed failure and stage. | Retain a reproducible command and redacted result or a concrete environmental cause and retry trigger. |

## Validation Sign-Off

- [ ] Task verifiers are runnable and have explicit failing directions.
- [ ] The required ARM64 integration proof and Docker-free graph are green.
- [ ] All four secondary probes have an evidenced outcome and any retry trigger.
- [ ] The report scopes the image metadata and runtime evidence, records terms, and preserves the AMD64 and probe-retirement conditions.

**Approval:** Pending execution evidence.
