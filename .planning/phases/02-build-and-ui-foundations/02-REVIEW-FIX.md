---
phase: 02-build-and-ui-foundations
fixed_at: 2026-11-25T16:53:17Z
review_path: .planning/phases/02-build-and-ui-foundations/02-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 02 Code Review Fix Report

All three critical findings and four warnings have individual commits and behavioral coverage. The independent follow-up reviewed all seven fixes at `0898e19`. The local Chromium run completed the timeout and recovery check that the review sandbox could only inspect in source.

## Fixed Issues

### CR-01: Worktree reconciliation can erase an editor save

**Files modified:** `tools/style/run.py`, `tools/style/test_hook.py`, `docs/maintainer-guide.md`
**Commit:** `aa98ba2`
**Status:** fixed and independently reproduced
**Applied fix:** Publish formatted content to the index and leave working files untouched. The guide explains how to inspect the remaining unstaged diff and selectively apply the committed formatting. A real commit verified that an editor save at index publication survives byte-for-byte. Test-only follow-up `b261211` corrected the existing tracked Prettier assertion for the preserved working bytes.

### CR-02: A path-limited commit leaves an unformatted change staged after success

**Files modified:** `tools/style/run.py`, `tools/style/test_hook.py`
**Commit:** `0f2a5e8`
**Status:** fixed and independently reproduced
**Applied fix:** Recognize Git's temporary path-limited index by its directory and owning process. When changes require formatting, abort before index publication and explain how to stage and commit the selection. Real Git commits verified refusal with both persistent index types, success with an already formatted path, and formatting in ordinary commits using the explicit alternate index.

### CR-03: Staged shell formatting changes literal output

**Files modified:** `tools/style/run.py`, `tools/style/policy.json`, `tools/style/test_hook.py`
**Commit:** `c69d252`
**Applied fix:** Preserve shell bytes through the staged and tracked paths and keep `sh -n` checks. The original and committed scripts emitted identical trailing spaces and tabs from a here-document and a multiline string. Both checks rejected invalid syntax.

### WR-01: A stalled directory response keeps retry unavailable

**Files modified:** `web/src/pages/home/model/useDemoRoles.ts`, `web/test/role-states.test.tsx`, `web/test/role-tracer.mjs`
**Commit:** `ff786c2`
**Status:** fixed and verified in Chromium
**Applied fix:** Give each directory request a five-second deadline that covers response-body consumption. Clear the timer when the request settles or its component unmounts. Chromium verified cancellation of partial HTTP 200 bodies on initial load and on retry, an enabled retry after each timeout, and restoration of the saved role after recovery.

### WR-02: The documented prefixed preview leaves the app pointing at the root

**Files modified:** `docs/maintainer-guide.md`
**Commit:** `cc47608`
**Applied fix:** Document the paired BFF, Vite and `/courses/` docs preview commands. Document `VITE_DOCS_BASE` for hosted web builds. Site checks covered the prefixed documentation, its launch links and the reverse journey through the app.

### WR-03: Bootstrap doctor accepts a missing or malformed Node version pin

**Files modified:** `tools/doctor.py`
**Commit:** `787c1ed`
**Applied fix:** Report `.nvmrc` as an independent required input in both modes. Missing and malformed pins exit nonzero with a repair naming the file. Managed observations remain deferred during bootstrap.

### WR-04: Gradle's comment check breaks on a path containing a comma

**Files modified:** `build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts`, `tools/check_kotlin_quality.py`
**Commit:** `a1bd895`
**Applied fix:** Analyze copies of the declared sources from a temporary directory and map detekt diagnostics to the original paths. The Gradle regression accepted a valid `Kdoc,CommentsWitness.kt` and reported its original filename with `EndOfSentenceFormat` after the deliberate comment error. The negative ktfmt control uses the original deliberately unwrapped Phase 01 specimen after the shared style policy assigned it a plain-text check.

## Verification

The Gradle, browser and doctor gates ran in the main phase checkout. The Git hook and Kotlin quality regression tests use disposable repositories or source copies.

- `python3 tools/style/test_hook.py` passed all 14 real Git hook tests.
- The full-tree style tests passed the detekt and FSD controls. The tracked Prettier policy control passed on a targeted rerun after the test-only correction.
- `./gradlew --offline --console=plain styleCheck :bff:detektComments :fixtures:detektComments` passed.
- `./gradlew --offline --console=plain :web:webCheck` passed all 19 adapter tests and the type and FSD checks.
- `./gradlew --offline --console=plain :web:shellSmoke :docs-site:check :web:siteSmoke` passed 18 Chromium role checks, 14 documentation assertions and the live site journey.
- Gradle doctor, bootstrap doctor and all six doctor self-tests passed their required checks. The running Docker daemon and architecture remained unavailable to the optional checks.
- `python3 tools/check_kotlin_quality.py format-comments` passed the ktfmt and detekt controls in a disposable checkout.
