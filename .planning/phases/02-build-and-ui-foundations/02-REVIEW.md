---
phase: 02-build-and-ui-foundations
reviewed: 2026-11-26T09:07:28Z
depth: standard
base_revision: 9bac74230360be3e04cef0192eba4e7df02e2017
reviewed_revision: cca11b1248b4f1c6b64aab557c98afa1173fc46b
files_reviewed: 17
files_reviewed_list:
  - bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt
  - bff/src/main/kotlin/courses/bff/BffApplication.kt
  - bff/src/main/resources/static/openapi.json
  - bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt
  - docs-site/eleventy.config.mjs
  - docs-site/package.json
  - docs-site/test/site.test.mjs
  - docs-site/verify-site.mjs
  - docs/maintainer-guide.md
  - tools/qodana-scan.sh
  - web/build.gradle.kts
  - web/src/app/main.tsx
  - web/test/client-graph.py
  - web/test/generated-client.test.ts
  - web/test/role-states.test.tsx
  - web/test/site-smoke.mjs
  - web/vite.config.ts
findings:
  critical: 1
  warning: 3
  info: 0
  total: 4
  necessity: 0
status: issues_found
---

# Phase 02 Code Review Report

- **Reviewed** 2026-11-26T09:07:28Z
- **Depth** standard
- **Files reviewed** 17
- **Status** issues_found

## Summary

The final Phase 02 source review covers `9bac742..cca11b1` on `gsd/phase-02-build-and-ui-foundations`. The 17-file scope excludes planning artifacts and the generated docs lockfile. The lockfile diff was checked for dependency provenance. It only adds the direct manifest entry for the already pinned parser. `git diff --check` and the Qodana launcher shell syntax check passed.

The effective documentation URL can change while Gradle reuses the old web bundle and skips Vite startup validation. Three independent browser controls also exposed inherited publication gaps in URL resolution and fragment indexing. The two Gradle controls ran against disposable archives of the reviewed revision. The documentation controls built disposable variants from the current staged sources and ran Chromium against the repository's preview server at both deployment bases. All three documentation controls passed the Eleventy gate before reproducing the respective navigation problem.

The orchestrator separately passed the CI-like build and the prior-phase native runtime regression at the reviewed source revision. The earlier targeted runs provide the role contract, live shell, landmark and Qodana evidence below.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-05: Gradle skips documentation URL validation after a dotenv substitution changes

**Severity:** BLOCKER

**File:** `web/build.gradle.kts:113-126` and `web/vite.config.ts:23-32`

**Issue:** Vite expands `VITE_DOCS_BASE` from mode-specific dotenv files using inherited environment values. Gradle fingerprints the four production env files and the raw process override. With no direct override, changes to a variable referenced inside the file are invisible to the task. In a disposable archive, `VITE_DOCS_BASE=https://docs.example.test/${DOCS_PREFIX}/` produced `/first/`. Changing only `DOCS_PREFIX` to `second` made `:web:webBuild` report `UP-TO-DATE` and retain `/first/`. The managed direct Vite build produced `/second/`. A second control used `VITE_DOCS_BASE=https://docs.example.test:${DOCS_PORT}/courses/` and changed the port from `443` to `bad`. Gradle again reported `UP-TO-DATE` and succeeded. Direct Vite rejected the input with the expected `VITE_DOCS_BASE` diagnostic. The missing input dependency predates this delta. It now bypasses the new build-time validation guarantee for the effective URL.

**Fix:** Fingerprint the effective production documentation value before Gradle's up-to-date check, using the same Vite env resolution as the build, or run the task whenever dotenv expansion can depend on the inherited environment. Extend `verifyClientGraph` with both variable-only transitions. Keep the literal process override and absent-versus-empty behavior.

## Warnings

### WR-05: The publication gate resolves relative URLs against the wrong base

**Severity:** WARNING

**File:** `docs-site/verify-site.mjs:18-28` and `docs-site/verify-site.mjs:69-80`

**Issue:** On pages with an authored `<base href>`, the parser adds its value to the regular link list and uses the deployment page URL for every link. Chromium uses the document's base element. In a staged Quick start variant, `<base href="../feasibility/phase-01/">` followed by `<a href="../maintainer-guide/">Guide</a>` passed Eleventy at `/` and `/courses/`. Chromium resolved that link to `/feasibility/maintainer-guide/` and `/courses/feasibility/maintainer-guide/` respectively, both HTTP 404 in the standard preview. The checked-in pages use the deployment URL as their base. The faulty resolution was already present before the parser change.

**Fix:** Reject authored `<base href>` in published pages so the configured deployment URL controls resolution. Add the failing control at both deployment bases.

### WR-06: Inert template content can satisfy a fragment check

**Severity:** WARNING

**File:** `docs-site/verify-site.mjs:18-28` and `docs-site/verify-site.mjs:81-84`

**Issue:** Every parsed element contributes IDs and legacy anchor names regardless of whether it is in the active document. A hosted fragment can therefore pass validation when its only match is inside an inert `<template>`. Eleventy accepted a maintainer guide with `<template><span id="only-in-template">Fixture</span></template>` and a link to `#only-in-template` at both deployment bases. Chromium found the ID in the template's document fragment and found no target in the navigated document. The previous verifier also treated that element as a fragment target.

**Fix:** Exclude template descendants from the active document's fragment index. Add a rejection test with a template-only ID at both bases and retain the existing positive ID and named-anchor checks.

### WR-07: The verifier accepts encoded paths that the preview cannot serve

**Severity:** WARNING

**File:** `docs-site/verify-site.mjs:73-80` and `docs-site/serve.mjs:28-35`

**Issue:** The verifier decodes the full path before looking up an allowlisted file. The documented preview looks up the URL path verbatim. In a staged maintainer guide, the relative path `../feasibility%2Fphase-01/` passed verifier checks at both deployment bases because the decoded path matched the allowlist. Chromium preserved `%2F` in the request and received HTTP 404 from the documented preview at both bases. This route mismatch predates the parser change.

**Fix:** Compare internal paths to the exact request routes derived from the approved output files, including their `index.html` aliases. Keep percent decoding for fragment identifiers. Add the encoded slash control at both bases.

## Prior review dispositions

<a id="cr-04-historical-qodana-scans-silently-use-the-editor-profile-and-can-contaminate-later-scans"></a>

The Phase 02 disposition ledger retains CR-01 through CR-04 and the original Phase 02 WR-01 through WR-04. The four slice findings below come from a separate review and use their original numbers with a source prefix. [Phase 02 disposition ledger](02-REVIEW-DISPOSITION.md) · [Application slice review](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md)

| Finding | Disposition at `cca11b1` | Evidence |
| --- | --- | --- |
| Phase 02 CR-04 | Fixed | The launcher excludes the editor profile when creating archives of historical revisions and uses a fresh analysis namespace. The retained historical, delivery and historical-repeat sequence recovered all 51 reference Gradle diagnostics in the same analysis cache. The first historical scan had one additional Gradle diagnostic. The workspace profile and existing Gradle and plugin cache directories were preserved. [Historical scan verification](../../quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-VERIFICATION.md) |
| Slice WR-01 | Partially fixed | Vite rejects invalid resolved values whenever it runs. The original malformed port and explicit empty override are covered, as are the default, literal process override and prefixed URL. CR-05 covers the remaining Gradle skip when a dotenv substitution changes. [Shell validation evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Slice WR-02 | Fixed | OpenAPI and Kotlin use the same whitespace character set, with independent NetworkNT and generated Zod checks. The directory documents and enforces exact case-sensitive ID uniqueness on both sides. The immutable student snapshot prevents callers from bypassing the invariant after validation. Chromium exercises invalid directory responses and recovery. [Role directory evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Slice WR-03 | Fixed | The 26 regions across the current articles have distinct, contextual names within each article. Chromium found them by exact accessible name and checked tab order, visible focus and arrow-key scrolling on overflowing regions. [Landmark evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |
| Slice WR-04 | Fixed for the reported attribute syntax | Both deployment bases now reject the original raw anchor with spaced equals, an unquoted image source, and broken Markdown destinations. WR-05 through WR-07 record other browser and preview mismatches in the publication gate. [Publication evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |

_Reviewed by gsd-code-reviewer at standard depth._
