# Axon 5 DCB Courses Roadmap

## v1.0 — Axon 5 DCB Courses

The v1.0 milestone starts with a reproducible Axon Server DCB proof, followed by the shared build and UI foundation. It then ships complete enrollment, transfer, scheduling, and waitlist workflows through the browser. The final phases turn the verified behavior into a teaching demo and publish the operating and release evidence.

Build, browser, architecture, and CI checks grow alongside the features they exercise. Each requirement is mapped to the phase that verifies its full scope.

## Phases

- [x] **Phase 1: Axon Server and Toolchain Feasibility** - Run the DCB compatibility probe and record the evidence for stack selection. (completed 2026-11-25)
- [ ] **Phase 2: Build and UI Foundations** - Set up the shared build, test conventions, and browser shell with a generated OpenAPI client.
- [ ] **Phase 3: Core Enrollment and Live Views** - Ship a complete course and student enrollment workflow with live updates and contention tests.
- [ ] **Phase 4: Course Names and Atomic Transfers** - Teach cross-entity decisions through unique names, capacity changes, and transfers.
- [ ] **Phase 5: Scheduling and Waitlist Automation** - Apply schedule constraints, promote eligible students, and package the complete set of application roles.
- [ ] **Phase 6: DCB Teaching Experience** - Let readers inspect decisions, run a last-seat race, and follow its telemetry.
- [ ] **Phase 7: Local Operations and Delivery** - Verify the full Compose quick start and hosted delivery controls.
- [ ] **Phase 8: Documentation and Showcase Review** - Publish the Axon 4 comparison, project artifacts, and AI development record.

## Phase Details

### Phase 1: Axon Server and Toolchain Feasibility

**Goal:** As a maintainer, I want to select a compatible stack by running a repeatable DCB probe and targeted toolchain checks, so that readers can reproduce the stack selection.
**Mode:** mvp
**Depends on:** None
**Requirements:** FND-01
**Success Criteria**:

1. Using a minimal Spring Boot probe on ARM64, a maintainer starts a clean DCB context without vendor registration, manual license acquisition, or Platform credentials and observes a multi-tag write, a rejected overlapping append, and a cross-process command, query, and subscription update.
2. The probe report records the exact artifacts, applicable image and connector terms, bootstrap steps, selected ARM64 and AMD64 digests, observed Temurin build, and relevant findings from the earlier dependency reviews. The version matrix starts from current stable and applicable LTS releases, and cites the verification evidence and any blocker that required an older release.
3. Small independent samples record TypeID interoperability between Kotlin and TypeScript, Kotlin 2.4 with JUnit 6 and Kotest, ktfmt behavior on representative KDoc, and the frontend path from a Gradle-driven npm build to packaging static assets with Paketo. Each check records a reproducible result or a concrete blocker before the affected tooling is adopted.

**Plans:** 5/5 plans complete
**Wave 1**
- [x] 01-01-PLAN.md

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-02-PLAN.md

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 01-03-PLAN.md

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 01-04-PLAN.md

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 01-05-PLAN.md

### Phase 2: Build and UI Foundations

**Goal:** As a maintainer, I want to build and test the demo shell and generated BFF client through shared conventions, so that I can verify later feature slices from a clean checkout.
**Mode:** mvp
**Depends on:** Phase 1
**Requirements:** FND-02, FND-05, FND-06, CQRS-04, UI-01, UI-03, QA-07, QA-08, DOC-06
**UI hint:** yes
**Success Criteria**:

1. A clean `./gradlew build` builds the documentation site and generates the frontend client from the BFF OpenAPI contract before building the frontend.
2. A reader can open the React shell and switch between admin and individual demo students. Shared components and loading, empty, and error states are inspectable in Storybook.
3. The initial UI-SPEC documents the design foundation, the frontend passes Steiger checks, and the contract gives feature slices an entry point for browser commands, reads, and live views.
4. A maintainer can run `doctor`, audit authoritative version owners, and run JUnit 6 and Kotest through Gradle JVM Test Suites with shared Java Test Fixtures. The documented dependency maintenance process links recovered or reproduced evidence and keeps advisory inputs and results private.
5. The pre-commit hook and CI use the same repository formatting and style checks. Representative Kotlin and KDoc pass ktfmt and detekt, and a Dokka warning fails the build.

**Plans:** 2/11 plans executed
**Wave 1**
- [x] 02-01-PLAN.md

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 02-02-PLAN.md
- [ ] 02-10-PLAN.md

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 02-03-PLAN.md
- [ ] 02-04-PLAN.md
- [ ] 02-05-PLAN.md

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 02-06-PLAN.md

**Wave 5** *(blocked on Wave 4 completion)*
- [ ] 02-11-PLAN.md

**Wave 6** *(blocked on Wave 5 completion)*
- [ ] 02-07-PLAN.md

**Wave 7** *(blocked on Wave 6 completion)*
- [ ] 02-08-PLAN.md

**Wave 8** *(blocked on Wave 7 completion)*
- [ ] 02-09-PLAN.md

### Phase 3: Core Enrollment and Live Views

**Goal:** Deliver enrollment and withdrawal through the real command service, projections, BFF, and browser.
**Mode:** mvp
**Depends on:** Phase 2
**Requirements:** FND-03, DCB-01, DCB-04, DCB-05, DCB-06, DCB-07, DCB-08, CQRS-01, CQRS-02, QA-01
**UI hint:** yes
**Success Criteria**:

1. An admin can create a course and register a student. In student mode, the reader can subscribe, see the live result, and unsubscribe to reopen the seat.
2. Concurrent attempts to claim a final seat or a student’s remaining allowance cannot exceed the corresponding limit. A reader sees the committed projection update through the BFF subscription stream.
3. A maintainer can rebuild the dedicated read models from committed events and verify initial query results and subsequent updates independent of the write decisions.
4. Given–when–then tests and an initial Testcontainers race verify the enrollment invariants. An initial Playwright workflow and architecture checks cover the slice.
5. Course and student TypeIDs round-trip between the Kotlin and TypeScript contracts and native UUID storage.

**Plans:** TBD

### Phase 4: Course Names and Atomic Transfers

**Goal:** Demonstrate coordinated decisions across names, existing subscriptions, and multiple courses.
**Mode:** mvp
**Depends on:** Phase 3
**Requirements:** DCB-02, DCB-03, DCB-09, DCB-10, QA-03
**UI hint:** yes
**Success Criteria**:

1. An admin can rename a course, and the prior name becomes available after the rename commits. Competing requests for a name allow only one owner.
2. An admin can change a course’s capacity when the new capacity accommodates active subscriptions. Attempts that would break the invariant are rejected and the previous capacity remains visible.
3. A student can transfer across courses in one committed decision. A rejected transfer leaves the source subscription intact. The live views show the resulting state for the student and both courses.
4. The reproducible Testcontainers suite exercises real Axon Server and database interactions across the command service, query service, and BFF. It verifies contention for enrollment, competing name claims, and transfers using committed event and projection state.

**Plans:** TBD

### Phase 5: Scheduling and Waitlist Automation

**Goal:** Extend enrollment with schedule constraints and vacancy-driven promotion and verify all four roles as runnable images.
**Mode:** mvp
**Depends on:** Phase 4
**Requirements:** FND-04, DCB-11, DCB-12, CQRS-03, UI-02, QA-02
**UI hint:** yes
**Success Criteria**:

1. An admin can define schedule slots. A student can see why an overlapping enrollment is rejected and can enroll in an eligible non-overlapping course.
2. A student can join a full course’s waiting list. When a seat opens, the automation service requests promotion and the command service rechecks eligibility and capacity. Duplicate delivery or a competing enrollment cannot overbook the course.
3. A maintainer can run and component-test all four service roles independently with Axon Server routing. Browser views show queue and promotion outcomes through subscription updates.
4. Every business operation through this phase has a UI-SPEC and a browser slice that shows the outcome and updates related views.
5. Using the verified buildpack path, a maintainer builds and starts all application role images with `bootBuildImage` and packages the Gradle-built frontend assets with Paketo Web Servers. The integration suite covers automation restart and delivery against Axon Server and the database.

**Plans:** TBD

### Phase 6: DCB Teaching Experience

**Goal:** Make actual command boundaries and concurrency outcomes inspectable in the showcase and traceable across services.
**Mode:** mvp
**Depends on:** Phase 5
**Requirements:** UI-04, UI-05, UI-06, QA-04, QA-05, OPS-02
**UI hint:** yes
**Success Criteria**:

1. A reader can filter the event timeline by tags and open a command attempt to see its criteria and actual historical events. Concurrent activity after the attempt does not change the displayed history for that attempt.
2. A reader can trigger competing requests for one seat and inspect accepted and rejected or queued outcomes alongside the committed enrollment count.
3. A maintainer can reproduce a concurrent workload with Gatling or k6 and compare reported results with the final domain state.
4. In the local Compose setup, a maintainer follows a representative operation across participating services using Grafana metrics, traces, and logs backed by OpenTelemetry.
5. Playwright exercises the business and teaching workflows across the assembled application, and architecture checks enforce backend module and frontend slice boundaries.

**Plans:** TBD

### Phase 7: Local Operations and Delivery

**Goal:** Verify the full Compose quick start and hosted delivery controls using the previously exercised images and checks.
**Mode:** mvp
**Depends on:** Phase 6
**Requirements:** CI-01, CI-02, CI-03, CI-04, CI-05, CI-06, QA-06, OPS-01, OPS-03
**Success Criteria**:

1. A reader launches the complete demo and its observability stack from a fresh checkout through one Docker Compose setup without vendor registration, manual license acquisition, or Platform credentials. The quick start documents any applicable runtime limit.
2. The optional AxonIQ Platform path is documented and configurable independently. When the author supplies credentials securely, record a successful account connection without exposing credentials.
3. A hosted PR run produces build, test, coverage, analysis, dependency and image scan, and secret scan results. It uses the existing JVM and frontend buildpack image tasks. A GitHub Actions AMD64 runner provides the first AMD64 runtime evidence for the DCB proof. Update automation targets the established version owners.
4. The remote demonstrates required PRs and checks, linear history, squash-only merges, and zero required approvals. The release-please workflow owns release creation and tags, with GSD tag creation disabled.
5. A maintainer can trace a marked workaround to its upstream record, and CI reports missing links.

**Plans:** TBD

### Phase 8: Documentation and Showcase Review

**Goal:** Publish the reader experience and complete accessibility and documentation review across the full demo.
**Mode:** mvp
**Depends on:** Phase 7
**Requirements:** UI-07, DOC-01, DOC-02, DOC-03, DOC-04, DOC-05
**UI hint:** yes
**Success Criteria**:

1. A new reader follows the README quick start, reaches the demo from a fresh checkout, and uses the screenshots or diagrams to locate its main scenarios.
2. The docs site contains ADRs, C4 diagrams, and Event Modeling or Event Storming artifacts. A reader can compare the project’s DCB and Axon 4 aggregate scenarios in diagrams and snippets and understand the trade-offs.
3. The repository preserves planning history and lessons from AI-assisted development. Records identify the vetted project-owned and third-party skills and how their OpenCode compatibility was checked.
4. Component and browser suites report axe results, and the completed showcase has a UI review of keyboard, focus, and live status behavior against the WCAG 2.2 AA target.

**Plans:** TBD

## Progress

| Phase | Plans Complete | Status | Completed |
| --- | --- | --- | --- |
| 1. Axon Server and Toolchain Feasibility | 5/5 | Complete    | 2026-11-25 |
| 2. Build and UI Foundations | 2/11 | In Progress | - |
| 3. Core Enrollment and Live Views | 0/TBD | Not started | - |
| 4. Course Names and Atomic Transfers | 0/TBD | Not started | - |
| 5. Scheduling and Waitlist Automation | 0/TBD | Not started | - |
| 6. DCB Teaching Experience | 0/TBD | Not started | - |
| 7. Local Operations and Delivery | 0/TBD | Not started | - |
| 8. Documentation and Showcase Review | 0/TBD | Not started | - |
