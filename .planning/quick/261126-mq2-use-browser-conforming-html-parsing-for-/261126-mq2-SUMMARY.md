---
phase: quick-261126-mq2
plan: "01"
subsystem: documentation
tags: [eleventy, parse5, publication]
requires:
  - phase: 02-build-and-ui-foundations
    provides: Allowlisted Eleventy publication and local preview
provides:
  - Browser-conforming document tree for published link and fragment validation
  - Two-base regression coverage for literal textarea markup and SVG targets
affects: [docs-site]
actuals:
  tokens: 2031
  tasks: 1
  commits: 2
commits: 2
plan_head_before: 381bcac24e213373260a09e224ed5dbf951232ac
plan_head_after: 1ca7bf947420172fcfb24b52e85b227d89de8410
tech-stack:
  added: [parse5@8.1.1]
  patterns: [HTML document tree traversal]
key-files:
  modified:
    - docs-site/package.json
    - docs-site/package-lock.json
    - docs-site/verify-site.mjs
    - docs-site/test/site.test.mjs
key-decisions:
  - Use the default parse5 document tree and scripting setting for the rendered pages.
  - Collect live IDs across namespaces and restrict legacy anchor names and base overrides to HTML elements.
requirements-completed: [FND-06, DOC-06]
duration: 6m14s
completed: "2026-11-26"
status: complete
---

# Use browser-conforming HTML parsing for publication checks

At `/` and `/courses/`, Quick start publishes literal markup in a textarea. Eleventy rejects live links to IDs found only in that text and retains the active HTML base guard, including an empty `href`.

## Implementation

- The verifier parses each rendered page once and visits its child nodes in document order. It checks unqualified `href` and `src` values, indexes live IDs in HTML and SVG, and keeps the template element itself in the index. The template content lives in a separate fragment.
- The article region tests read the rendered document tree and check immediate `pre` and `code` relationships, wrapper role and keyboard focus, and the order and uniqueness of contextual names.

## RED and GREEN evidence

- **RED.** `mise exec java -- ./gradlew --console=plain :docs-site:docsCheck` reported 38 passes and six failures. At each base the combined textarea fixture expected exit 0 and received exit 1 with `Active base href in quick-start/index.html`. The textarea-only fragment and SVG anchor-name controls expected exit 1 and received exit 0. The managed Node TAP rerun reproduced the six assertion failures without setup or collection errors. Each target returned `RED_EVIDENCE_OK`.
- **GREEN.** After the forced managed install, `mise exec java -- ./gradlew --console=plain :docs-site:docsCheck` passed all 44 tests. The same command with `-PdocsBase=/courses/` passed all 44 tests. The post-commit tracer run passed all 44 tests again. At both bases the passing variants check the exact nine public files and exercise live SVG and HTML targets. The rejection fixtures check `Missing fragment in quick-start/index.html: #textarea-only` and the corresponding SVG name diagnostic. The active base, empty base, template, destination, and accessibility controls all passed.

## Parser provenance and managed install

- Managed Node `26.13.1` and npm `12.2.3` generated the docs lock and confirmed the registry entry for exact `parse5@8.1.1`, its official repository, and its `entities@^9.0.0` dependency. The lock records `entities@9.0.0` and the matching parser integrity `sha512-EcR/6WDcU7b2N3vQSxKALCk9lXGtUMQxXio008OEMBE0kavu/7JLfBEeFPzi43nMqVDSbEn3QCK+BMCc9zO//w==`. [npm registry metadata](https://registry.npmjs.org/parse5/8.1.1) · [parse5 repository](https://github.com/inikulin/parse5)
- `mise exec java -- ./gradlew --console=plain :docs-site:npmInstall --rerun` installed 117 packages through the configured `npm ci --ignore-scripts --no-audit --no-fund` and passed the lock-byte check. Managed `npm ls` confirmed `parse5@8.1.1` as the sole direct HTML parser and `htmlparser2@7.2.0` under Eleventy `3.1.8` through PostHTML. Every pre-existing indirect lock entry retained its resolution.

## Chromium evidence

The Phase 02 review recorded the original differential result. The `cca11b1` verifier built the literal base fixture at both bases, the `c967802` verifier rejected it, and Chromium saw the exact textarea text and zero base elements. [Phase 02 review](../../phases/02-build-and-ui-foundations/02-REVIEW.md)

Fresh checks used Playwright with Chromium `159.0.8154.6` and the standard `serve.mjs` preview on disposable Eleventy output. Both `/quick-start/` and `/courses/quick-start/` returned HTTP 200. At both routes the textarea value was exactly `<base href="../feasibility/phase-01/"><span id="textarea-only">example</span>`, the document had zero base elements, and `document.getElementById("textarea-only")` returned `null`.

## Task commits

1. `ce147d476ed28c626a4c7d98d560489b2861296f` added the publication regression fixtures.
2. `1ca7bf947420172fcfb24b52e85b227d89de8410` switched the verifier and test helper to parse5.

The project pre-commit hook passed on both commits.

## Self-Check: PASSED
