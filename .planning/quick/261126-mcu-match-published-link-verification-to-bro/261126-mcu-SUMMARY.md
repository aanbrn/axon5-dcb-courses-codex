---
phase: quick-261126-mcu
plan: "01"
subsystem: documentation
tags: [eleventy, htmlparser2, publication]
requires:
  - phase: 02-build-and-ui-foundations
    provides: Allowlisted Eleventy publication and local preview
provides:
  - Active-document fragment and base validation
  - Exact request-path matching for published destinations
  - Two-base regression coverage for publication and output inventory
affects: [docs-site, maintainer-guide]
actuals:
  tokens: 1699
  tasks: 2
  commits: 7
commits: 7
plan_head_before: 2144dac91b5983f7b19e8a91d4c67c12f1463e58
plan_head_after: c96780221b9fa19af5987c68927ebdced67a9351
tech-stack:
  added: []
  patterns: [active-document parsing, exact published request-path matching]
key-files:
  modified:
    - docs-site/verify-site.mjs
    - docs-site/test/site.test.mjs
    - docs/maintainer-guide.md
key-decisions:
  - Match the URL pathname verbatim against the public inventory and directory aliases to align validation with the preview.
requirements-completed: [FND-06, DOC-06]
duration: 9m28s
completed: "2026-11-26"
status: complete
---

# Match published link verification to browser navigation

At `/` and `/courses/`, Eleventy rejects an active `<base href>`, a link to a fragment found only in template content, and a link to a pathname the local preview cannot serve. The Maintainer guide explains how to write document-relative paths and active fragment targets.

## RED and GREEN evidence

- Task 1 RED. At each base, `active base override`, `active base override with an empty href`, and `fragment matching only a nested template ID` each expected Eleventy exit 1 and received 0. Gradle and the managed Node TAP run each reported 28 passing tests and six failures. All six target assertions returned `RED_EVIDENCE_OK`. Task 1 GREEN and the tracer rerun each passed all 34 tests. The valid fixture links to the template element's own ID and a live sibling after the nested template, and contains inert links and base markup.
- Task 2 RED. At each base, `path with an uppercase encoded slash`, `path with a lowercase encoded slash`, and `path with an encoded letter` each expected Eleventy exit 1 and received 0. Gradle and the managed Node TAP run each reported 34 passing tests and six failures. All six target assertions returned `RED_EVIDENCE_OK`. Both RED runs failed on the fixture process exit assertion after rendering, with no setup or collection failures.
- Task 2 GREEN. `mise exec java -- ./gradlew --console=plain :docs-site:docsCheck` passed 40 tests at the default base. The same command with `-PdocsBase=/courses/` passed 40 tests. Each run builds distinct Eleventy variants at both bases. The passing fixtures cover the directory route, its `index.html` alias, an encoded slash in a query and fragment, a percent-encoded UTF-8 fragment, and legacy anchors. Each valid variant checks its sorted regular-file inventory against nine fixed expected names. The publication gate checks file contents, and the suite exercises canonical report bytes, launch policy, and exclusion of private filenames and bytes.

## Publication diagnostics

Separate Eleventy builds of copies of the staged Markdown reproduced every GREEN diagnostic below. Each failed with exit 1, and each base produced a valid nine-file build with nonempty outputs.

| Fixture                 | Diagnostic                                                                                                                   |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Active base             | `Active base href in quick-start/index.html: "../feasibility/phase-01/"`                                                     |
| Empty active base       | `Active base href in quick-start/index.html: ""` at `/` and `Active base href in quick-start/index.html: "."` at `/courses/` |
| Template-only ID        | `Missing fragment in quick-start/index.html: #template-only`                                                                 |
| Uppercase encoded slash | `Missing destination in quick-start/index.html: ../feasibility%2Fphase-01/`                                                  |
| Lowercase encoded slash | `Missing destination in quick-start/index.html: ../feasibility%2fphase-01/`                                                  |
| Encoded letter          | `Missing destination in quick-start/index.html: ../feasibility/%70hase-01/`                                                  |

Eleventy's HTML base transform renders the empty authored `href` as `.` at the prefixed base, so the fixture checks that rendered value there.

## Local preview and browser evidence

- Direct loopback HTTP requests to the standard `serve.mjs` preview verified both deployment bases. The canonical feasibility directory, its exact `index.html` alias, and the directory URL with `?view=events%2Ftags` returned 200. The exact request paths containing `%2F`, `%2f`, or `%70` returned 404.
- The Phase 02 review supplied the Chromium observations. At both bases Chromium applied the authored base override before following the guide link, found the template element's descendants only in its document fragment, and preserved the encoded slash in the HTTP request. This quick task ran local build and direct HTTP checks. Hosted evidence is pending. [Phase 02 review](../../phases/02-build-and-ui-foundations/02-REVIEW.md)

## Task commits

1. `d9fb338999eacecba3ba90376f05f221b3cfd24c` added the active-document RED fixtures.
2. `8715e4a4e4f9791f7e6c24bb6282947c23f73630` implemented active-document indexing and the passing template controls.
3. `22c389f8c65e04650d3f14c1812e49fd07bb0973` added the encoded-alias RED fixtures.
4. `c96780221b9fa19af5987c68927ebdced67a9351` matched the preview's exact pathname lookup, added the positive route and inventory controls, and documented the authoring rules.

The checked-in pre-commit hook passed on all four commits. The measured Git range also includes three parallel app commits. The token estimate uses the diff of the three source paths in this plan.

## Implementation refinement

Task 2 uses verbatim pathname lookup against the current published routes. The same check covers encoded slash and encoded letter aliases because the preview looks up the request path verbatim. Fragment decoding still resolves encoded IDs in the active document.

## Self-Check: PASSED
