# Pitfalls Research

**Project:** Axon 5 DCB Courses

**Date:** 2026-11-24

## Feasibility and Build Foundation

- **A successful boot misses a context or routing mismatch.** Verify the named context is DCB-enabled, run a tagged write with multiple tags, force overlapping appends, and check cross-process command, query, and subscription routing. Inspect the exact distribution, terms, and dependency coordinates used by the proof. [Axon Server DCB contexts](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/administration/multi-context/) · [Axoniq Framework licensing](https://docs.axoniq.io/axoniq-platform-reference/licensing/)
- **A declared dependency version differs from selection.** Compare the resolved affected and control graphs, selection reasons, and incoming paths before and after a scoped change. Prefer a compatible BOM update first, then use a catalog-backed constraint where the project policy calls for one. Run the applicable suites and repeat the comparisons at removal. [Gradle dependency constraints](https://docs.gradle.org/current/userguide/dependency_constraints.html) · [Gradle dependency reports](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html)
- **Image tags and frontend package tooling drift.** Capture image index and child digests, verify the applicable CPU targets, reproduce the npm build and Paketo packaging, and keep inputs under their assigned version owners. [Paketo Web Servers](https://paketo.io/docs/howto/web-servers/)

## Business Decisions and Delivery

- **An incomplete selector permits invalid writes.** List the state consulted by each command and the events that can change it during the decision. For each invariant, test an overlapping conflicting pair and an unrelated pair that should proceed independently. Inspect effective append criteria in addition to the events read. [Axon event store internals](https://docs.axoniq.io/axon-framework-reference/5.1/events/event-store-internals/)
- **A rename reserves the new name without releasing the old name.** Exercise races against both claims and keep changes in one append. Define normalization and ownership semantics before implementing. [DCB uniqueness example](https://dcb.events/examples/unique-username/)
- **Schedule changes race with enrollment.** Decide how schedule edits interact with existing subscriptions, check adjacent intervals and concurrent changes, and cover the schedules and enrollments whose events could change the result.
- **Repeated vacancy events promote twice or bypass an invariant.** Give each promotion request a stable identity. Reevaluate availability and eligibility in the command service and test repeated delivery, processor restart, and a competing direct request. Define what happens when the next queued student is temporarily ineligible.
- **The UI mistakes an accepted command for a visible projection update.** Test the initial result, committed update delivery, reconnect, cleanup, and fresh state after a disconnect. Use the committed domain state when explaining a race outcome. [Axon subscription queries](https://docs.axoniq.io/axon-framework-reference/5.0/queries/infrastructure/)

## Showcase and Release

- **The teaching view reconstructs the wrong historical decision.** Check it against the recorded command attempt and verify matching through concurrent activity, rejected operations, and retries.
- **An axe pass misses a live-view interaction problem.** Review focus restoration, keyboard flows, and announcements for status changes in addition to scanning rendered components and pages. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- **Optional integrations become mandatory at startup.** Test a clean Compose run without Platform credentials and validate account connection separately through secret injection. [Axon Framework Client](https://docs.axoniq.io/axoniq-platform-reference/connectors/axon-framework/)
