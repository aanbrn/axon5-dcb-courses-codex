# Phase 1: Axon Server and Toolchain Feasibility - Context

**Gathered:** 2026-11-24

**Status:** Ready for planning

<domain>

## Phase Boundary

Reproduce a minimal Kotlin and Spring Boot DCB scenario against a clean Axon Server context. Verify a committed multi-tag write, rejection of an overlapping append, remote command and query routing, and a subscription query update across processes. Record the exact tuple, image metadata, terms, and results before selecting version pins. Run narrow TypeID, Kotlin 2.4 and JUnit 6 with Kotest, ktfmt and KDoc, and frontend packaging samples.

The shared build and UI foundation, application domain workflows, deliverable images, and hosted CI are scheduled in later phases.

</domain>

<decisions>

## Implementation Decisions

### Probe lifecycle and evidence

- **D-01:** Use a temporary `:probe` module in the shared Gradle build. Use the project’s authoritative version declarations and expose a separate Gradle entry point for the Docker-backed check. Keep the Docker probe outside the ordinary `./gradlew build` task graph.
- **D-02:** Use course and student terminology with `courseId` and `studentId` tags. Keep the scenario small enough to isolate the DCB and transport behavior.
- **D-03:** Keep a short run guide with `:probe`. Record reproducible commands, exact tested versions, image index and child digests, applicable terms, results, and limitations in a Phase 1 report. Preserve the report after retiring the module.

### Architecture verification and retirement

- **D-04:** Run the full Phase 1 probe on ARM64 and verify the selected image child digests for both ARM64 and AMD64. Report Phase 1 AMD64 evidence as image metadata until a runtime check passes.
- **D-05:** Perform the first AMD64 runtime verification on a GitHub Actions AMD64 runner when hosted CI is enabled. Use the integration and E2E suites if they already provide the required evidence. Otherwise use `:probe` for the first AMD64 run.
- **D-06:** Retire `:probe` once Testcontainers tests in GitHub Actions reproduce the multi-tag write, append conflict, and cross-process subscription behavior, and Playwright verifies the representative browser workflow. Require a successful run on AMD64 with that replacement coverage.

### Secondary probe outcomes and frontend packaging

- **D-07:** If a secondary probe fails reproducibly while the main DCB proof passes, record the blocker and its reproducer. Leave the affected choice open for the phase that uses that tool. A failure that invalidates the selected Axon runtime tuple blocks Phase 1.
- **D-08:** Mark a secondary probe `Unverified` when an environmental condition prevents a result. Record the cause and retry trigger. Phase 1 may finish with this status if the core DCB proof succeeds.
- **D-09:** Use npm and `package-lock.json` for frontend and documentation-site builds. Consider pnpm for a specific tooling need if one arises.
- **D-10:** For the frontend probe, Gradle runs `npm ci` and builds static assets. Paketo Web Servers packages those assets and the probe verifies that the image serves them. Apply the same ownership of the build and packaging steps in the application.

### Public quick start and version selection

- **D-11:** A reader can run the default local quick start and Phase 1 DCB probe without registering with the vendor, obtaining a license manually, or configuring a Platform token. Verify a clean launch for the exact server image and connector combination and record its applicable terms.
- **D-12:** Document the unlicensed runtime limit where applicable. Axoniq documents a 12-hour shutdown for Axon Server 2026.0 and later when the server is disconnected from Platform and has no license file. Keep the Individual Development plan and Platform connection optional. Handle credentials outside Git and planning files.
- **D-13:** Apply the project’s version policy to the actual tested artifacts. Start from current stable releases and applicable current LTS lines. Choose an older release only for a documented blocker with supporting evidence. Reconcile earlier dependency and image notes against recovered or reproduced evidence in this checkout.

### Planner Discretion

- Select exact artifact candidates after checking current official documentation and apply D-13 when choosing the matrix. Choose the minimal processes, bootstrap mechanism, and tests that prove the required DCB behaviors and can be rerun from a clean checkout.

</decisions>

<canonical_refs>

## Canonical References

**Read these before planning or implementing the phase.**

### Project and verification scope

- `.planning/PROJECT.md` — constraints, version ownership, dependency maintenance, and prior review records.
- `.planning/REQUIREMENTS.md` — FND-01 and related frontend packaging, testing, and optional Platform requirements.
- `.planning/ROADMAP.md` — Phase 1 boundary and follow-on packaging and CI milestones.
- `.planning/research/STACK.md` — candidate verification areas and official tooling sources.
- `.planning/research/ARCHITECTURE.md` — cross-process command, query, and event flow.
- `.planning/research/PITFALLS.md` — context, routing, and evidence pitfalls.

### Upstream references

- [Axoniq Platform licensing and expiry](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/) — standalone runtime limit and license behavior.
- [Axoniq Individual plan](https://docs.axoniq.io/axoniq-platform-reference/billing/) — Development access.
- [Axon Server DCB contexts](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/administration/multi-context/) — versioned context behavior. Recheck the reference for the selected image.
- [Paketo Web Servers](https://paketo.io/docs/howto/web-servers/) — packaging and serving frontend assets.

</canonical_refs>

<code_context>

## Existing Code Insights

- The checkout contains project planning files, the local GSD installation, and `.gitignore`. The Gradle wrapper, Kotlin services, frontend, and Compose setup will be established by later planning and execution.
- The project already assigns version ownership by ecosystem. Use the Gradle catalog for applicable Gradle inputs, `.java-version` for the Temurin feature version, `.nvmrc` for Node.js, and `packageManager` plus the lockfile for npm. Record the observed JDK patch and build as evidence.
- Historical Phase 1 plan paths cited in `.planning/PROJECT.md` are references from the original brief. This checkout has no corresponding plans or runtime evidence from those paths.

</code_context>

<specifics>

## Specific Ideas

- The reader-facing example uses `courseId` and `studentId` to connect the feasibility probe to the later enrollment scenario.
- Retain the Phase 1 report as a dated record of the selected stack and any unverified check. Link later AMD64 evidence to the report.

</specifics>

<deferred>

## Deferred Ideas

- First actual AMD64 run and subsequent `:probe` retirement are deferred to GitHub Actions and equivalent proven coverage.
- A concrete pnpm tooling use can be evaluated when that tooling is selected.
- Verify the optional Platform connection when the author supplies credentials securely, as scheduled in Phase 7.

</deferred>
