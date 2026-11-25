---
phase: 01-axon-server-and-toolchain-feasibility
verified: 2026-11-25T00:41:04Z
status: passed
score: 18/18 must-haves verified
covered_files: [
  ".gitignore",
  ".java-version",
  ".nvmrc",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-01-PLAN.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-01-SUMMARY.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-02-PLAN.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-02-SUMMARY.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-03-PLAN.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-03-SUMMARY.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-04-PLAN.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-04-SUMMARY.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-05-PLAN.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-05-SUMMARY.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-CONTEXT.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-REVIEW-DISPOSITION.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-REVIEW.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-SECURITY.md",
  ".planning/phases/01-axon-server-and-toolchain-feasibility/01-VALIDATION.md",
  "AGENTS.md",
  "docs/feasibility/phase-01.md",
  "gradle/libs.versions.toml",
  "gradle/wrapper/gradle-wrapper.jar",
  "gradle/wrapper/gradle-wrapper.properties",
  "gradlew",
  "gradlew.bat",
  "mise.toml",
  "probe/README.md",
  "probe/build.gradle.kts",
  "probe/kdoc/Specimen.kt",
  "probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt",
  "probe/src/integrationTest/kotlin/probe/ProbeFixture.kt",
  "probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt",
  "probe/src/main/kotlin/probe/ProbeApplication.kt",
  "probe/src/main/kotlin/probe/ProbeProjection.kt",
  "probe/src/test/kotlin/probe/ProbeContractsTest.kt",
  "probe/src/typeIdProbe/kotlin/probe/TypeIdVectors.kt",
  "probe/typeid/check-vectors.ts",
  "probe/typeid/package-lock.json",
  "probe/typeid/package.json",
  "probe/typeid/vectors.json",
  "probe/verify_evidence.py",
  "probe/verify_secondary.py",
  "probe/web/build.gradle.kts",
  "probe/web/build.mjs",
  "probe/web/package-lock.json",
  "probe/web/package.json",
  "probe/web/settings.gradle.kts",
  "settings.gradle.kts"
]
covered_digest: "v4:sha256:fb72bb0f832d305f65bd6fd312ec8e9141af1febe6e7e68432c18c143bf0b822"
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 13
  total: 13
  not_honored: []
human_verification: []
---

# Phase 01 Verification Report

**Phase goal**

As a maintainer, I want to select a compatible stack by running a repeatable DCB probe and targeted toolchain checks, so that readers can reproduce the stack selection.

**Status** `passed` · **Mode** MVP · **Verification** Initial

## User Flow Coverage

| Step | Expected | Evidence | Status |
| --- | --- | --- | --- |
| Follow the [probe guide](../../../probe/README.md) on native ARM64 | The wrapper starts a clean local DCB context without requiring a vendor account, license file or Platform token | The retained wrapper output, server log and JUnit trace show the native container, unregistered startup and usable context | Verified |
| Read the native trace | The maintainer sees a remote tagged commit, an overlapping append rejected by Axon Server and a live update followed by the same direct-query result | Three registered JVMs on distributed buses. The course, winning student, joint and history reads all return the committed event. The losing student has no event. The update and fresh query carry the same event ID. | Verified |
| Reproduce the toolchain and compare the version owners | The four samples run through their documented entry points, and the report explains the selection and its measured scope | Seven successful secondary stages and a report checker that validates the retained outputs against the checked-in source and version owners. [Feasibility record](../../../docs/feasibility/phase-01.md) | Verified |
| Reproduce the stack selection | A reader can recover the commands, tested revision and exact artifacts and distinguish measured results from pending work | `acceptance-nvahwpkb` binds the inputs and observed results. The report records architecture, terms, dependency scope and the hosted handoff. | Verified |

## Goal Achievement

The verifier ran the report check against the retained `acceptance-nvahwpkb` directory. It exited 0 on the actual manifest, JUnit XML, command outputs, secondary observations and OCI files from tested revision `0f3101a5d7195f2c5d9d26d42e95849232a8028d`. No executable source changed between that revision and the reviewed phase head, `3fe3b95`. The report check recomputes the current execution-input hash.

The publication check confirmed that reproduction revision `6af08e257c63673114afbd3d9d9c511a9507565b` has the same Git tree as the tested revision. The report check passed again with the published reproduction link.

### Observable Truths

| Contract | Truth | Status | Evidence |
| --- | --- | --- | --- |
| Roadmap 1 | A clean, registration-free native ARM64 Spring Boot probe demonstrates a multi-tag write, overlapping append rejection and cross-process command, query and subscription update. | Verified | `integration-junit.xml` has three active cases with zero failures, errors or skips. `AxonProbeTest.kt:95` asserts the full path. `ProbeFixture.kt:76` checks live ARM64 identity and unregistered startup. |
| Roadmap 2 | The record specifies exact artifacts, publisher terms, bootstrap, both selected child digests, observed Temurin and earlier dependency findings. The dated matrix starts with stable/LTS candidates and explains any fallback. | Verified | The feasibility report reconciles version owners, resolved graphs, publisher documents and hashed OCI files. Temurin `25.0.5.1+2-LTS` appears across the measured JVMs. The starting Gradle/Kotlin pair passed, with the published KGP support-range difference documented. |
| Roadmap 3 | Independent samples give reproducible outcomes for Kotlin/TypeScript TypeID, Kotlin 2.4/JUnit 6/Kotest, KDoc/ktfmt and Gradle/npm/Paketo static packaging. | Verified | All seven producer records show first-attempt exit 0. The verifier checked their JUnit, TypeID exchanges, formatted KDoc, staged bytes and native HTTP response artifacts. |
| 01-01 | `:probe:integrationTest` identifies the separate handler and reads the committed event independently by course and student. | Verified | The named tracer case validates an empty initial history, the remote receipt and both matching durable reads. `AxonProbeTest.kt:64`. |
| 01-01 | The clean native run needs no vendor registration, supplied license or Platform token. Server and application terms are traceable separately. | Verified | Real startup logs, worker and child isolation, and exact server, Framework and Java transport terms in the report. See the negative guarantees below. |
| 01-01 | The wrapper, runtime artifacts and JVMs can be recovered from the dated candidate evaluation. | Verified | Checked wrapper SHA-256 and distribution pin, observed `--version`, JVM fingerprints and resolved selection commands. [Gradle release checksums](https://gradle.org/release-checksums/) |
| 01-02 | The stale writer with the same course and a different student receives an explicit server rejection, and every relevant successful read finds the same sole winning event. | Verified | Captured empty-history marker 0 before the successful command. Subsequent commit returned `AppendEventsTransactionRejectedException` with gRPC `CANCELLED` and `ConsistencyConditionException`. Course, student, joint and full histories agree. Losing-student history is empty. `AxonProbeTest.kt:129–166`. |
| 01-02 | The public command exercises three client identities, a zero baseline, an open subscription and the correlated direct query after the write. | Verified | Native worker, command and projection PIDs were 60104, 61139 and 61152. Server registrations and bus identities are distinct and role-specific. Query and subscription both moved from 0 to 1, correlated to the stored event. |
| 01-02 | The guide covers bootstrap, transcript, teardown and clean retry. | Verified | The documented wrapper task launches the disposable fixture. The native tests exercise successful and controlled-failure exits. The failure case proves the unrelated network survives. [Probe guide](../../../probe/README.md) |
| 01-02 | Ordinary build works with Docker unreachable, and secondary classification preserves justified non-passes and rejects core failures. | Verified | Cold and warm commands each ran the smoke test at the refused Docker endpoint. The retained dry-run graph reserves the Docker and image tasks for explicit invocation. The standalone classifier self-test passed on both supported interpreter samples. |
| 01-03 | Node and npm version owners and the lock drive a Gradle `npm ci` build. Paketo receives the staged static HTML and serves the same bytes. | Verified | `.nvmrc` and `probe/web/package.json` select Node `26.13.1` and npm `12.2.3`. Staging allows only `public/index.html`. Both native images returned HTTP 200 with their distinct expected bodies and matching digests. |
| 01-03 | ARM64 packaging has measured evidence and failures of the core tuple remain blocking. | Verified | Retained Pack, lifecycle, OCI and HTTP evidence supports frontend Pass. The evidence checker gates acceptance on the core JUnit and transcript before classifying secondaries. |
| 01-04 | The three language and formatting checks run independently and produce concrete outcomes. | Verified | Jupiter ran the seeded Kotest property for 32 checks, ktfmt produced identical bytes on its second pass, and the TypeID check validated 9 positive and 21 negative fixtures per language plus two cross-language records in each direction. |
| 01-04 | The TypeScript sample uses the declared npm, a dedicated lock and an isolated clean install. | Verified | The root task delegates to the scoped Gradle Node task with `probe/typeid` as its project directory. A checked TypeID lock and producer tool metadata establish the execution, and the runtime graph and static package remain isolated. |
| 01-05 | The final guide reproduces the fresh native proof and the durable report states the exact tuple, image children, commands and limits. | Verified | Retained acceptance command, manifest and report cross-check. The native config digest matches the running container. The separately verified AMD64 config and manifest provide registry metadata. |
| 01-05 | All four secondary outcomes carry evidence and an adoption decision. Mandatory runtime and terms gates are resolved. | Verified | Four Pass dispositions across seven producers. The report assigns subsequent tooling decisions to the receiving phases and scopes them to the observed outputs. |
| 01-05 | The selected stack traces to stable/LTS candidates, entitlement terms, launch behavior and dependency review scope. | Verified | The report pins exact coordinates and reconciles the Guava paths, non-consuming pgJDBC and PostgreSQL scope, and the incomplete private JVM scan. |
| 01-05 | The report assigns first AMD64 runtime to hosted GitHub Actions and states the retirement conditions. | Verified | The hosted handoff requires AMD64, replacement Testcontainers coverage of tagged write, rejection and subscription correlation, a representative Playwright pass and a retained replacement-run link. [Hosted verification and retirement](../../../docs/feasibility/phase-01.md#hosted-amd64-verification-and-retirement) |

### Negative Guarantees

| Plan projection | Resolution | Enforcement and scope |
| --- | --- | --- |
| 01-01 · The public quick start must not depend on vendor registration, a manually obtained license or a Platform token. | Verified for the Phase 01 standalone quick start. | The worker starts with freshly reset home and work directories and an environment limited to Docker reachability and system basics. Both child JVMs receive fresh homes and allowlisted environments, and Spring starts with an explicit blank configuration. The disposable server uses explicit standalone DCB, no supplied bind mounts and mapped loopback ports. Its own log recorded unregistered mode and scheduled shutdown, and the three clients successfully completed the proof. Docker Registry used an anonymous pull. The fixture does not block or monitor vendor egress, and the short run did not exercise renewal or shutdown. The report scopes these observations separately from the evaluation terms. [Image terms](https://hub.docker.com/r/axoniq/axonserver), [Legacy agreement](https://www.axoniq.io/legal/legacy-software-subscription-agreement-terms), [Current terms](https://www.axoniq.io/legal/terms-of-service), [Licensing behavior](https://docs.axoniq.io/axoniq-platform-reference/licensing/), [Rotation and expiry](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/) |
| 01-02 · A fake event store, single-process handler or simulated subscription must not count as the FND-01 proof. | Verified by executable assertions. | The role identity checks require `AxonServerEventStorageEngine` and both distributed buses. The test checks distinct PIDs, names and server-side registrations with command and query handler isolation. It opens the actual query publisher before sending the remote write. The server enforces the stale condition at commit and subsequent engine reads verify the same persisted winner by both tags. A streaming event handler emits the projection's correlated state to the open subscription. The report verifier requires matching native XML and trace records. |

Both plans projected these guarantees with `status: unresolved` and an unspecified verification tier. The executed positive and negative assertions and observed credential-isolated startup resolve the statements at phase scope. The verification requires no override.

### Required Artifacts

The GSD artifact check passed all 27 declared entries, including shared paths declared by multiple plans. Manual verification established substance and the following runtime or documentation uses.

| Plan | Required artifacts | Status | Wiring and substance |
| --- | --- | --- | --- |
| 01-01 | `probe/build.gradle.kts`, `gradle/libs.versions.toml`, `ProbeApplication.kt`, `AxonProbeTest.kt`, `gradle-wrapper.properties` | Verified | The root build includes the opt-in suite, provides the catalog-selected native image and compiles the Spring roles. The Unix and Windows launchers reference the checked wrapper JAR, and the distribution ZIP and JAR match Gradle's published SHA-256 values. The retained Unix wrapper output reports Gradle `9.9.2`. [Gradle release checksums](https://gradle.org/release-checksums/) |
| 01-02 | `.java-version`, `verify_secondary.py`, `ProbeContractsTest.kt`, `ProbeApplication.kt`, `ProbeProjection.kt`, `AxonProbeTest.kt`, `ProbeFixture.kt`, `probe/README.md` | Verified | Gradle reads the JDK feature pin. The acceptance runner invokes the default smoke and integration paths. The fixture starts and connects the roles, then performs scoped cleanup. The guide invokes those tasks and links the record. |
| 01-03 | `probe/web/package.json`, `probe/web/package-lock.json`, `.nvmrc`, `probe/web/build.gradle.kts`, `probe/web/build.mjs` | Verified | The nested build installs from the lock, runs the sample with Gradle-provisioned Node/npm, checks staged output and drives native Pack/HTTP. |
| 01-04 | `KotestInteropTest.kt`, `probe/kdoc/Specimen.kt`, `probe/typeid/vectors.json`, `TypeIdVectors.kt`, `check-vectors.ts`, `probe/build.gradle.kts` | Verified | The named Jupiter suite, formatter scratch copies and reciprocal filtered vector checks each run through dedicated Gradle tasks. |
| 01-05 | `docs/feasibility/phase-01.md`, `probe/README.md`, `probe/verify_evidence.py` | Verified | The guide links the permanent report and exact runner command. The runner verifies report fields against the retained, fingerprinted acceptance run. |

### Key Link Verification

The GSD text matcher found two literal path references. The other 14 links resolve through Gradle task selection, version aliases, shared message contracts, cross-process routing or evidence filenames. Those links were traced in source and checked against the run.

| Plan | From → To | Status | Evidence |
| --- | --- | --- | --- |
| 01-01 | `settings.gradle.kts` → `probe/build.gradle.kts` | Wired | `include(":probe")` resolves the probe build and the conventional root catalog. |
| 01-01 | `AxonProbeTest.kt` → `ProbeApplication.kt` | Wired | The tracer uses the shared command name and type, checks remote registration and asserts handler PID and persisted receipt ID. |
| 01-01 | `probe/build.gradle.kts` → `gradle/libs.versions.toml` | Wired | `libs` provides runtime BOMs and passes the pinned OCI index through `probe.serverImage` to `ProbeFixture`. |
| 01-02 | `AxonProbeTest.kt` → `ProbeApplication.kt` | Wired | `fixture.send` reaches `EnrollmentHandler`; the stale append uses the same real server engine and old marker. |
| 01-02 | `AxonProbeTest.kt` → `ProbeProjection.kt` | Wired | The query gateway and existing subscription reach the only registered `READ_COURSE` handler, and update data carries the original event ID and projection PID. |
| 01-02 | `probe/README.md` → `probe/build.gradle.kts` | Wired | The documented wrapper command selects the named integration JVM suite present in the retained Gradle graph. |
| 01-03 | `probe/build.gradle.kts` → `probe/web/build.gradle.kts` | Wired | `runFrontendTask` invokes the wrapper with `-p probe/web` for the two named frontend tasks. |
| 01-03 | `probe/web/package.json` → `probe/web/build.mjs` | Wired | npm's `build` script executes the producer with the Gradle-provided marker and staging path. |
| 01-03 | `probe/web/build.gradle.kts` → `gradle/libs.versions.toml` | Wired | The nested settings import the root catalog. The packaging task resolves pinned builder, run image and Web Servers inputs. |
| 01-04 | `probe/build.gradle.kts` → `KotestInteropTest.kt` | Wired | The isolated Jupiter suite filters for the named method, verifies exercise count and retains its actual XML. |
| 01-04 | `probe/build.gradle.kts` → `probe/kdoc/Specimen.kt` | Wired | The task formats scratch copies, checks required features and compares actual first and second bytes. |
| 01-04 | `TypeIdVectors.kt` → `check-vectors.ts` | Wired | Gradle forwards Kotlin output to the TypeScript check and consumes its independently written JSON with the same run/exchange IDs, prefix and UUID bytes. |
| 01-04 | `probe/web/build.gradle.kts` → `probe/typeid/package.json` | Wired | The scoped Gradle npm task resolves the TypeID manifest and lock, installs with `ci` and runs the declared `tsc` and Node script under the shared pins. |
| 01-05 | `probe/README.md` → `docs/feasibility/phase-01.md` | Wired | Relative link resolves to the durable report. |
| 01-05 | `probe/verify_evidence.py` → `AxonProbeTest.kt` | Wired | The checker requires the named integration methods and binds their XML, sidecar records and correlated run values. |
| 01-05 | `docs/feasibility/phase-01.md` → `gradle/libs.versions.toml` | Wired | The report links the authoritative catalog and cross-checks its selected coordinates and index with execution evidence. |

### Data-Flow Trace

| Rendered result | Data source and path | Status |
| --- | --- | --- |
| Receipt, per-tag histories and latest query state | Remote command receipt follows `commit()`. The engine reads the real Axon Server event. The projection's streaming handler increments the state from that event and emits through the existing query subscription. Run, course and event identifiers agree in the outputs. | Flowing |
| Static HTTP response | Gradle's npm task stages the marker-specific HTML. Native Paketo packaging reads that stage. The probe requests the running image's loopback endpoint and compares the body byte-for-byte to the stage. | Flowing |
| TypeID exchange and feasibility transcript | Canonical expected vectors drive separate language implementations. Each exchange is independently produced and validated by the other implementation. The acceptance checker binds real producer output, inputs and published fields by digest. | Flowing |

## Behavioral Spot-Checks and Probe Execution

| Command or retained producer | Result | Status |
| --- | --- | --- |
| `python3 probe/verify_evidence.py --evidence probe/build/reports/feasibility --report docs/feasibility/phase-01.md` | Independently ran. Exit 0, `Acceptance evidence verified for acceptance-nvahwpkb`. | Pass |
| `python3 probe/verify_secondary.py self-test` and `/usr/bin/python3 probe/verify_secondary.py self-test` | Independently ran on Python 3.12.1 and 3.9.6. Both returned exit 0 and `Secondary verifier self-test passed`. | Pass |
| `sh -n gradlew` and `python3 probe/verify_evidence.py --help` | Independently ran. Valid Unix launcher syntax and option descriptions. The Windows launcher was inspected statically. | Pass |
| Retained `./gradlew --console=plain :probe:integrationTest --rerun-tasks` | Three JUnit cases passed. The forced failure and success path both closed the subscription, exited owned child JVMs and removed the owned container. The separate Docker network survived the forced failure. | Pass |
| Retained ordinary cold and warm wrapper builds and both dry runs | The Docker endpoint returned `ECONNREFUSED`. Both ordinary builds passed the named contract smoke case. The opt-in graph contains the integration and native image tasks. | Pass |
| Retained secondary stages | `frontend-fixture`, `frontend-assets`, `frontend-image`, `kotest`, `kdoc`, `typeid-jvm` and `typeid-exchange` each recorded exit 0 and a validated output. The Node stages recorded Node `v26.13.1` and npm `12.2.3`, and the image stage recorded Pack `0.40.11+git-523c9ce.build-7117`. | Pass |

The native producer and secondary executions are from the retained post-review acceptance run. This verification reran the report checker and Python self-tests without restarting Docker workloads.

### Test Quality Audit

| Test evidence | Active | Skipped | Assertion strength | Verdict |
| --- | --- | --- | --- | --- |
| `AxonProbeTest.kt` | 3 | 0 | Observes real registrations, a committed payload, typed server rejection, exact event IDs, live state and scoped cleanup | Behavioral coverage for FND-01 |
| `ProbeContractsTest.kt` | 1 per build | 0 | Compares round-tripped contract values and case-sensitive tag keys | Value coverage |
| `KotestInteropTest.kt` and TypeID cases | Named Jupiter property and both TypeID implementations executed | 0 in required selected cases | Seeded property workload, external canonical vectors, opposite-language prefix and byte decoding and rejection checks | Value and interoperability coverage |

The native cases use Axon Server outcomes and independent event reads as their oracle. TypeID canonical expectations come from the referenced upstream vector revision. The evidence snapshots record observed output after assertions complete. No disabled or circular test was used as proof of FND-01.

## Requirements and Review Coverage

| Requirement | Source | Status | Evidence |
| --- | --- | --- | --- |
| FND-01 | Roadmap and Plans 01-01 through 01-05 | Satisfied | The native proof exercises the exact Axon APIs, Boot wiring, overlapping tagged append and remote routing. The report records applicable terms, artifacts, bootstrap and both image children. This is the only requirement mapped to Phase 01. |

### Decision Coverage

The GSD decision coverage check found evidence for all 13 trackable decisions. The record covers the hosted AMD64 and retirement conditions for D-05 and D-06. Phase 07 owns the hosted workflow.

### Review, Security and Anti-Patterns

- The [code review](01-REVIEW.md) scoped the review to the phase-range file union and documented its resolver fallback. The [disposition](01-REVIEW-DISPOSITION.md) closes CR-01 and WR-01 through WR-03 in `0f3101a`. Source and independent self-tests confirm concrete failure signatures and environmental classification, Java timestamp parsing on Python 3.9, and staged-hash validation. The acceptance records confirm executable-backed Node/npm/Pack provenance.
- The [security register](01-SECURITY.md) covers ten planned threats for the local fixture, with zero open High or Critical findings in that scope. The executable controls include local-only exposed ports, sanitized role startup, immutable native image selection, correlated evidence and narrowly scoped teardown. No blocking stub, disabled FND-01 case or unresolved debt marker was found in the phase implementation.
- Runtime and test Guava graphs select `33.8.0-android`, and the isolated formatter selects `33.8.0-jre`. The [feasibility record](../../../docs/feasibility/phase-01.md#dependency-and-image-review) records the earlier High advisory and the affected graph comparisons. The isolated TypeID sample's single underlying Moderate advisory has a dated review through 2026-12-02. The private JVM scan is explicitly incomplete. The recorded verification scope covers the examined public graphs and local fixture.

## Deferred Work and Verification Limits

| Item | Receiving work | Current evidence |
| --- | --- | --- |
| Hosted AMD64 runtime and delivery scans | Phase 07 hosted delivery | Both runnable OCI children have verified metadata. The ARM64 child ran on Linux/ARM64 and its running config matched the checked digest. The first AMD64 execution is assigned to the hosted runner. |
| Account-based Platform connection | Phase 07 optional Platform path | The local quick start is credential-free. The account flow, vendor-offline runtime and extended entitlement behavior are outside this measurement. |
| Probe retirement | After hosted AMD64 and replacement application checks | The durable evidence record requires equivalent Testcontainers behavior, a passing Playwright workflow and a link to the replacement run. |

## Human Verification

N/A for Phase 01. The maintainer CLI path and runtime transitions were exercised in the recorded native run, and the verifier checked the reproducer, retained artifacts and referenced publisher terms. No required acceptance gap remains.

_Verifier: gsd-verifier_
