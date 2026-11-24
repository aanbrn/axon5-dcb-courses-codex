# Walking Skeleton — Axon 5 DCB Courses

**Phase 1 · Axon Server and Toolchain Feasibility**

The maintainer runs `./gradlew --console=plain :probe:integrationTest --rerun-tasks` and reads a transcript showing which JVM handled the command, which tagged event survived and which update reached the waiting subscriber. This is the planned contract. A successful native run and the corresponding report supply the evidence.

## Execution path

1. The Gradle integration test starts an isolated Axon Server with a fresh DCB context, a Spring Boot command JVM and a Spring Boot query/projection JVM. The test driver is a third JVM with distributed command and query gateways.
2. The driver reads the empty course projection and waits for the initial result of a remote subscription. It sources the stale writer’s history from the server and retains the returned consistency marker.
3. A remote winning command commits an event tagged with `courseId=C` and `studentId=A`. The losing append uses the earlier marker and criteria matching course C or student B. Its awaited transaction rejects the partial overlap.
4. Two independent tag reads identify the same durable winning event. The losing student's history is empty. The projection JVM consumes the committed event and emits its correlated update to the original subscription. A fresh direct query agrees.
5. The reader can match the run, event and process identities in the transcript. The fixture closes the stream, processes and container, including on a forced failure.

## Architectural decisions

| Decision | Choice and reason |
| --- | --- |
| Entry point | A temporary shared Gradle `:probe` module exposes an explicit Docker-backed integration task. Ordinary `build` runs a serialization smoke test without Docker. |
| Framework and transport | Kotlin and Spring Boot on Temurin, using the actual Axon 5/Axoniq starter, connector and distributed buses. Separate JVM registrations make local dispatch distinguishable from remote delivery. |
| Durable state | A single fresh DCB-enabled Axon Server stores tagged events and arbitrates the conditional append. Its persisted history is the evidence for the winning write. A process-local query projection supports the isolated subscription scenario. |
| Local access | A qualified unregistered evaluation starts on ARM64, with clean homes, disposable storage, local endpoints and no supplied vendor credentials. Document the exact server and application terms separately, including anonymous permission/egress if observed. |
| Version ownership | Gradle Wrapper owns Gradle. The catalog owns Gradle plugin/library and image inputs. `.java-version` owns the Temurin feature. `mise.toml` owns independent CLIs, `.nvmrc` owns Node and the web manifest’s `packageManager` owns npm. Each npm project has a lockfile. Test actual versions before adoption. |
| Frontend fixture | Gradle builds one static marker document with npm. Pack receives the staged output and Paketo Web Servers serves it locally. This independent check supplies the first evidence for application packaging in Phase 5. |
| Evidence lifetime | `probe/README.md` explains how to run the module. `docs/feasibility/phase-01.md` permanently records the tested revision, commands, selected inputs, terms, results, limitations and later replacement criteria. |

## Acceptance and handoff

| Observable result | Owning plan |
| --- | --- |
| One clean command and durable two-tag read on native ARM64, checksummed wrapper and observed host Temurin candidate | 01-01 |
| Explicit rejected overlapping commit, absent loser, distinct remote command/query roles, initial/live subscription, bounded cleanup, persistent Temurin feature owner, Docker-free build and secondary outcome checks with renewable native core evidence | 01-02 |
| Gradle-driven npm build, prebuilt-only Pack input and two distinct native byte-for-byte HTTP responses | 01-03 |
| Jupiter/Kotest execution, ktfmt KDoc behavior and actual bidirectional Kotlin/TypeScript TypeID exchange | 01-04 |
| Repeated full proof, exact selected tuple, image index and both runnable children, terms and dependency decisions | 01-05 |

Plans 01–05 execute in five serial waves in the same checkout. This keeps the core probe on a stable Gradle graph while it runs and gives each secondary stage the outcome checker from Plan 02.

Phase 2 owns shared build conventions, quality tooling and the browser shell. Phase 3 introduces the first application command, database projection, REST BFF and browser workflow. Phase 5 builds the application-role images. Phase 7 owns the full Compose quick start, hosted CI and optional Platform connection. AMD64 registry metadata remains the available Phase 1 evidence until an actual hosted run.

For the first GitHub Actions AMD64 run, use the replacement integration/E2E suites if they already provide the required observations, otherwise use `:probe`. Retire the module after a successful hosted AMD64 run demonstrates the Testcontainers multi-tag write, conflict and cross-process subscription and Playwright proves the representative browser workflow. Preserve the report with a link to the replacement evidence.
