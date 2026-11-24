# Axon 5 DCB Courses

## What This Is

A reference implementation of students subscribing to courses, built on Axon Framework 5 using Dynamic Consistency Boundaries (DCB) instead of aggregates and inspired by “Killing the Aggregate.” It is a learning example held to production-grade standards in architecture, code, tests, documentation, CI/CD, and observability. It serves developers moving from Axon 4, the author’s own deep learning, and a public portfolio or article.

## Core Value

Show, with working code, tests, and documentation, how DCB enforces cross-entity business invariants without aggregates and what trade-offs it offers versus an aggregate-based approach.

## Requirements

### Validated

None yet. Validate through shipped and verified work.

### Active

#### Domain and write-side decisions

- [ ] Create a course, rename it, and change its capacity.
- [ ] Register a student.
- [ ] Subscribe a student to a course and unsubscribe them.
- [ ] Never exceed course capacity, including under concurrent subscriptions.
- [ ] Respect the maximum number of subscriptions per student.
- [ ] Enforce unique course names and release the old name after a successful rename.
- [ ] Transfer a student atomically in one decision spanning the student and both courses.
- [ ] Enqueue a student who requests a full course and automatically subscribe the next student when a seat opens.
- [ ] Define course schedule slots and prevent a student from subscribing to overlapping courses.

#### CQRS and services

- [ ] Separate command decisions over event history from query projections into dedicated read models.
- [ ] Serve reads via QueryBus and live updates via subscription queries.
- [ ] Run a command service, query/projection service, event-driven automation service, and REST BFF with an OpenAPI contract.
- [ ] Use Axon Server as the DCB-capable event store and interservice message router.

#### UI

- [ ] Provide a polished React and TypeScript UI for all business operations, with live views backed by subscription queries.
- [ ] Let readers browse tagged events and inspect which events formed the consistency boundary of a given command.
- [ ] Demonstrate many concurrent attempts for the last seat and make the preserved invariant visible.
- [ ] Provide a demo role switcher for admin and individual students.

#### Quality and testing

- [ ] Use given–when–then unit tests for DCB decisions and component tests per service.
- [ ] Run integration tests against Axon Server and databases via Testcontainers.
- [ ] Exercise browser workflows with Playwright and enforce module or slice boundaries with architecture tests.
- [ ] Load-test concurrent subscriptions with Gatling or k6 and measure and report code coverage.
- [ ] Write idiomatic, documented Kotlin.

#### CI/CD and supply chain

- [ ] Run builds, all test levels, coverage, static analysis, and container image builds in GitHub Actions.
- [ ] Track dependency and tool updates automatically with Renovate or Dependabot.
- [ ] Scan dependencies and built images for vulnerabilities, and scan the repository for leaked secrets.

#### Observability

- [ ] Provide metrics, tracing, and logs via OpenTelemetry and a Grafana stack under Docker Compose.
- [ ] Support an optional AxonIQ Platform connection and verify it with the author’s account when credentials are provided securely.

#### Documentation

- [ ] Publish a presentable README with an overview, quick start, and screenshots or diagrams.
- [ ] Provide ADRs, C4 diagrams, Event Modeling or Event Storming artifacts, and a documentation site.
- [ ] Explain project-specific DCB choices and compare the scenarios to Axon 4 aggregates using diagrams and snippets, including trade-offs.
- [ ] Document how the project was built with AI, retain `.planning/` history, and record lessons learned.

#### Runtime

- [ ] Run the entire system locally with Docker Compose.

### Out of Scope

- Real authentication and authorization with OAuth2/OIDC or Keycloak is deferred to v2. The demo role switcher keeps v1 focused on DCB.
- The aggregate-based implementation appears in documentation only, which preserves the teaching value without maintaining a second application.
- One command service owns both course and student decisions because the write-side boundaries span those entities.
- Docker Compose is the runtime target for v1. Kubernetes and cloud deployment are outside this scope.

## Context

- The author has hands-on experience with Axon 4 aggregates and recognized the problems described in “Killing the Aggregate.”
- The audience is the public GitHub community, the author as a learner, and readers of future portfolio or article material. The before/after story matters.
- The GSD planning history, decisions, and lessons are part of the AI-assisted development deliverable.
- Before committing to a version matrix, verify Axon 5 APIs, Spring Boot integration, and Axon Server DCB configuration against current official documentation and a reproducible compatibility check.
- The author has an AxonIQ Platform account. Keep the local demo independent of the connection and handle credentials through a secure channel outside Git and planning artifacts.
- This is a fresh checkout. The Phase 1 references and dependency review records below come from the project brief. Reconcile them with recovered or reproduced evidence before treating their settings, selected versions, or results as current here.

## Constraints

- Use Kotlin, Spring Boot, and Axon Framework 5 on the backend. Prefer idiomatic Kotlin to Java-style translations.
- Run Axon Server with DCB support in Docker.
- Separate command, query/projection, automation, and REST BFF services by responsibility.
- Use React and TypeScript with Feature-Sliced Design (FSD), checked by Steiger.
- Use Gradle JVM Test Suites and Java Test Fixtures to organize test levels and reuse test helpers.
- Auto-format and style-check all repository artifacts through a local pre-commit hook and in CI.
- Use one Docker Compose setup for the full local system.
- Hold code, tests, documentation, CI, and observability to reference-quality standards.
- Write code, docs, and repository artifacts in English.

## Key Decisions

| Decision | Rationale | Outcome |
| --- | --- | --- |
| Use DCB instead of aggregates | The core invariants span courses and students | Pending implementation |
| Use Kotlin and Spring Boot | Author preference and idiomatic, concise backend code | Pending implementation |
| Use Axon Server | Native DCB persistence and Axon message routing | Pending compatibility proof |
| Split services by CQRS role | Preserve cross-entity decisions while making location transparency visible | Pending implementation |
| Compare Axon 4 aggregates in documentation only | Preserve the before/after explanation without maintaining a second application | Pending implementation |
| Use a demo role switcher in v1 | Keep the example focused on DCB | Pending implementation |
| Retain AI-assisted planning and lessons in the repository | The development process is a second learning goal | Pending implementation |
| Keep one authoritative version owner per ecosystem | Avoid drift and preserve automated updates | Pending implementation |
| Use TypeID (type prefix, UUIDv7, base32) for entity IDs and native `uuid` in storage | Client-generatable, time-ordered, readable typed IDs, with a high cost for changing event identifiers later | Verify Kotlin and TypeScript libraries in Phase 1 |
| Establish a dedicated UI foundation, carry a UI-SPEC and a UI slice for each feature, build a dedicated DCB teaching UI, and run a final UI review | Keep features demonstrable end to end and give the showcase a design contract | Pending implementation |
| Use Storybook and target WCAG 2.2 AA with axe in component and E2E suites | Make the design system inspectable and accessibility testable | Pending implementation |
| Use branches per phase and `$gsd-ship` PRs with squash merge only. Protect `main` with required PRs, required checks, linear history, and zero required approvals | Preserve a review point and clean history for a solo author | Pending remote configuration |
| Let release-please own version tags and releases. Disable GSD tag creation | Prevent tag ownership conflicts | Pending local configuration and release automation in this checkout |
| Report defects and gaps upstream first, maintain one `docs/upstream/` record per case, and enforce links on marked workarounds in CI | Make local workarounds visible and removable | Pending implementation |
| Pin CLI tools with mise and maintain a tooling inventory and `doctor` check | Reproduce the environment beyond Gradle | Pending implementation |
| Use vetted third-party and project-owned skills locally in OpenCode | Treat skills as reviewed code and verify OpenCode compatibility before adoption | Pending selection and implementation |
| Use the Gradle Node plugin for frontend and docs-site subprojects | Make the BFF OpenAPI contract, generated client, and frontend an explicit build graph under `./gradlew build` | Pending implementation |
| Build all images with Cloud Native Buildpacks (Paketo), using `bootBuildImage` for JVM apps and the Web Servers buildpack for the frontend, with no Dockerfiles | Share a build approach, SBOM support, base rebase, and JVM memory tuning | Verify the pnpm path in Phase 1 |
| Use JUnit 6 as the runner with Kotest assertions and property testing | Align with Spring Boot 4, Testcontainers, Gradle Test Suites, and idiomatic Kotlin tests | Verify Kotlin 2.4 and Kotest compatibility in Phase 1 |
| Use Gradle JVM Test Suites and Java Test Fixtures | Separate test levels without duplicating shared helpers | Pending implementation |
| Enforce frontend FSD with Steiger | Make frontend boundaries as explicit as backend ones | Pending implementation |
| Auto-format and style-check produced artifacts | Apply the same standard regardless of author | Pending implementation |
| Use ktfmt for Kotlin/KDoc formatting, detekt `comments` rules, and Dokka `failOnWarning` | Treat documentation quality as part of Kotlin code quality | Verify ktfmt behavior on representative KDoc in Phase 1 |

### Dependency Maintenance

Start with the latest stable release in the applicable major line. For components with an applicable LTS track, start with the current LTS line and its latest stable release. Verify compatibility before pinning or updating versions. Select or return to an older release only when a concrete blocker is documented with evidence.

Use the Gradle wrapper for Gradle, the Gradle catalog for Gradle inputs including images, `.java-version` for the Temurin JDK feature version, `mise.toml` for independent CLIs, `.nvmrc` for Node.js, `packageManager` and the lockfile for pnpm/npm, and SHA pins for GitHub Actions. Keep `.java-version` feature-only and record full observed JDK patch/build versions as evidence.

For a hold, record the affected scope, owner, confirmed blocker and supporting evidence, dated review or expiry (normally within seven days), and the exact retry or removal trigger. Record any renewal explicitly. Triage security notices, including upstream advisories, immediately. Expedite a verified fix in the narrow affected graph and escalate unfixed high risk or incomplete verification immediately.

Prefer updating the existing BOM or parent if it delivers the fix without widening the change. Otherwise, add a catalog-backed ordinary lower-bound constraint with a reason on the affected declarable configuration. Use a strict bound only when observed behavior shows it is necessary, and record why. Keep global force, exclusions, and fake direct dependencies out of the fix. Compare actual selected coordinates, incoming paths, selection causes, and complete affected and control graphs, including compile, runtime, other suites, and other roles as applicable. Run the applicable tests and repeat the graph and test checks when removing the constraint. The source brief cites the B17 scoped transitive review in `phases/01-axon-server-feasibility-and-build-foundation/01-13-PLAN.md#b17-reference-scoped-transitive-review`.

#### Private JVM Advisory Check

The source brief cites the B8 opt-in procedure in `phases/01-axon-server-feasibility-and-build-foundation/01-09-PLAN.md#b8-reference-private-jvm-advisory-check`. Its stated scope covers selected Maven coordinates, including transitives and BOM metadata, with project components excluded. It covers `runtimeClasspath` in `:command`, `:query`, and `:bff`, plus `:probe:testRuntimeClasspath` and `:probe:integrationTestRuntimeClasspath`. Recheck at least weekly and after a dependency change or relevant advisory. Keep inventories, the feed, and scanner output private. Escalate incomplete results and High/Critical findings immediately and triage unrated findings on their own evidence.

A complete no-match result applies only to the checked inventories and feed. Coverage excludes Gradle plugins, the toolchain and JDK, npm and other non-Maven inputs, container images and OS packages, and advisories absent from the feed. CI-02 (dependency update automation) and CI-03 (hosted dependency and built-image scanning) remain open.

#### Prior Dependency Review Records

The supplied records are dated **2026-11-24** and name the build maintainer as the owner for reviews by **2026-12-01**. Reconcile them against the selected graphs and runtime evidence in this checkout.

- **Guava scoped constraint.** Recheck sooner on relevant upstream or BOM changes. Remove the constraint only if upstream independently selects a compatible release unaffected by `GHSA-xxph-c9ww-hj94` / `CVE-2026-102554` in all consuming graphs and the graph comparisons, applicable tests, and private scan pass without it. [Advisory cited in the brief](https://osv.dev/vulnerability/GHSA-xxph-c9ww-hj94)
- **Explicit pgJDBC version.** Recheck whenever Spring Boot changes. Remove the explicit version only if the BOM independently supplies `42.7.15` or a verified newer fix in the consuming graphs and the role, worker, and runtime checks pass.
- **Axon Server and PostgreSQL images.** Recheck sooner on relevant security or terms changes. Before updating the catalog, review the replacement immutable index, the selected ARM64 and AMD64 child digests, the exact applicable terms, and a fresh local runtime result.

## Evolution

After each phase, reconcile shipped, invalidated, and newly discovered requirements. Record decision outcomes and update the description if it has drifted. At each milestone boundary, review all sections, check the core value, audit exclusions, and update the project context.

---

*Initialized 2026-11-24 from the project brief.*
