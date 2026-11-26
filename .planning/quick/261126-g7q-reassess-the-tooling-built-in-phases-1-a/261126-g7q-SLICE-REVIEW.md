---
phase: 02-build-and-ui-foundations
reviewed: 2026-11-26T04:50:59Z
depth: deep
files_reviewed: 31
files_reviewed_list:
  - bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt
  - bff/src/main/kotlin/courses/bff/BffApplication.kt
  - bff/src/main/resources/static/openapi.json
  - bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt
  - docs-site/eleventy.config.mjs
  - docs-site/serve.mjs
  - docs-site/src/_includes/page.11ty.js
  - docs-site/src/feasibility/phase-01.11tydata.json
  - docs-site/src/index.11ty.js
  - docs-site/src/site.css
  - docs-site/verify-site.mjs
  - web/src/app/main.tsx
  - web/src/app/theme.css
  - web/src/pages/home/HomePage.stories.tsx
  - web/src/pages/home/index.ts
  - web/src/pages/home/model/useDemoRoles.ts
  - web/src/pages/home/ui/HomePage.tsx
  - web/src/shared/api/demoRoles.ts
  - web/src/shared/api/index.ts
  - web/src/shared/lib/utils.ts
  - web/src/shared/ui/Controls.stories.tsx
  - web/src/shared/ui/alert.tsx
  - web/src/shared/ui/button.tsx
  - web/src/shared/ui/index.ts
  - web/src/shared/ui/native-select.tsx
  - web/test/client-graph.py
  - web/test/foundation-proof.mjs
  - web/test/generated-client.test.ts
  - web/test/role-states.test.tsx
  - web/test/role-tracer.mjs
  - web/test/site-smoke.mjs
findings:
  critical: 0
  warning: 4
  info: 0
  total: 4
  necessity: 0
status: issues_found
---

# Phase 02 Application Slice Code Review

**Revision:** `393ae8c73e60585fed8611f1c3a5bf833fedef01`

## Summary

Traced the Spring HTTP route and served OpenAPI document through client generation, generated Fetch and Zod validation, the React request lifecycle and the native role selector. Traced the allowlisted Markdown and assets through Eleventy, publication verification and the loopback preview. Reviewed component, client, Storybook and browser test assertions and used build wiring, the canonical articles and the existing phase records as context.

The documented local journey works with the live BFF. Recent review corrections cover the five-second response-body deadline, stale request cancellation and the paired prefixed docs settings. The BFF serves a fixed public read model with no privileged operation. The selected demo role is an opaque value in tab-local browser storage and confers no server-side identity. Enrollment, access to protected actions and hosted deployment have their own later-phase scope.

The rerun passed all 19 generated-client checks, 14 documentation checks, 18 Chromium shell checks and the live app/docs journey. The Chromium suites exercised same-context tab isolation, timeout cancellation during initial load and retry, focus restoration and the production response. The recorded maintainer observations provide the native selector and assistive technology evidence. The current review used separate inputs for the four findings below and did not repeat the manual assistive technology checks or hosted delivery.

## Narrative Findings (AI reviewer)

## Warnings

### WR-01: An invalid documentation base can prevent the entire app from mounting

**Severity:** WARNING

**File:** `web/src/app/main.tsx:6-16`

**Issue:** The documented deployment setting enters the production bundle without validation. The module constructs the URL before initializing React. A fresh Vite build with `VITE_DOCS_BASE=https://docs.example.test:wrong/courses/` succeeded. In Chromium the built HTML responded with HTTP 200, the page reported `Failed to construct 'URL': Invalid URL`, and `#root` had zero children. A typo in a documentation setting therefore takes down the role selector and the shell along with the links. The documented valid root and prefixed URLs passed the browser journey.

**Fix:** Validate the resolved documentation base in the Vite configuration for dev and production builds. Report an invalid configured value as a build or startup error that names `VITE_DOCS_BASE`. Preserve the default local URL and supported configured paths. Cover a malformed absolute URL and a valid prefixed URL with focused build checks.

### WR-02: The published directory contract admits blank options and omits its ID uniqueness rule

**Severity:** WARNING

**File:** `bff/src/main/resources/static/openapi.json:29-59`

**Issue:** Both role schemas use `minLength: 1`, which admits whitespace-only labels and IDs. The generated adapter accepted a student label containing only spaces and a tab. Chromium rendered that payload as an enabled student option with an empty displayed name and raised no directory alert. The adapter separately rejects duplicate IDs across the entire directory at `web/src/shared/api/demoRoles.ts:17-24`, but the published schema and response description omit that rule. Two student objects with distinct labels and a shared ID meet the published schema and are rejected by the generated client adapter. The shipped fixed directory has visible names and distinct IDs. The defect affects the promised contract-first extension path and malformed-response handling.

**Fix:** Encode a non-whitespace constraint for the string fields in OpenAPI and verify that both generated Zod and the independent HTTP validator enforce it. Document ID uniqueness across Administrator and students as a directory invariant, enforce it on the server and retain the client check. Cover whitespace and duplicate IDs in contract and browser checks.

### WR-03: Published command samples share indistinguishable landmark names

**Severity:** WARNING

**File:** `docs-site/eleventy.config.mjs:64-94`

**Issue:** Each scroll region uses only its kind and the preceding heading for its accessible name. A fresh prefixed Eleventy build produced three regions named `Code sample — Start the shell`, four named `Code sample — Setup and diagnostics` and two named `Code sample — Reproduce the proof`. These regions contain different instructions. A reader using a landmark list cannot tell which entry opens the desired command block. The live smoke check at `web/test/site-smoke.mjs:250-255` picks the first match in the report and misses the ambiguity. [W3C APG landmark design guidance](https://www.w3.org/WAI/ARIA/apg/practices/landmark-regions/#general-principles-of-landmark-design)

**Fix:** Give each region a distinct, contextual label. Add visible captions or use per-section sample numbering for sections with multiple blocks. Preserve keyboard scrolling and assert unique region names across every rendered article.

### WR-04: The root publication check misses valid HTML links

**Severity:** WARNING

**File:** `docs-site/verify-site.mjs:18-24`

**Issue:** The regex requires an attribute name immediately followed by `=` and a quoted value. The root site build leaves valid inline HTML in Markdown as authored. Appending `<a href = "/no-such-docs-page/">Missing article</a>` to a disposable copy of the staged quick start produced an active link to a missing destination and passed the root build. The same test failed under `/courses/` because Eleventy serialized the attribute as `href="..."`. The gate can therefore pass or fail the same broken link depending on the deployment prefix.

**Fix:** Inspect the rendered document with an HTML parser and use its normalized attributes for destination and fragment validation. Exercise a broken link in valid raw HTML and the existing broken Markdown link under both deployment bases.
