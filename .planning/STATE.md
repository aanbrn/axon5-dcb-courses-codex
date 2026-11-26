---
gsd_state_version: "1.0"
milestone: v1.0
milestone_name: Axon 5 DCB Courses
current_phase: 3
current_phase_name: Core Enrollment and Live Views
current_plan: Not started
status: planning
stopped_at: Phase 02 local verification passed. PR publication authorization and hosted build-and-style are pending.
last_updated: "2026-11-26T09:42:19.526Z"
last_activity: 2026-11-26
last_activity_desc: Phase 02 complete, transitioned to Phase 3
state_head: 4873ae565b901bba23a81b36058522c9455bbf3e
progress:
  total_phases: 8
  completed_phases: 2
  total_plans: 16
  completed_plans: 16
  percent: 25
---

# Project State

## Project Reference

See [PROJECT.md](PROJECT.md), initialized 2026-11-24.

**Core value:** Show how DCB enforces cross-entity invariants without aggregates and explain the trade-offs with working code, tests, and documentation.
**Current focus:** Publish Phase 02 and verify its hosted check before starting Phase 3.

## Current Position

Phase: 3 — Core Enrollment and Live Views
Current Plan: Not started
Total Plans in Phase: 0
Status: Ready to plan after Phase 02 ship. PR publication authorization and hosted `build-and-style` are pending.
Last activity: 2026-11-26 — Phase 02 complete, transitioned to Phase 3

Progress: [███░░░░░░░] 25%

## Performance Metrics

- Total plans completed: 0
- Total execution time: 0 hours

**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 60min | 2 tasks | 9 files |
| Phase 01 P02 | 82min | 3 tasks | 10 files |
| Phase 01 P03 | 393min | 3 tasks | 9 files |
| Phase 01 P04 | 21min | 3 tasks | 9 files |
| Phase 01 P05 | 47min | 2 tasks | 6 files |
| Phase 02 P01 | 12m20s | 2 tasks | 15 files |
| Phase 02 P02 | 18m54s | 3 tasks | 10 files |
| Phase 02 P10 | 12m14s | 2 tasks | 5 files |
| Phase 02 P03 | 16m40s | 2 tasks | 6 files |
| Phase 02 P05 | 13m55s | 2 tasks | 9 files |
| Phase 02 P04 | 25m16s | 3 tasks | 16 files |
| Phase 02 P06 | 15m50s | 2 tasks | 15 files |
| Phase 02 P11 | 18m51s | 2 tasks | 15 files |
| Phase 02 P07 | 21m00s | 3 tasks | 8 files |
| Phase 02 P08 | 17m50s | 2 tasks | 5 files |
| Phase 02 P09 | 28m05s | 2 tasks | 45 files |

## Accumulated Context

### Decisions

- The v1.0 roadmap uses vertical MVP phases and defers repository-wide release verification to the final phases.
- Phase 1 must reproduce the Axon Server compatibility probe before committing the version matrix.
- Phase 1 uses small TypeID, JUnit/Kotest, KDoc, and pnpm/Paketo samples. Shared build conventions, application IDs, and deliverable images follow in later phases.
- Version selection starts from current stable and applicable LTS releases. Choosing an older release requires a documented blocker.
- GSD uses one branch per phase and disables tag creation. Release-please owns release tags.
- [Phase 01]: Gradle-driven npm builds and Paketo static packaging supersede the earlier pnpm frontend sample. See 01-CONTEXT.md.
- [Phase 01]: Give the phased projection an isolated token store and resolve its pooled processor from the Axon event processor module.
- [Phase 01]: Use .java-version as the Temurin feature owner and validate each secondary stage against a complete current native core proof.
- [Phase 01]: Use Node 26.13.1 and npm 12.2.3 through their separate version owners, with the Gradle Node plugin confined to the nested web build.
- [Phase 01]: Package only the validated staged public tree with the digest-pinned Paketo Jammy builder, run image and Web Servers buildpack.
- [Phase 01]: Measure Kotlin/Jupiter/Kotest, ktfmt, and TypeID from explicit Gradle tasks with isolated JVM and npm dependencies.
- [Phase 01]: Scope the npm uuid advisory assessment to the temporary TypeID probe. Keep application adoption open and review by 2026-12-02.
- [Phase 01]: Record a native acceptance tuple with its tested revision, input SHA-256, and manifest SHA-256.
- [Phase 01]: Constrain Guava in the consuming runtime and formatter graphs with separate scoped, catalog-backed lower bounds.
- [Phase 01]: Preserve the permanent report and require hosted AMD64 Testcontainers and Playwright coverage before probe retirement.
- [Phase 02]: Keep the canonical OpenAPI file as the published Gradle artifact and Spring static resource.
- [Phase 02]: Disable implicit npm lifecycle scripts and provision the pinned Chromium through an explicit task.
- [Phase 02]: Use the root Gradle catalog and .java-version in the reusable JVM convention.
- [Phase 02]: Restrict NetworkNT to the BFF component suite and allow schema references only within the packaged contract.
- [Phase 02]: Load the Kotlin plugins in the root classpath and aggregate the BFF and web lifecycles using task providers.
- [Phase 02]: Use the managed Node test runner with the existing Vite module loader and preserve the approved npm inputs.
- [Phase 02]: Reject Fetch redirects so the documented status is checked at the original operation URL.
- [Phase 02]: Keep role selection in tab-local storage and reconcile the whole stored identifier after directory validation.
- [Phase 02]: Run browser component checks using the pinned Playwright and Vite dependencies in the opt-in smoke task.
- [Phase 02]: Capture retry focus when the button leaves the DOM and restore it after the selector is enabled.
- [Phase 02]: Share Kotlin formatting and comments commands through the JVM convention and scope the Guava JRE floor to ktfmtTool.
- [Phase 02]: Publish BFF main and public fixture helpers from testFixtures with reportUndocumented and failOnWarning enabled.
- [Phase 02]: Accept the explicitly approved Eleventy 3.1.8 identity after managed npm ci, Gradle, and canonical Markdown rendering qualify the exact lock.
- [Phase 02]: Fail the build for invalid launch configuration. Allow the local Vite origin and explicitly configured HTTPS deployment origins.
- [Phase 02]: Serve the verified documentation tree through the managed Node runtime with an explicit IPv4 loopback bind.
- [Phase 02]: Generate only the official radix-nova primitives and use the project-owned clsx and tailwind-merge helper.
- [Phase 02]: Measure native selected text against the control content width and display the complete value when it clips.
- [Phase 02]: Build static Storybook during assemble and require explicit Chromium provisioning for storyTest and foundationProof.
- [Phase 02]: Use public FSD entry points for the home slice and shared API, with Steiger scanning authored source.
- [Phase 02]: Scope TypeScript 5.9.3 to the approved Steiger plugin to satisfy tsconfck's peer and review the package extension by 2026-12-02.
- [Phase 02]: Use the same rules over raw staged blobs and checked-out tracked files, with configuration from the corresponding snapshot.
- [Phase 02]: Validate the whole candidate before taking the Git index lock and replacing the original index.
- [Phase 02]: Preserve Phase 01 evidence and npm-owned lock bytes while checking their text or structured content.
- [Phase 02]: Doctor probes existing managed executables and identifies the setup command for an unprovisioned consumer.
- [Phase 02]: Preserve each existing Guava constraint on its owning configuration and compare changes using the current tooling with just those constraints removed.
- [Phase 02]: Keep the B8 private result incomplete and publish only the scoped procedure and public evidence.
- [Phase 02]: Keep the style hook's generated tool manifest in Gradle project state so the installed hook remains usable after a clean build.
- [Phase 02]: Use the existing locked YAML parser to verify the exact read-only pull request workflow and its approved actions.

### Pending Todos

None yet.

### Blockers/Concerns

- The earlier Phase 1 references and dependency review records are context from the brief. Reconcile them against recovered or reproduced evidence in this checkout.
- Hosted repository controls and account-based Platform verification have external prerequisites. Record status as those checks are reached.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261126-fhh | Document mise and enable canonical Java and Node version files | 2026-11-26 | d92322e | [261126-fhh-document-mise-and-enable-canonical-java-](./quick/261126-fhh-document-mise-and-enable-canonical-java-/) |
| 2 | Add local Kotlin inspections with Qodana | 2026-11-26 | 390ffd7 | — |
| 261126-fxn | Pin Python and lint the PR workflows | 2026-11-26 | 99f4d32 | [261126-fxn-pin-python-for-local-tooling-and-the-pr-](./quick/261126-fxn-pin-python-for-local-tooling-and-the-pr-/) |
| 261126-g7q | Assess the technical maturity of Phases 1 and 2 | 2026-11-26 | 90333e6 | [261126-g7q-reassess-the-tooling-built-in-phases-1-a](./quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/) |
| 261126-i4h | Resolve actionable Qodana findings | 2026-11-26 | dcf3504 | [261126-i4h-resolve-actionable-qodana-findings](./quick/261126-i4h-resolve-actionable-qodana-findings/) |
| 261126-ink | Qualify Axon and Spring inspection support in Qodana | 2026-11-26 | c413c15 | [261126-ink-qualify-axon-and-spring-inspection-suppo](./quick/261126-ink-qualify-axon-and-spring-inspection-suppo/) |
| 261126-jp0 | Recognize Spring Bean entry points in Qodana Community | 2026-11-26 | b838a25 | [261126-jp0-recognize-spring-bean-entry-points-in-qo](./quick/261126-jp0-recognize-spring-bean-entry-points-in-qo/) |
| 261126-jsl | Reduce intentional Gradle incubation noise in IntelliJ IDEA | 2026-11-26 | fff0b35 | [261126-jsl-reduce-intentional-gradle-incubation-noi](./quick/261126-jsl-reduce-intentional-gradle-incubation-noi/) |
| 9 | Record live IntelliJ inspection profile verification | 2026-11-26 | 3b26378 | — |
| 261126-lmx | Validate rendered docs links and distinguish code landmarks | 2026-11-26 | a702e28 | [261126-lmx-validate-rendered-docs-links-and-disting](./quick/261126-lmx-validate-rendered-docs-links-and-disting/) |
| 261126-lmn | Reject invalid demo shell settings and role data | 2026-11-26 | cca11b1 | [261126-lmn-reject-invalid-demo-shell-settings-and-r](./quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/) |
| 261126-lmh | Isolate historical Qodana scans from IDEA profiles | 2026-11-26 | 3df371b | [261126-lmh-isolate-historical-qodana-scans-from-ide](./quick/261126-lmh-isolate-historical-qodana-scans-from-ide/) |
| 261126-mcu | Match published link verification to browser and local routes | 2026-11-26 | c967802 | [261126-mcu-match-published-link-verification-to-bro](./quick/261126-mcu-match-published-link-verification-to-bro/) |
| 261126-mdh | Invalidate the Vite build when dotenv expansion inputs change | 2026-11-26 | 68c43a0 | [261126-mdh-invalidate-the-vite-build-when-dotenv-ex](./quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/) |
| 261126-mq2 | Use browser-conforming HTML parsing for publication checks | 2026-11-26 | 1ca7bf9 | [261126-mq2-use-browser-conforming-html-parsing-for-](./quick/261126-mq2-use-browser-conforming-html-parsing-for-/) |

## Session Continuity

Last session: 2026-11-26T09:42:19.442Z
Stopped at: Phase 02 local verification passed. PR publication authorization and hosted build-and-style are pending.
Resume file: .planning/phases/02-build-and-ui-foundations/02-VERIFICATION.md
