# Axon Server DCB feasibility probe

Run the probe from the repository root on a native ARM64 host with Eclipse Temurin 25 and a Linux/ARM64 Docker daemon. Start Docker before running the integration suite. The acceptance run used macOS ARM64 and Docker 29.10.0.

```sh
./gradlew --console=plain :probe:integrationTest --rerun-tasks
```

The fixture pulls the pinned ARM64 child of the Axon Server OCI index and gives every scenario a fresh container with `AXONIQ_AXONSERVER_STANDALONE_DCB=true`. Docker maps the management and gRPC ports to random loopback ports. Every role points `axon.axonserver.servers` at the mapped gRPC endpoint and explicitly selects `axon.axonserver.context=default`. The driver runs in the test worker. Spring Boot starts separate command and projection JVMs with isolated homes, distinct client IDs and the same message contracts.

The observed run started without vendor registration, a license file or a Platform token. Axoniq documents a 12-hour server shutdown without a license or Platform connection. The permanent [Phase 01 feasibility report](../docs/feasibility/phase-01.md) records the tested revision, image digests, publisher terms and runtime limitations. [Axoniq rotation and expiry](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/)

## Read the results

- `PROBE_TRACER` shows one remote command and its event under both tag criteria.
- `PROBE_CORE` shows the run ID, three role identities, the initial zero direct query and subscription result, and the terminal marker from empty history. The trace then records the remote commit, the stale append refusal (`CANCELLED`, `ConsistencyConditionException`), the same winner ID through both tags and an empty losing-student read. The original subscription and a fresh remote query both report one enrollment and the winning event ID.
- `PROBE_CLEANUP` shows the controlled exception after the subscription opened and confirms cancellation, child JVM exit and container removal. The successful core trace contains the same cleanup measurements.

The suite prints each trace through Gradle. Ignored JSON and per-run diagnostics are under `probe/build/reports/feasibility/`, with JUnit XML under `probe/build/test-results/integrationTest/`. Match the run ID and event ID across the output and XML before using the evidence.

## Repeat a run

Use the same wrapper command to get distinct run IDs and empty starting histories. The fixture allows 90 seconds for the HTTP endpoint and DCB leader, 45 seconds per child role and 20 seconds for scenario messages, with a five-minute budget for the full Gradle integration task. A first run also resolves the wrapper, Gradle dependencies, registry metadata and image layers. Its duration depends on the network and image cache.

If a run fails, start with the first failing JUnit assertion or named readiness stage. The scenario directory contains the matching `server.log`, `command.log` and `projection.log` once those components start. Keep raw logs local. Verify Docker is running and the selected architecture matches before repeating the command.

## Run the optional checks

Run each sample independently from the repository root. The image sample uses the Pack version declared in `mise.toml` and a reachable native Docker daemon. Gradle reads Node and npm from their version owners.

```sh
./gradlew --console=plain :probe:kotestProbe --rerun-tasks
./gradlew --console=plain :probe:kdocProbe --rerun-tasks
./gradlew --console=plain :probe:typeIdProbe --rerun-tasks
./gradlew --console=plain :probe:frontendAssets --rerun-tasks
./gradlew --console=plain :probe:frontendImageProbe --rerun-tasks
```

The full acceptance command runs the ordinary build with Docker unreachable, then the native suite and all secondary stages. Those stages include the direct npm fixture and the JVM-only TypeID vectors. It requires Python 3.9 or newer, retains a fresh fingerprinted manifest under the ignored `probe/build/reports/feasibility/runs/` directory and updates the current acceptance pointer after verification.

```sh
python3 probe/verify_evidence.py --capture --evidence probe/build/reports/feasibility
```

Verify the published report using the original retained acceptance directory. The report identifies that run even if the pointer advances.

```sh
python3 probe/verify_evidence.py --evidence probe/build/reports/feasibility --report docs/feasibility/phase-01.md
```
