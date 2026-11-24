# Axon Server DCB feasibility probe

Run the probe from the repository root on a native ARM64 host with Eclipse Temurin 25 and a Linux ARM64 Docker daemon. Start Docker before running the integration suite. The suite was exercised on macOS ARM64 with Colima and Docker 29.5.2. The local daemon was reachable through the standard Unix socket.

```sh
./gradlew --console=plain :probe:integrationTest --rerun-tasks
```

The fixture pulls the pinned ARM64 child of the Axon Server OCI index and gives every scenario a fresh container with `AXONIQ_AXONSERVER_STANDALONE_DCB=true`. Docker maps the management and gRPC ports to random loopback ports. Every role points `axon.axonserver.servers` at the mapped gRPC endpoint and explicitly selects `axon.axonserver.context=default`. The driver runs in the test worker. Spring Boot starts separate command and projection JVMs with isolated homes, distinct client IDs and the same message contracts.

The observed run started without vendor registration, a license file or a Platform token. Axoniq documents a 12-hour server shutdown without a license or Platform connection. The permanent [Phase 01 feasibility report](../docs/feasibility/phase-01.md) records the exact versions, image children, publisher terms and runtime limitations. [Axoniq rotation and expiry](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/)

## Read the results

- `PROBE_TRACER` shows one remote command and its event under both tag criteria.
- `PROBE_CORE` shows the run ID, three role identities, the initial zero direct query and subscription result, and the terminal marker from empty history. The trace then records the remote commit, the stale append refusal (`CANCELLED`, `ConsistencyConditionException`), the same winner ID through both tags and an empty losing-student read. The original subscription and a fresh remote query both report one enrollment and the winning event ID.
- `PROBE_CLEANUP` shows the controlled exception after the subscription opened and confirms cancellation, child JVM exit and container removal. The successful core trace contains the same cleanup measurements.

The suite prints each trace through Gradle. Ignored JSON and per-run diagnostics are under `probe/build/reports/feasibility/`, with JUnit XML under `probe/build/test-results/integrationTest/`. Match the run ID and event ID across the output and XML before using the evidence.

## Repeat a run

Use the same wrapper command to get distinct run IDs and empty starting histories. The two warm runs on the observed host took 87–90 seconds for all three tests. Server readiness took about 20 seconds per scenario, each child role took about 2 seconds to register, and cleanup took 3–4 seconds. The fixture allows 90 seconds for the HTTP endpoint and DCB leader, 45 seconds per child role and 20 seconds for scenario messages, with a five-minute budget for the full Gradle integration task. A first run also resolves the wrapper, Gradle dependencies, registry metadata and image layers. Its duration depends on the network and image cache.

If a run fails, start with the first failing JUnit assertion or named readiness stage. The scenario directory contains the matching `server.log`, `command.log` and `projection.log` once those components start. Keep raw logs local. Verify Docker is running and the selected architecture matches before repeating the command.
