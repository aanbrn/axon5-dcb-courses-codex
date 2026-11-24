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
| Quick run | `./gradlew --console=plain :probe:test` after 01-02 Task 3 provisions the smoke test. |
| Required full run | `./gradlew --console=plain :probe:integrationTest --rerun-tasks` on native ARM64 with clean state. |
| Docker-free graph | `./gradlew --console=plain build --dry-run` omits `:probe:integrationTest` and Docker image tasks. |
| Runtime | Target a warm integration run within five minutes once dependencies and images are present. Measure and report cold setup separately. |

## Sampling Rate

- Run the affected compile, test, or tool task after each runnable change. Use deterministic source checks before the wrapper is provisioned.
- Run the core Docker command after any change to its wiring, selected dependencies, or runtime image, with hard bounds and fixture cleanup.
- Before FND-01 verification, rerun the required command from the public instructions and reconcile the secondary outcomes with the report.
- Optional tooling checks may produce a successful result, reproducible blocker, or environmental `Unverified` outcome with a retry trigger. An environmental change or deterministic failure in the required DCB proof blocks phase sign-off until the proof passes.

## Per-Plan Verification Map

Use the checks below from the repository root. The first task verifies the candidate Gradle distribution before the wrapper exists. Commands using `./gradlew` apply after 01-01 Task 2 has generated and verified it. Run the actual gate even where the table also calls for reviewing documentation or diagnostics.

| Plan/task | Observable outcome and threat ref | Command or evidence | Status |
| --- | --- | --- | --- |
| 01-01 T1 | Cold native credential-free remote command and durable event, applicable terms, immutable image index and distinct runnable ARM64/AMD64 child metadata. T-01-01, T-01-02 | `gradle --console=plain :probe:integrationTest --tests 'probe.AxonProbeTest.a remote command persists a tagged event' --rerun-tasks` | Pending |
| 01-01 T2 | Same tracer via verified wrapper. T-01-01 | `./gradlew --console=plain :probe:integrationTest --tests 'probe.AxonProbeTest.a remote command persists a tagged event' --rerun-tasks` | Pending |
| 01-02 T1 | Real conflict at commit, same durable winner under both tags, absent loser, remote command/query, initial result and correlated update. T-01-03 | `./gradlew --console=plain :probe:integrationTest --tests 'probe.AxonProbeTest.overlapping writes leave one winner and notify the remote subscriber' --rerun-tasks` | Pending |
| 01-02 T2 | Bounded cleanup after success and forced failure, distinct empty starting states. T-01-04 | `./gradlew --console=plain :probe:integrationTest --rerun-tasks` twice | Pending |
| 01-02 T3 | Persistent Temurin feature owner, secondary preflight and smoke test in an ordinary build with unreachable Docker. Selected toolchain and actual worker/role identities | `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain build --rerun-tasks` plus the full native suite and `python3 probe/verify_secondary.py self-test` | Pending |
| 01-03 T1 | Reproducible checked input and deterministic static asset | `python3 probe/verify_secondary.py check frontend-fixture` | Pending |
| 01-03 T2 | Gradle uses the selected Node/npm, clean lockfile and staged bytes | `python3 probe/verify_secondary.py check frontend-assets` | Pending |
| 01-03 T3 | Native Paketo image serves two distinguishable staged assets and cleans up. T-01-05, T-01-06 | `python3 probe/verify_secondary.py check frontend-image` | Pending |
| 01-04 T1 | Named Jupiter test with Kotest matcher/seeded property. ktfmt expected delta, preserved KDoc and idempotence | `python3 probe/verify_secondary.py check kotest` and `python3 probe/verify_secondary.py check kdoc` | Pending |
| 01-04 T2 | JVM canonical TypeID encodings and malformed/wrong-prefix rejections | `python3 probe/verify_secondary.py check typeid-jvm` | Pending |
| 01-04 T3 | Independent JVM→TS and TS→JVM exchanges verify 16 bytes and prefix. T-01-07 | `python3 probe/verify_secondary.py check typeid-exchange` | Pending |
| 01-05 T1 | Both verifier modes complete before capture. Clean hard gate, four independent secondary statuses, actual resolved graphs, prior review and private check scope. T-01-08 | `python3 probe/verify_evidence.py --capture --evidence probe/build/reports/feasibility` | Pending |
| 01-05 T2 | Documentation-only changes checked with the captured verifier. Permanent report, exact terms and future AMD64/retirement criteria agree with observed results. T-01-09 | `python3 probe/verify_evidence.py --evidence probe/build/reports/feasibility --report docs/feasibility/phase-01.md` plus source review | Pending |

## Local evidence contract

Each producer uses `probe/build/reports/feasibility/` for ignored evidence. Use the same evidence root for all producers in a run. In 01-05, `--capture` uses a fresh `runs/<runId>/` subdirectory and exports `PROBE_EVIDENCE_DIR` and `PROBE_RUN_ID` to every child; outside acceptance the helper manages a local iteration ID. The report checker consumes results scoped to that run. Creating the directory or filling a template is insufficient for a passing result.

- `core.json` associates the most recent complete run with its JUnit case, UTC start/finish, run and event IDs, remote identities, positive and negative tag reads, explicit conflict type, subscription and direct-query observations. The case records empty initial history, actual process architecture, effective DCB engine, isolated credential sources and lifecycle observations. Capture the live data before teardown. Pair it with the JUnit XML from `probe/build/test-results/integrationTest/` for the same invocation.
- `images.json` records the registry index and runnable child descriptors/config IDs, Docker host/server platform, pulled/running ARM64 config and lookup time. `build-graph.txt` is the real output of `./gradlew --console=plain build --dry-run`. Keep filtered sources or safe derived fields for publisher terms and actual Gradle resolution alongside these files.
- `secondary/{frontend,typeid,kotest,kdoc}.json` records the observed status, exact command(s), selected inputs, stage and supporting output or diagnostic. `Pass` requires every outcome assertion. `Blocked` requires a repeated matching failure in the same controlled configuration. `Unverified` requires the attempted command, environmental cause and a concrete retry condition. Preserve the underlying exit codes for all three statuses. Each producing plan writes its own stage records. Plan 05 regenerates every one for the acceptance run in the current checkout. Never translate a failed required runtime or permission gate into a secondary status.

### Secondary outcome commands

Plan 01-02 Task 3 supplies the following interface before Plans 03 and 04 use it. For every secondary stage, invoke `python3 probe/verify_secondary.py ensure-core` first. The helper's run, classify and check entry points also use this preflight. Check the native core run against the current checkout inputs and tuple, its complete passing JUnit suite and associated transcript. If evidence is missing or stale, automatically run `./gradlew --console=plain :probe:integrationTest --rerun-tasks` in the same checkout and capture the newly verified provenance in the active evidence directory. A failed or incomplete required run immediately blocks secondary collection and acceptance. Recollect stages whose provenance changed. Each later task implements its fixture assertions and runs the exact raw diagnostic from its action. During acceptance the capture reads the same stage inputs and runs the same commands.

| Command | Result |
| --- | --- |
| `python3 probe/verify_secondary.py ensure-core` | Validate native core provenance, rebuilding it in this checkout when missing or stale. Return nonzero for a failed or incomplete required proof. |
| `python3 probe/verify_secondary.py run STAGE -- COMMAND [ARGS...]` | Launch COMMAND with the selected tools, capture actual argv/exit/timing, success observations and redacted diagnostic evidence. Successful capture may return zero even if COMMAND failed. The stored raw exit remains authoritative. |
| `python3 probe/verify_secondary.py classify STAGE Pass` | Select the measured success for validation. |
| `python3 probe/verify_secondary.py classify STAGE Blocked --reason TEXT --retry TEXT` | Retain two independent comparable failed attempts with the same command, tuple and first failure signature. |
| `python3 probe/verify_secondary.py classify STAGE Unverified --cause TEXT --retry TEXT` | Attach observed environmental diagnostic and retry condition. Record the attempted invocation and launch error even if the executable never started. |
| `python3 probe/verify_secondary.py classify STAGE STATUS --prerequisite STAGE_ID --pending-command TEXT --reason TEXT --retry TEXT` | Carry forward a verified non-pass only when the earlier stage's failure prevents this command. The checker computes the prerequisite record hash, validates the dependency and retains the exact pending diagnostic. |
| `python3 probe/verify_secondary.py check STAGE` | Recompute the record and referenced evidence hashes, validate the actual scope/inputs, require working downstream code or identify generated outputs prevented by the concrete prerequisite, then return zero only for a supported outcome with a passing required core proof. |
| `python3 probe/verify_secondary.py self-test` | Exercise the positive, negative and prerequisite classification cases using temporary fixtures. |

Store one `stages/<stage>.json` record for each of `frontend-fixture`, `frontend-assets`, `frontend-image`, `kotest`, `kdoc`, `typeid-jvm` and `typeid-exchange`. Required fields are `runId`, `stage`, `inputSha256`, `coreTupleSha256`, `coreEvidenceSha256`, `status`, `attempts` and `observations`. Every attempt includes argv, start/end UTC, actual tool versions, raw exit (null only for a captured launch error), diagnostic/signature and SHA-256 of referenced local output. Store `cause`, `retry`, `prerequisiteStage`, `prerequisiteRecordSha256` and `pendingCommand` where applicable. A dependent stage with no attempt must have a verified causal non-pass for the same run and applicable inputs. A downstream prerequisite record cannot claim Pass. A reproducible fixture implementation defect requires repair.

Pass validates affirmative fixture-specific evidence: distinct marker outputs and intact lockfile for the static fixture, provisioned tool versions and the validated staged tree for Gradle assets, both matching native HTTP responses for packaging, a named nonzero Jupiter execution and seeded property, two ktfmt passes preserving the KDoc content, positive/negative canonical JVM vectors, or two genuine TypeID language exchanges as appropriate. Malformed records, absence of work, stale evidence, unsupported prerequisites or a failed core proof make the check exit nonzero. Independent stages must still be attempted. Summarize each complete sample from its own stage chain in the four `secondary/*.json` records.

### Acceptance run manifest

In the current checkout, `--capture` allocates an empty run root and recomputes the input tree SHA-256 from relevant file paths and bytes (wrapper, version owners, Gradle scripts, role/fixture/verifier source, manifests, lockfiles and sample inputs, including modified/untracked ones). Both verify_evidence.py modes and verify_secondary.py are complete and included before capture. Exclude the documentation outputs `docs/feasibility/phase-01.md` and `probe/README.md` from this execution digest. The immutable `--report` checks their fields and links independently in Task 2. Record Git revision separately. In `manifest.json`, bind the run ID, start/end time, tested input hashes, actual tool/runtime tuple, and each invocation and raw exit to the content SHA-256 of its evidence. Include the Docker-unreachable build/smoke result, freshly captured dry-run graph, raw OCI index and runnable child/config identities, running ARM64 image, matched JUnit XML and transcript, all stage diagnostics/prerequisite references and four secondary outcomes. The capture fails if an input changes in flight or any signed-off input/output is foreign, stale, missing or inconsistent. Recompute hashes at report verification using the manifest/run ID in the report. Preserve fresh raw statuses even when a secondary outcome is acceptable.

## Planning coverage

| Source | Item | Plans that implement the check |
| --- | --- | --- |
| GOAL | Maintainer selects the stack using a repeatable DCB proof and targeted tooling checks | 01–05 |
| REQ | FND-01, including exact evidence and bootstrap before stack adoption | 01, 02, 05 |
| RESEARCH | Current stable/LTS candidates, KGP/Gradle support boundary, both Axon distributions, exact terms, immutable registry and actual native JVMs | 01, 05 |
| RESEARCH | Real marker and awaited commit, OR between criteria, remote initial/update sequencing, lifecycle and build isolation | 01, 02 |
| RESEARCH | Independent JVM, TypeID, KDoc and static native image checks, including package legitimacy and observed blockers | 03, 04, 05 |
| RESEARCH | Prior Guava/pgJDBC and image review notes, private report scope and architecture handoff | 05 |
| CONTEXT | D-01–D-04 temporary module, scenario, guide, durable report and native/metadata distinction | 01, 02, 05 |
| CONTEXT | D-05–D-06 first hosted AMD64 evidence and later retirement conditions | 05, report and handoff |
| CONTEXT | D-07–D-10 secondary outcome rules, npm/lockfile and buildpack ownership | 03, 04, 05 |
| CONTEXT | D-11–D-13 credential-free launch, limits, version choice and earlier review evidence | 01, 02, 05 |

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
