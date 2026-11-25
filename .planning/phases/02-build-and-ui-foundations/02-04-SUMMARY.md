---
phase: 02-build-and-ui-foundations
plan: "04"
subsystem: docs
tags: [eleventy, gradle, node, npm, static-site, publication]
requires:
  - phase: 01-05
    provides: Canonical Phase 1 feasibility report and probe retirement criteria
  - phase: 02-02
    provides: Contract-checked BFF role directory
  - phase: 02-10
    provides: Root production lifecycle and clean generated-client build
provides:
  - Four documentation routes generated from an explicit Gradle staging allowlist
  - A configurable demo action and verified root and prefixed navigation
  - Publication checks for allowlisted files, fragments, and launch URL policy
  - A loopback preview of the production documentation output
affects: [02-06, 02-08, 02-09, 07]
tech-stack:
  added: ["@11ty/eleventy@3.1.8"]
  patterns: [byte-preserving Gradle Sync, Eleventy HTML Base, fail-closed static publication]
key-files:
  created:
    - docs-site/build.gradle.kts
    - docs-site/package.json
    - docs-site/package-lock.json
    - docs-site/eleventy.config.mjs
    - docs-site/serve.mjs
    - docs-site/verify-site.mjs
    - docs-site/src/index.11ty.js
    - docs-site/src/_includes/page.11ty.js
    - docs-site/src/feasibility/phase-01.11tydata.json
    - docs-site/src/site.css
    - docs-site/test/site.test.mjs
    - docs/quick-start.md
    - docs/maintainer-guide.md
  modified:
    - build.gradle.kts
    - settings.gradle.kts
    - docs/feasibility/phase-01.md
key-decisions:
  - "Accept the explicitly approved Eleventy 3.1.8 identity after managed npm ci, Gradle, and canonical Markdown rendering qualify the exact lock."
  - "Fail the build for invalid launch configuration. Allow the local Vite origin and explicitly configured HTTPS deployment origins."
  - "Serve the verified documentation tree through the managed Node runtime with an explicit IPv4 loopback bind."
patterns-established:
  - Render the canonical report with Markdown preprocessing disabled and layout defined in Eleventy page data.
  - Validate the exact static artifact list and internal destinations after each Eleventy render.
requirements-completed: [FND-06]
coverage:
  - id: D1
    description: Clean Gradle build generates the browser client first and produces the frontend and static documentation with Docker unreachable.
    requirement: FND-06
    verification:
      - kind: integration
        ref: "DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain clean build"
        status: pass
    human_judgment: false
  - id: D2
    description: Both launch modes and all four documentation routes pass root and nested path checks with an exact file list.
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :docs-site:check"
        status: pass
      - kind: integration
        ref: "./gradlew --console=plain :docs-site:check -PdocsBase=/courses/ -PdocsAppUrl=http://127.0.0.1:5173/"
        status: pass
    human_judgment: false
actuals:
  tokens: 26751
  tasks: 3
  commits: 4
commits: 4
plan_head_before: d83e5628d543cc823689a94cf1495707a563851d
plan_head_after: 9a081b7fca13fae4111cc69a513f549507d40d48
duration: 25m16s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 04: Public Documentation Site Summary

**The clean Gradle build now produces four documentation routes, preserves the canonical feasibility report byte for byte during staging, and checks each publication for broken navigation and unexpected files.**

## Performance

- Started at 2026-11-25T13:58:27Z and completed execution evidence at 2026-11-25T14:23:43Z.
- Completed three tasks covering 16 files.

## Accomplishments

- The home page offers one launch action. The default opens the local quick start. A trusted app URL opens the demo. The deployment base applies to navigation, assets, and cross-page fragments.
- The quick start explains the local BFF, Vite and docs processes, per-tab roles, retry, and extension of the contract-first `listDemoRoles` operation. The maintainer guide links authoritative version files, the probe runbook, and the retirement criteria.
- The Phase 1 report retains the native ARM64 proof and both image child metadata records. Phase 7 owns the first hosted AMD64 DCB runtime proof through equivalent application suites or `:probe`. Probe retirement still requires the committed multi-tag write, overlapping append rejection, correlated cross-process subscription update, and a representative Playwright workflow.
- Gradle stages only the seven named public inputs. Eleventy writes four pages and one CSS asset. The preview serves those verified files on `127.0.0.1:8081`.

## Package Disposition

GSD classified `@11ty/eleventy` as SUS for the sole `too-new` flag. The user explicitly approved exact version `3.1.8`. The npm manifest names `11ty/buildawesome` and declares no install lifecycle hook. The stable publisher release and the locked tarball SHA-512 matched the reviewed identity. The separate explicit approval for `prettier@3.10.1` belongs to 02-07. [Eleventy 3.1.8 publisher release](https://github.com/11ty/buildawesome/releases/tag/v3.1.8)

The isolated candidate resolved all locked artifacts to `registry.npmjs.org` with SHA-512 integrity. Managed npm `12.2.3` installed 113 packages using `npm ci --ignore-scripts` without changing the lock. The managed Node runtime was `26.13.1`. The real Gradle build and direct Eleventy rendering preserved report heading anchors, fenced shell examples, and tables before the pin was committed. [Eleventy Markdown configuration](https://www.11ty.dev/docs/languages/markdown/) [Eleventy HTML Base](https://www.11ty.dev/docs/plugins/html-base/)

## Verification

| Check | Observed evidence |
| --- | --- |
| `./gradlew --console=plain :docs-site:docsBuild` and `:docs-site:docsBuild -PdocsBase=/courses/` | Home, quick start, report, and guide rendered with the base-qualified stylesheet. Heading, fence and table checks passed. |
| `./gradlew --console=plain :docs-site:check` and `:docs-site:check -PdocsBase=/courses/ -PdocsAppUrl=http://127.0.0.1:5173/` | 13 of 13 TAP assertions passed in both modes. The tests exercised HTTPS deployment allowlisting, the local Vite origin, invalid schemes and origins, a broken fragment, and deliberate filename and byte contamination. |
| Disposable source and owner mutations | A synthetic Markdown file in each source directory was absent by name and bytes from staging and output. A linked public source failed before copying. Invalid `.nvmrc` and `packageManager` inputs failed in the docs Gradle script. |
| `:docs-site:serve` at `/` and `/courses/` | The process printed the actual bound URL. The only listener was `127.0.0.1:8081`. All four routes and CSS returned HTTP 200 in both runs. Served navigation, report and skip fragments, and the applicable launch action matched. |
| Chrome 158.0.8127.89 on the local preview | All four pages fit at 320px, 768px and 1280px after doubling the root text size. Tab and Enter moved focus to main content. Focused table and code regions scrolled horizontally by keyboard and displayed a 2px outline. |
| `DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain clean build` | A fresh source copy built both Node subprojects. `:web:generateClient` ran before `:web:webBuild`. The BFF component and unit suites passed, along with 13 docs checks and 19 web checks. The final repeat passed after formatting and the preview link adjustments. Browser provisioning, DCB integration, and image builds were absent from the task graph. |

The canonical and staged feasibility report SHA-256 was `73ca0b1b445ebb625d6c5d3679b75fe77500a702ab7cf356cecd90ff96c76bb3`. The docs and web lockfile SHA-256 values stayed `5739aa141cfad536f9c3b6d85d1e2886bb730a7537223779d0c2a36db67a84e8` and `265a68b1127838d40126679373f6b2004a97e6e8c6284234d4faa98215689b12`.

## TDD Gate Compliance

- RED at `5a20959` ran `publication rejects a broken prefixed report fragment` with managed Node and the TAP reporter. The test changed the maintainer guide link in an isolated fixture and Eleventy returned 0 instead of 1. The target assertion observed the successful render of the broken fragment, and GSD returned `RED_EVIDENCE_OK`.
- GREEN at `9a081b7` used the same fixture and required the `Missing fragment` diagnostic. The complete managed test suite passed through Gradle.

## Task Commits

1. `78ce1aa` renders the exact canonical report and connects docs to the root Gradle build.
2. `5351c52` publishes the quick start, maintainer guide, accessible layout, and Phase 7 handoff.
3. `5a20959` records the failing publication test. `9a081b7` adds the publication verifier, positive and negative checks, and a loopback preview.

## Decisions Made

- The only preauthorized HTTP destination is the loopback Vite origin. Hosted launch paths require HTTPS and an exact entry in `docsTrustedAppOrigins`. Invalid launch or deployment settings fail the build.
- Historical source links in the report point to immutable repository revisions. The linked paths and Markdown anchor headings were checked in local Git. Planning artifacts stay outside the generated site.
- The docs typography uses the approved Geist family names and their system font fallbacks.

## Deviations from Plan

**[Rule 1 - Bug] Enforce the loopback boundary and keep configuration-specific preview addresses as text.** During Task 3, the bundled Eleventy development server ignored its supplied host option and listened on a wildcard socket. A served-link check also caught absolute preview example links leading to a different deployment base. Commit `9a081b7` adds a dependency-free Node preview with an explicit loopback bind and displays the example URLs as code. HTTP checks in both modes verified the listener and every served internal destination.

## Outstanding Evidence

- Plan 02-08 owns the complete dependency maintenance procedure, tool diagnostics, and reconciliation for DOC-06 and FND-02. Private advisory coverage remains incomplete.
- Plans 02-06 and 02-11 own shared UI, Storybook and Steiger evidence for UI-01. The complete browser contract remains pending for CQRS-04. Plan 02-09 owns the combined BFF, browser and docs smoke.
- The hosted AMD64 DCB runtime and the probe retirement gate remain scheduled for Phase 7.

## Self-Check: PASSED
