# Requirements for Axon 5 DCB Courses

**Defined:** 2026-11-24

**Core value:** Show how DCB enforces cross-entity business invariants without aggregates and explain the trade-offs with working code, tests, and documentation.

## v1 Requirements

### Build Foundation

- [x] **FND-01** Reproduce a Kotlin and Spring Boot compatibility probe that verifies the Axon 5 APIs, wiring, tagged conflict detection, and cross-process message routing in a DCB-enabled Axon Server context before pinning the version matrix. Record the official references, exact tested artifacts and image terms, bootstrap steps, and selected ARM64 and AMD64 image digests.
- [x] **FND-02** Build and check the toolchain with one authoritative version owner per ecosystem, pinned independent CLIs in mise, an inventory, and a `doctor` check. Keep `.java-version` at the Temurin feature version and record the actual build separately.
- [ ] **FND-03** Exchange type-prefixed UUIDv7 TypeIDs between Kotlin and TypeScript and round-trip them through native `uuid` storage.
- [ ] **FND-04** Build project images through Paketo Cloud Native Buildpacks, using `bootBuildImage` for JVM services and the Web Servers buildpack for the frontend. Package the static assets built by Gradle using npm and `package-lock.json`.
- [x] **FND-05** Run Gradle JVM Test Suites with shared Java Test Fixtures, JUnit 6, and compatible Kotest assertions and property tests. JUnit supplies the runner.
- [x] **FND-06** Build the frontend and documentation site from Gradle Node subprojects. On a clean `./gradlew build`, generate the frontend client from the BFF OpenAPI contract before building the frontend.

### Domain and Consistency

- [ ] **DCB-01** An admin can create a course with a name and capacity.
- [ ] **DCB-02** An admin can rename an existing course.
- [ ] **DCB-03** An admin can change a course’s capacity while preserving the capacity invariant for existing subscriptions.
- [ ] **DCB-04** An admin can register a student.
- [ ] **DCB-05** A registered student can subscribe to a course when the request satisfies the applicable rules.
- [ ] **DCB-06** A subscribed student can unsubscribe from a course and free the seat.
- [ ] **DCB-07** Course subscriptions never exceed capacity, including under concurrent attempts to claim the last seat.
- [ ] **DCB-08** A student’s active subscriptions never exceed the maximum, including concurrent attempts across courses.
- [ ] **DCB-09** Course names are unique across creates and renames. A committed rename releases the former name for reuse, and competing claims respect uniqueness.
- [ ] **DCB-10** Transfer a student atomically in one decision spanning the student and both courses. A rejected move preserves the existing subscription.
- [ ] **DCB-11** A student can join a waiting list for a full course. When a seat opens, automation requests promotion of the next student and the command path rechecks eligibility and capacity.
- [ ] **DCB-12** An admin can define course schedule slots, and a student cannot subscribe to overlapping courses.

### CQRS and Services

- [ ] **CQRS-01** The command service decides using relevant tagged event history. The query service builds dedicated projections from committed events and can rebuild the read models.
- [ ] **CQRS-02** The BFF reads course and student state through QueryBus and serves live initial results and subsequent updates through subscription queries.
- [ ] **CQRS-03** The command, query/projection, automation, and REST BFF services run as separately deployable roles. Axon Server is the DCB event store and interservice command and query router.
- [x] **CQRS-04** The BFF exposes an OpenAPI contract covering the browser’s commands, reads, and live view entry points.

### Frontend and Teaching UI

- [ ] **UI-01** A React and TypeScript UI uses Feature-Sliced Design with Steiger checks. A dedicated UI foundation defines reusable components and view patterns in Storybook.
- [ ] **UI-02** Each business feature has a UI-SPEC and a browser slice that exposes the operation, shows its outcome, and keeps related views live through subscription queries.
- [x] **UI-03** A reader can switch between an admin and individual demo students.
- [ ] **UI-04** A reader can use a dedicated teaching UI to browse and filter tagged events.
- [ ] **UI-05** A reader can inspect a selected command attempt and see the criteria and actual historical events that formed its decision boundary.
- [ ] **UI-06** A reader can run a concurrent last-seat demonstration and see both attempt outcomes and the committed capacity invariant.
- [ ] **UI-07** Target WCAG 2.2 AA with axe checks in component and E2E suites and a final UI review of the complete showcase.

### Testing and Code Quality

- [ ] **QA-01** Given–when–then unit tests verify DCB decision behavior, including rejections and conflicts.
- [ ] **QA-02** Component tests exercise the public boundaries of each service.
- [ ] **QA-03** Integration tests use Testcontainers to verify the selected Axon Server and database behavior, including cross-service interactions and contention.
- [ ] **QA-04** Playwright verifies browser workflows and architecture tests enforce backend module and frontend slice boundaries.
- [ ] **QA-05** A Gatling or k6 scenario drives concurrent subscriptions and reports results with the observed domain invariant.
- [ ] **QA-06** CI measures and publishes code coverage from the applicable test suites.
- [ ] **QA-07** Kotlin code is idiomatic and documented. Verify representative KDoc formatting with ktfmt, detekt `comments` checks, and Dokka `failOnWarning`.
- [ ] **QA-08** A pre-commit hook and CI apply the same formatting and style checks to all covered repository artifacts.

### CI/CD and Supply Chain

- [ ] **CI-01** GitHub Actions runs builds, every test level, coverage, static analysis, and container image builds.
- [ ] **CI-02** Renovate or Dependabot tracks dependency and tool updates using their authoritative declarations.
- [ ] **CI-03** Hosted CI scans dependencies and built images for vulnerabilities, and the repository for leaked secrets.
- [ ] **CI-04** Phase branches ship through `$gsd-ship` PRs. The remote requires PRs and passing checks on `main`, enforces linear history, allows squash merges only, and requires zero approvals.
- [ ] **CI-05** Release-please creates Git tags and releases. GSD milestone completion leaves tag creation disabled.
- [ ] **CI-06** Upstream defects and gaps have one `docs/upstream/` record per case after upstream reporting. CI checks links on marked workarounds.

### Runtime and Observability

- [ ] **OPS-01** A fresh checkout runs the full local system through one Docker Compose setup without vendor registration, manual license acquisition, or AxonIQ Platform credentials. Document the applicable runtime limit of this mode.
- [ ] **OPS-02** Docker Compose exposes metrics, traces, and logs via OpenTelemetry and a Grafana stack. A reader can follow a representative operation across the participating services.
- [ ] **OPS-03** The optional AxonIQ Platform connection can be enabled separately and is verified with the author’s account when credentials are supplied securely outside Git and planning artifacts.

### Documentation and Development Practice

- [ ] **DOC-01** The public README provides an overview, a reproducible quick start, and screenshots or diagrams.
- [ ] **DOC-02** A documentation site presents ADRs, C4 diagrams, and Event Modeling or Event Storming artifacts.
- [ ] **DOC-03** Diagrams and snippets explain the project’s DCB decisions and compare the same scenarios with Axon 4 aggregates, including trade-offs.
- [ ] **DOC-04** The repository retains `.planning/` history and publishes how AI-assisted development was used, including lessons learned.
- [ ] **DOC-05** Third-party and project-owned skills used locally are vetted and their compatibility with OpenCode is documented.
- [ ] **DOC-06** Document the dependency maintenance and private advisory procedure from the project brief, reconcile the cited review records against this checkout’s evidence, and keep private inputs and results outside the repository.

## User Stories

- As a reader migrating from Axon 4, I can observe an invariant under contention and follow the exact events that informed the decision.
- As an admin, I can manage courses and students and see the resulting changes in live views.
- As a demo student, I can enroll, withdraw, transfer, and see why a request was rejected or queued.

## Definition of Done

- Each applicable requirement has verified evidence recorded with its phase. The full demo starts from the documented Compose quick start and exercises the teaching scenarios.
- The browser, architecture, integration, load, coverage, and supply-chain checks produce reviewable results. The repository includes the comparative documentation and development history.
- Verify the optional Platform connection when the author provides credentials securely and record the outcome without exposing credentials.

## v2 Requirements

- **AUTH-01** Add real authentication and authorization, with OAuth2/OIDC or Keycloak considered during v2 planning.

## Out of Scope

| Exclusion | Reason |
| --- | --- |
| Executable Axon 4 aggregate implementation | Diagrams and snippets preserve the comparison within one maintained application. |
| Separate course and student command services | The reference requires one write-side boundary that can span both. |
| Kubernetes and cloud deployment | Docker Compose serves the local reference. |

## Traceability

| Requirement | Phase | Status |
| --- | --- | --- |
| FND-01 | Phase 1 | Complete |
| FND-02 | Phase 2 | Complete |
| FND-03 | Phase 3 | Pending |
| FND-04 | Phase 5 | Pending |
| FND-05 | Phase 2 | Complete |
| FND-06 | Phase 2 | Complete |
| DCB-01 | Phase 3 | Pending |
| DCB-02 | Phase 4 | Pending |
| DCB-03 | Phase 4 | Pending |
| DCB-04 | Phase 3 | Pending |
| DCB-05 | Phase 3 | Pending |
| DCB-06 | Phase 3 | Pending |
| DCB-07 | Phase 3 | Pending |
| DCB-08 | Phase 3 | Pending |
| DCB-09 | Phase 4 | Pending |
| DCB-10 | Phase 4 | Pending |
| DCB-11 | Phase 5 | Pending |
| DCB-12 | Phase 5 | Pending |
| CQRS-01 | Phase 3 | Pending |
| CQRS-02 | Phase 3 | Pending |
| CQRS-03 | Phase 5 | Pending |
| CQRS-04 | Phase 2 | Complete |
| UI-01 | Phase 2 | Pending |
| UI-02 | Phase 5 | Pending |
| UI-03 | Phase 2 | Complete |
| UI-04 | Phase 6 | Pending |
| UI-05 | Phase 6 | Pending |
| UI-06 | Phase 6 | Pending |
| UI-07 | Phase 8 | Pending |
| QA-01 | Phase 3 | Pending |
| QA-02 | Phase 5 | Pending |
| QA-03 | Phase 4 | Pending |
| QA-04 | Phase 6 | Pending |
| QA-05 | Phase 6 | Pending |
| QA-06 | Phase 7 | Pending |
| QA-07 | Phase 2 | Pending |
| QA-08 | Phase 2 | Pending |
| CI-01 | Phase 7 | Pending |
| CI-02 | Phase 7 | Pending |
| CI-03 | Phase 7 | Pending |
| CI-04 | Phase 7 | Pending |
| CI-05 | Phase 7 | Pending |
| CI-06 | Phase 7 | Pending |
| OPS-01 | Phase 7 | Pending |
| OPS-02 | Phase 6 | Pending |
| OPS-03 | Phase 7 | Pending |
| DOC-01 | Phase 8 | Pending |
| DOC-02 | Phase 8 | Pending |
| DOC-03 | Phase 8 | Pending |
| DOC-04 | Phase 8 | Pending |
| DOC-05 | Phase 8 | Pending |
| DOC-06 | Phase 2 | Pending |

All 52 v1 requirements map to one phase each.
