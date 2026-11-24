# Phase 1: Axon Server and Toolchain Feasibility - Discussion Log

> Audit trail for human review. Use `01-CONTEXT.md` for planning, research, and execution decisions.

**Date:** 2026-11-24

**Phase:** 01 — Axon Server and Toolchain Feasibility

**Areas discussed:** Probe lifecycle, ARM64 and AMD64 verification, secondary probe blockers and frontend packaging, public quick start.

## Probe Lifecycle

| Question | Options considered | Selected |
| --- | --- | --- |
| Where should the probe live? | Dedicated `:probe` module in the shared Gradle build or a self-contained sample beside the Phase 1 materials. | Dedicated `:probe` module with shared version declarations. |
| When should it run? | Separate command or part of every `./gradlew build`. | Separate Docker-backed Gradle command. |
| Where should usage and evidence be recorded? | A module run guide plus a Phase 1 report or a single module document. | Short run guide and separate Phase 1 report. |
| Which terminology should the sample use? | Course and student terminology or neutral test entities. | Course and student terminology, with `courseId` and `studentId` tags. |

## ARM64 and AMD64 Verification

| Question | Options considered | Selected |
| --- | --- | --- |
| Which architectures are tested in Phase 1? | Full ARM64 run plus image digests for both architectures, or full runs on both. | Full ARM64 run and verified child digests for ARM64 and AMD64. |
| When should AMD64 run? | First available runner or the application image milestone. | First run on a GitHub Actions AMD64 runner once hosted CI is enabled. |
| Should `:probe` keep running after AMD64 verification? | Trigger on relevant changes, run on every PR, or replace the probe when full integration and browser coverage are available. | Use a temporary `:probe`. Use the replacement suite for the first AMD64 run if ready and retire the probe after the replacement coverage passes on AMD64 in hosted CI. |

The author pointed out that the project already plans integration and E2E suites in CI. That changed the discussion from a permanent probe schedule to what the suites must verify before the module can be retired. The Phase 1 evidence remains in the repository.

## Secondary Probe Blockers and Frontend Packaging

| Question | Options considered | Selected |
| --- | --- | --- |
| How should a secondary incompatibility affect Phase 1? | Record a reproducible blocker and defer the tool choice, or check a fallback in this phase. | Record the blocker and defer the tool choice when the core proof passes. |
| How should an external impediment be recorded? | Mark the probe `Unverified` and record a retry trigger, or delay the phase until every sample runs. | Record `Unverified`, the cause, and the retry trigger. |
| Which frontend package manager should be used? | Use npm for frontend and docs builds or keep the proposed pnpm frontend path. | Use npm and `package-lock.json`. Consider pnpm for specific tooling needs. |
| Who should build the frontend assets? | Gradle runs npm and builds the assets for Paketo, or Paketo builds the assets from source. | Gradle runs `npm ci` and builds static assets. Paketo Web Servers packages the result. |

The author asked what pnpm would add and identified tooling as the more likely use. The frontend test remains a small end-to-end packaging sample with npm.

## Public Quick Start

| Option | Description | Selected |
| --- | --- | --- |
| Registration-free quick start | Start from a clean checkout without registration, manual license acquisition, or a Platform token. Document applicable runtime limits. | Yes |
| Documented manual license acquisition | Let the reader obtain a license before running the sample. | |

The author noted the Individual plan and the 12-hour limit for standalone use. The official expiry reference applies that limit to Axon Server 2026.0 and later without a Platform connection or license file. The author confirmed registration-free startup and version selection under the project’s existing stable/LTS policy. [License expiry reference](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/) · [Individual plan](https://docs.axoniq.io/axoniq-platform-reference/billing/)

## Planner Discretion

Select versions and exact APIs after checking the documentation for the selected artifacts and reproducing the proof. Choose the minimum number of processes, tests, and configuration needed for the agreed evidence.

## Deferred Ideas

- Run the AMD64 verification once hosted CI is enabled.
- Consider pnpm when a concrete tooling need arises.
- Verify the optional Platform path with the author’s account when credentials are supplied securely.
