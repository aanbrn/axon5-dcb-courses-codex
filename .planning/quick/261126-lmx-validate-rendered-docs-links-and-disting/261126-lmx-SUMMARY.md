---
phase: quick-261126-lmx
plan: "01"
subsystem: documentation
tags: [eleventy, htmlparser2, accessibility, playwright]
requires:
  - phase: 02-build-and-ui-foundations
    provides: Allowlisted Eleventy publication and live shell browser smoke
provides:
  - Rendered link and fragment validation at both deployment bases
  - Distinct accessible names for article tables and code samples
  - Keyboard focus and horizontal-scroll evidence for published articles
affects: [docs-site, web-site-smoke]
actuals:
  tokens: 5585
  tasks: 2
  commits: 5
commits: 5
plan_head_before: 9bac74230360be3e04cef0192eba4e7df02e2017
plan_head_after: a702e28515011b1124fc9c17d34c1aa5dd35a1bb
tech-stack:
  added: [htmlparser2 7.2.0 as an explicit docs-site development dependency]
  patterns:
    [
      parse rendered HTML once per page,
      index fragment targets before resolving links,
    ]
key-files:
  modified:
    - docs-site/package.json
    - docs-site/package-lock.json
    - docs-site/verify-site.mjs
    - docs-site/eleventy.config.mjs
    - docs-site/test/site.test.mjs
    - web/test/site-smoke.mjs
key-decisions:
  - Declare the existing lock resolution of htmlparser2 directly in docs-site so the verifier can import it after a clean npm install.
  - Name each region with its type and section, then use a concise step or caption, an ordinal, or an existing heading ID where needed.
requirements-completed: [FND-06, DOC-06]
duration: 9m
completed: "2026-11-26"
status: complete
---

# Validate rendered documentation links and distinguish article landmarks

Both deployment bases reject broken published destinations and fragments. All 26 code and table regions across Quick start, the feasibility report, and the Maintainer guide have distinct names within their articles.

## Publication

The verifier reads element attributes through the HTML parser and indexes element IDs and legacy named anchors before resolving links. It continues to check the nine approved output files, canonical report bytes, launch policy, and synthetic private filename and byte controls. Managed Node 26.13.1 and npm 12.2.3 regenerated the lock. The only lock change was the root direct dependency entry, preserving the prior parser resolution and integrity. A fresh Gradle-managed npm install with scripts disabled passed.

The root RED test expected exit 1 for a missing raw anchor destination written with whitespace around the equals sign. Eleventy returned 0. The broken unquoted image source also returned 0 at the root. The prefixed build already rejected both. The GREEN matrix gives each raw anchor, raw image, Markdown link, missing fragment and non-anchor name an independent build at both bases. Positive fixtures at both bases exercise a decoded element ID, a legacy anchor name, and tag-shaped text in a comment and escaped code. GSD verified the target RED against the Node TAP report.

## Article landmarks

The article RED test found that the first three Quick start samples were all named `Code sample — Start the shell`. GSD verified the failure against the Node TAP report. The rendered names now identify the BFF, web app, and documentation commands individually. The feasibility report uses `Code sample — Reproduce the proof (1)` and `Code sample — Reproduce the proof (2)`. The Maintainer guide numbers its four Setup and diagnostics samples. A fixture exercises repeated headings and captioned and uncaptioned tables at both publication bases, with escaped inline text and the existing heading IDs.

## Verification

- `mise exec java -- ./gradlew --console=plain :docs-site:docsCheck` passed all 26 tests for the first task and passed again at the tracer gate.
- `mise exec java -- ./gradlew --console=plain :docs-site:docsCheck :web:siteSmoke` passed all 28 docs tests and the full live browser workflow. Chromium 159.0.8154.6 found the expected landmarks by exact accessible name, reached all 26 in document order with Tab, verified visible focus, and moved overflowing regions with ArrowRight at 320px and 200% text. The skip link reached the main landmark, and each page fit the viewport after scrolling. The combined run used the shared phase checkout while the shell task was in progress.
- The checked-in pre-commit hook passed for all four task commits.

## Task commits

1. `0497a657606f3d614a55cdda84cabdba0995e6f2` added the rendered link and fragment regressions.
2. `69dfa2bd191d320e7cad44c7bb07a65df05eb9af` indexed rendered links and fragments with the pinned parser.
3. `86ec0fc011bd98abf18115d366c8b5c534c6c62d` reproduced duplicated landmark names in rendered articles.
4. `a702e28515011b1124fc9c17d34c1aa5dd35a1bb` implemented contextual names and verified keyboard interaction in Chromium.

The measured Git range contains these four commits and the interleaved Qodana commit `3df371b`. The token estimate uses the diff of the six docs task paths.

## Deviations from plan

None.

## Self-Check: PASSED
