# Phase 2: Build and UI Foundations - Context

**Gathered:** 2026-11-25
**Status:** Ready for UI design and planning

<domain>

## Phase Boundary

Turn the verified toolchain into shared Gradle build and test conventions. Deliver a runnable React shell, a BFF operation for demo roles, an explicit OpenAPI-to-TypeScript build path, Storybook, and an initial documentation site. Verify the clean Docker-free build, shared repository checks, and maintainer tooling.

Phase 3 adds enrollment, domain projections, and live browser views. Phase 7 verifies the complete Compose quick start and hosted delivery controls.

</domain>

<decisions>

## Implementation Decisions

### First BFF scenario

- **D-01:** Load the administrator and two named demo students from the BFF through the generated TypeScript client. Use the response to populate the role switcher.
- **D-02:** Keep the shell and documentation links usable while the role directory is unavailable. Display an inline error and a retry action next to the switcher.
- **D-03:** Keep a contract-first OpenAPI specification in the BFF module. Make the specification an explicit input for Gradle client generation and make the generated client an input for the frontend build. Generate it without launching the BFF. Verify the BFF HTTP implementation against the specification.
- **D-04:** Publish the implemented demo-role directory operation in the first contract. Document how feature slices extend the contract and add browser commands, reads, and subscription operations as the corresponding behavior ships.

### Demo role switcher

- **D-05:** Open a fresh demo tab in administrator mode. Use two named demo students and keep the names consistent across the app, quick start, and examples.
- **D-06:** Scope the selected role to the tab and preserve it on reload. Separate tabs can show different roles.
- **D-07:** If a successfully loaded directory omits the saved student, fall back to the administrator and tell the reader the previous student is unavailable.
- **D-08:** Use the existing v1 demo-role model. If a later version adds login, use a signed cookie for the login session.

### Documentation entry point

- **D-09:** Lead the documentation home page with the demo launch path. Show an `Open demo` action when the app URL is configured and route readers to local launch instructions otherwise.
- **D-10:** Render the Phase 1 feasibility report in the docs site from `docs/feasibility/phase-01.md` as its single source.
- **D-11:** Publish a Maintainer Guide with the tool inventory, `doctor`, and dependency maintenance and advisory procedures. Reconcile the Phase 1 records against the evidence in this checkout. Keep advisory inventories, feeds, and results outside the repository and the generated site.

### Local checks and CI

- **D-12:** Apply the shared repository formatting and style rules to staged content in the pre-commit hook and to the whole repository in CI. Include staged formatting fixes in the current commit and preserve unstaged edits, including in partially staged files.
- **D-13:** Give `doctor` one report with required and additional checks. Distinguish prerequisites for a regular build from prerequisites for Docker-backed checks and image packaging.
- **D-14:** Run style checks and a clean `./gradlew build` in Phase 2 GitHub Actions on PRs without Docker.
- **D-15:** Schedule the first hosted AMD64 DCB runtime check for Phase 7. Use application suites if they reproduce the Phase 1 DCB evidence and fall back to `:probe` otherwise. This decision updates the timing in Phase 1 D-05. Reconcile the handoff wording in the feasibility report when integrating it into the docs site. Retain the Phase 1 D-06 retirement criteria.

### Research and design discretion

- Choose the client generator, static docs engine, and compatible Gradle integration during phase research. Apply the current stable and LTS policy and document any reproducible blocker that requires an older choice.
- Define the screen layout, theme, navigation, and interaction details in the Phase 2 UI-SPEC. Cover loading, empty, and error states in Storybook and carry the accessibility target into the foundation.

</decisions>

<canonical_refs>

## Canonical References

Read these before planning or implementing the phase.

### Scope and conventions

- `.planning/ROADMAP.md` — Phase 2 acceptance and the Phase 3, 7, and 8 handoffs.
- `.planning/REQUIREMENTS.md` — FND-02, FND-05, FND-06, CQRS-04, UI-01, UI-03, QA-07, QA-08, and DOC-06.
- `.planning/PROJECT.md` — version ownership, dependency review procedure, architecture constraints, and UI decisions.
- `AGENTS.md` — repository conventions and quality checks.
- `.planning/research/STACK.md` — framework and tooling direction.
- `.planning/research/ARCHITECTURE.md` — BFF boundary and the later CQRS flow.

### Phase 1 evidence and build examples

- `.planning/phases/01-axon-server-and-toolchain-feasibility/01-CONTEXT.md` — D-05, D-06, and the verified toolchain direction.
- `.planning/phases/01-axon-server-and-toolchain-feasibility/01-VERIFICATION.md` — verified behavior and open verification boundaries.
- `docs/feasibility/phase-01.md` — report content, dependency evidence, and AMD64 and probe retirement notes.
- `gradle/libs.versions.toml` — catalog and scoped constraints.
- `probe/build.gradle.kts` — JVM suites and Kotlin and KDoc checks exercised in Phase 1.
- `probe/web/build.gradle.kts` — Node and npm ownership and the verified Gradle asset build pattern.

### API contract discussion

- [Springdoc Gradle plugin](https://springdoc.org/plugins.html#gradle-plugin) — startup behavior considered when choosing contract-first.
- [OpenAPI Generator build plugins](https://openapi-generator.tech/docs/plugins/) — example of generation from a file input. Evaluate generator candidates in phase research.

</canonical_refs>

<code_context>

## Existing Code Insights

- The root Gradle build currently includes `:probe`. Its Docker-backed check runs separately from the ordinary build.
- Reuse the Gradle catalog, wrapper, `.java-version`, `.nvmrc`, and `mise.toml` as version owners. Retain the checked-in npm metadata and lockfile pattern from the Phase 1 probe.
- The probe proves Gradle-driven `npm ci`, Kotlin with JUnit and Kotest, and ktfmt behavior on representative KDoc. These results inform the reusable build conventions.
- The BFF, React app, shared UI primitives, and docs site each need their initial project structure. Connect them through Gradle task inputs and outputs and the OpenAPI artifact.
- The Phase 1 report is the existing narrative entry point for the technical proof.

</code_context>

<specifics>

## Specific Ideas

- The quick start should show how to open the Phase 2 shell and switch between the same three roles readers see in the app.
- The role switcher retry is independent of documentation navigation.
- Keep the style check rules shared even where the hook and CI select different file sets.

</specifics>

<deferred>

## Later Phases

- Phase 3 delivers the first application commands, reads, subscription streams, and Playwright enrollment workflow.
- Phase 5 packages the runnable application roles and frontend using Paketo.
- Phase 7 provides full Compose and hosted delivery validation, including the first AMD64 DCB runtime evidence and the optional AxonIQ Platform path.
- Phase 8 publishes the full documentation and showcase review, including the Axon 4 comparison and AI-assisted development record.

</deferred>
