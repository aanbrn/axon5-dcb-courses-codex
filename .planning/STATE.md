---
gsd_state_version: "1.0"
milestone: v1.0
milestone_name: Axon 5 DCB Courses
current_phase: 02
current_phase_name: Build and UI Foundations
current_plan: 8
status: executing
stopped_at: Completed 02-06-PLAN.md
last_updated: "2026-11-25T14:47:20.934Z"
last_activity: 2026-11-25
last_activity_desc: Completed per-tab demo roles and directory recovery
state_head: b3f56b2b6833ab014ada8bdb29367977fdd50f4d
progress:
  total_phases: 8
  completed_phases: 1
  total_plans: 16
  completed_plans: 12
  percent: 13
---

# Project State

## Project Reference

See [PROJECT.md](PROJECT.md), initialized 2026-11-24.

**Core value:** Show how DCB enforces cross-entity invariants without aggregates and explain the trade-offs with working code, tests, and documentation.
**Current focus:** Phase 02 — Build and UI Foundations

## Current Position

Phase: 02 (Build and UI Foundations)
Current Plan: 8
Total Plans in Phase: 11
Status: Ready to execute
Last activity: 2026-11-25 -- Completed per-tab demo roles and directory recovery

Progress: [█░░░░░░░░░] 13%

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

### Pending Todos

None yet.

### Blockers/Concerns

- The earlier Phase 1 references and dependency review records are context from the brief. Reconcile them against recovered or reproduced evidence in this checkout.
- Hosted repository controls and account-based Platform verification have external prerequisites. Record status as those checks are reached.

## Session Continuity

Last session: 2026-11-25T14:47:20.861Z
Stopped at: Completed 02-06-PLAN.md
Resume file: None
