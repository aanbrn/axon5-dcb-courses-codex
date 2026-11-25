---
gsd_state_version: "1.0"
milestone: v1.0
milestone_name: Axon 5 DCB Courses
current_phase: 02
current_phase_name: Build and UI Foundations
current_plan: 4
status: executing
stopped_at: Completed 02-10-PLAN.md
last_updated: "2026-11-25T13:16:20.335Z"
last_activity: 2026-11-25
last_activity_desc: Completed the live role directory tracer
state_head: 11ad528b8895bedb57bf9c3b3d868cb284edf82c
progress:
  total_phases: 8
  completed_phases: 1
  total_plans: 16
  completed_plans: 8
  percent: 13
---

# Project State

## Project Reference

See [PROJECT.md](PROJECT.md), initialized 2026-11-24.

**Core value:** Show how DCB enforces cross-entity invariants without aggregates and explain the trade-offs with working code, tests, and documentation.
**Current focus:** Phase 02 — Build and UI Foundations

## Current Position

Phase: 02 (Build and UI Foundations)
Current Plan: 4
Total Plans in Phase: 11
Status: Ready to execute
Last activity: 2026-11-25 -- Completed the live role directory tracer

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

### Pending Todos

None yet.

### Blockers/Concerns

- The earlier Phase 1 references and dependency review records are context from the brief. Reconcile them against recovered or reproduced evidence in this checkout.
- Hosted repository controls and account-based Platform verification have external prerequisites. Record status as those checks are reached.

## Session Continuity

Last session: 2026-11-25T13:16:20.266Z
Stopped at: Completed 02-10-PLAN.md
Resume file: None
