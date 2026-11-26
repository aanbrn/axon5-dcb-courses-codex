---
phase: 02-build-and-ui-foundations
reviewed: 2026-11-25T16:37:30Z
depth: standard
files_reviewed: 77
files_reviewed_list:
  - .gitattributes
  - .githooks/pre-commit
  - .github/workflows/build.yml
  - .gitignore
  - .idea/inspectionProfiles/Project_Default.xml
  - .qodana/profiles/spring-beans.xml
  - bff/build.gradle.kts
  - bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt
  - bff/src/main/kotlin/courses/bff/BffApplication.kt
  - bff/src/main/resources/static/openapi.json
  - bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt
  - build-logic/build.gradle.kts
  - build-logic/settings.gradle.kts
  - build-logic/src/main/kotlin/courses.jvm.gradle.kts
  - build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts
  - build.gradle.kts
  - config/detekt/comments.yml
  - docs-site/build.gradle.kts
  - docs-site/eleventy.config.mjs
  - docs-site/package.json
  - docs-site/serve.mjs
  - docs-site/src/_includes/page.11ty.js
  - docs-site/src/feasibility/phase-01.11tydata.json
  - docs-site/src/index.11ty.js
  - docs-site/src/site.css
  - docs-site/test/site.test.mjs
  - docs-site/verify-site.mjs
  - docs/feasibility/phase-01.md
  - docs/maintainer-guide.md
  - docs/quick-start.md
  - fixtures/build.gradle.kts
  - fixtures/src/testFixtures/kotlin/courses/fixtures/DirectoryFixtures.kt
  - gradle/libs.versions.toml
  - mise.toml
  - qodana.yaml
  - settings.gradle.kts
  - tools/check_kotlin_quality.py
  - tools/check_pr_workflow.py
  - tools/doctor.py
  - tools/qodana-scan.sh
  - tools/style/package.json
  - tools/style/policy.json
  - tools/style/run.py
  - tools/style/test_hook.py
  - tools/test_phase2_build.py
  - tools/verify_dependency_evidence.py
  - web/.storybook/main.ts
  - web/.storybook/preview.ts
  - web/build.gradle.kts
  - web/components.json
  - web/index.html
  - web/orval.config.ts
  - web/package.json
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
  - web/steiger.config.ts
  - web/test/client-graph.py
  - web/test/foundation-proof.mjs
  - web/test/generated-client.test.ts
  - web/test/role-states.test.tsx
  - web/test/role-tracer.mjs
  - web/test/site-smoke.mjs
  - web/tsconfig.json
  - web/vite.config.ts
  - web/vitest.config.ts
findings:
  critical: 4
  warning: 4
  info: 0
  total: 8
  necessity: 0
status: issues_found
---

# Phase 02 Code Review Report

- **Reviewed:** 2026-11-25T16:37:30Z
- **Depth:** standard
- **Files reviewed:** 71
- **Status:** issues_found

## Summary

The review covers Phase 02's Gradle lifecycle, BFF contract and client generation, demo shell, documentation build and preview, staged formatter, tool ownership and pull request workflow at `d4ea692` against `44589a4`. The scope excludes planning artifacts, generated lockfiles and formatting-only changes to the Phase 1 probes and project instructions.

The installed hook can erase an editor save, diverge from the persistent index during a path-limited commit, and change a shell script's output when it trims significant spaces. The Git and formatter findings were reproduced in disposable directories. The review also identifies recovery and setup gaps in the demo shell, non-root docs preview, bootstrap doctor and Gradle comment check. Hosted CI, AMD64 DCB runtime and private advisory results have separate verification scopes. The role review covers the v1 demo selector.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Worktree reconciliation can erase an editor save

**Severity:** BLOCKER

**File:** `tools/style/run.py:568-592`

**Issue:** `reconcile_worktree` checks that the file still matches the earlier read and then replaces the path in a separate operation. An editor save between the final `read_version` and `replacement.replace` is overwritten. The index lock has already been released by the time reconciliation starts at `tools/style/run.py:619-625`, and Git index locks do not protect worktree writes. A deterministic check wrote new editor bytes immediately before the real replacement operation. Reconciliation returned success and the new bytes were lost, violating D-12.

**Fix:** Keep the hook's automatic write in the validated index. Leave each worktree path untouched and report how to reconcile the formatted index with local edits when the caller chooses. Verify that a worktree save during publication survives and that the commit still uses formatted bytes.

### CR-02: A path-limited commit leaves an unformatted change staged after success

**Severity:** BLOCKER

**File:** `tools/style/run.py:595-619`

**Issue:** `git commit -- example.txt` gives the hook a Git-owned `next-index-*.lock` for the commit contents. Git also prepares a separate index for the persistent staged state. The hook publishes only to the first index, and its worktree reconciliation runs against the resulting formatted bytes. With the actual opt-in hook in a disposable repository, `HEAD:example.txt` and the worktree contained `after\n`, while `:example.txt` contained `after   \n`. Git showed `MM example.txt` immediately after the successful commit. The next commit includes this staged diff unless it is corrected.

**Fix:** Detect Git's path-limited commit index before writing. If formatting is required in this mode, fail before publishing either index or changing worktree bytes and instruct the caller to stage the selection and perform an ordinary commit. Preserve the explicit alternate-index workflow and verify both paths with real commits.

### CR-03: Staged shell formatting changes literal output

**Severity:** BLOCKER

**File:** `tools/style/run.py:129-137`

**Issue:** The shell route applies `rstrip(" \t")` to every line via `tools/style/run.py:264-265`, including shell here-document and multiline string bodies. The `sh -n` check at `tools/style/run.py:288-289` passes after the change because the script remains syntactically valid. In a real disposable commit with the installed hook, a here-document line containing `column` followed by three spaces emitted `b'column   \n'` before staging and `b'column\n'` from the committed script.

**Fix:** Preserve horizontal whitespace on the shell route and keep the syntax check. If shell whitespace formatting is required, use a syntax-aware formatter that preserves literal data. Verify the committed script's output with a literal whitespace witness.

## Warnings

### WR-01: A stalled directory response keeps retry unavailable

**Severity:** WARNING

**File:** `web/src/pages/home/model/useDemoRoles.ts:38-72`

**Issue:** The controller aborts only during unmount. The adapter passes that signal directly to the generated Fetch call at `web/src/shared/api/demoRoles.ts:3-4`, and the generated client awaits the body. If a connected server or proxy stalls before completing the reply, neither `catch` nor `finally` runs. The selector stays disabled, and the retry control stays disabled if the stall occurs during recovery.

**Fix:** Add a per-request deadline that covers response consumption and cancels the fetch. Route a timed-out active request to the existing failed state and retain the unmount guard. Verify that a stalled initial load and stalled retry both recover to an enabled retry action.

### WR-02: The documented prefixed preview leaves the app pointing at the root

**Severity:** WARNING

**File:** `docs/maintainer-guide.md:74-83`

**Issue:** The published preview command mounts the docs at `/courses/`. With that command and the published app launch command, `web/src/app/main.tsx:6-10` still builds links from `http://127.0.0.1:8081/`, and `docs-site/serve.mjs:8-16` registers the pages only under `/courses/`. The app's Documentation, Quick start and feasibility report links therefore return 404. The browser smoke supplies `VITE_DOCS_BASE` explicitly at `web/test/site-smoke.mjs:310-318`, a step missing from the guide.

**Fix:** Document the paired app command `VITE_DOCS_BASE=http://127.0.0.1:8081/courses/ ./gradlew :web:dev` beside the prefixed preview command. Document the same build-time input for hosted web builds using a separate docs origin or prefix.

### WR-03: Bootstrap doctor accepts a missing or malformed Node version pin

**Severity:** WARNING

**File:** `tools/doctor.py:223-280`

**Issue:** `npm_checks` parses `.nvmrc` but marks managed Node as `DEFERRED` even when the pin is missing or invalid. The npm input checks can all pass independently of that pin. The report at `tools/doctor.py:530-550` can consequently declare bootstrap ready and exit successfully just before Gradle rejects the file at configuration time (`build.gradle.kts:31-40`). A check using the real package metadata with the `.nvmrc` read failed produced zero required Node-related failures.

**Fix:** Report a required `.nvmrc` input check independently of executable observations. Fail on a missing or malformed pin in both modes, with a repair that names the version file. Keep the managed executable observations deferred during bootstrap.

### WR-04: Gradle's comment check breaks on a path containing a comma

**Severity:** WARNING

**File:** `build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts:63-79`

**Issue:** The Gradle task passes a comma-delimited list of absolute paths to detekt. A comma in a source filename or in the checkout directory splits a legitimate path into invalid arguments. The managed CLI rejected an actual comma-bearing path with `ParameterException`, while the same witness under a plain path reached `EndOfSentenceFormat`. The repository-wide style driver already avoids this parser limitation at `tools/style/run.py:328-345`, so the ordinary build and `styleCheck` handle those paths differently.

**Fix:** Give the Gradle detekt invocation comma-free temporary paths for the declared inputs and map findings to original filenames, using the same path-handling approach as the repository style driver. Verify a clean Kotlin file and a comment-rule failure under a comma-bearing checkout or source path.

---

_Reviewed at 2026-11-25T16:37:30Z by gsd-code-reviewer at standard depth._

## Incremental Review After the Original Verification

- **Reviewed:** 2026-11-26T08:14:43Z
- **Depth:** standard
- **Range:** `393ae8c73e60585fed8611f1c3a5bf833fedef01..3779fa227d23e1503dc04d70a35e5839172eff72` on `gsd/phase-02-build-and-ui-foundations`
- **Status:** `issues_found` with one new blocker

GSD returned `degraded` with `source: phase-range` and `reason: no-task-commit-rows` for `check evaluation-scope --phase 02 --since 393ae8c --raw`. The resolved paths match the supplied scope and the committed diff. The frontmatter counts the distinct files and findings across both reviews. The seven original findings retain their recorded dispositions. [Original review dispositions](02-REVIEW-DISPOSITION.md)

The incremental scope contains ten files.

- `.gitattributes`
- `.gitignore`
- `.idea/inspectionProfiles/Project_Default.xml`
- `.qodana/profiles/spring-beans.xml`
- `build-logic/src/main/kotlin/courses.jvm.gradle.kts`
- `build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts`
- `docs-site/build.gradle.kts`
- `docs/maintainer-guide.md`
- `qodana.yaml`
- `tools/qodana-scan.sh`

The Gradle edits preserve lazy toolchain resolution and the ordered staging allowlist. The original follow-up recorded a clean build and both root and prefixed documentation checks after those edits. Shell syntax, ShellCheck and `git diff --check` passed during this review. The committed archive at `3779fa2` excludes the IntelliJ profile and contains the Qodana YAML and Spring entry-point XML. [Gradle and documentation verification](../../quick/261126-i4h-resolve-actionable-qodana-findings/261126-i4h-SUMMARY.md)

The retained SARIF controls show that the Axon plugin removed the four handler diagnostics and Spring configuration removed the three probe factories and the temporary genuine bean control. The unused and lookalike bean controls still appear. The native IntelliJ reports show 97 Gradle incubation diagnostics before the profile and zero after it, with both Guava `@Beta` diagnostics present in each report. The maintainer confirmed the editor behavior after reopening the project. The ordinary Qodana report for `fff0b35` retained all 51 Gradle diagnostics with its analysis cache cleaned of the previously seeded editor profile. [Axon verification](../../quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md), [Spring verification](../../quick/261126-jp0-recognize-spring-bean-entry-points-in-qo/261126-jp0-SUMMARY.md), [IntelliJ and Qodana verification](../../quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md)

Manual acceptance covers all seven UAT rows. Hosted QA-08 still requires the matching `build-and-style` run. [Phase 02 UAT](02-UAT.md), [Phase 02 verification](02-VERIFICATION.md)

### CR-04: Historical Qodana scans silently use the editor profile and can contaminate later scans

**Severity:** BLOCKER

**File:** `tools/qodana-scan.sh:36-53`

**Issue:** The launcher accepts any committed revision and archives it with that revision's attributes. The exclusion at `.gitattributes:2` took effect in `fff0b35`. A checked archive of `e434f25` still contains `.idea/inspectionProfiles/Project_Default.xml`, and its retained ordinary scan reports `configProfile: recommended` and `executionSuccessful: true` with zero findings. The clean comparison at `fff0b35` reports 51 `UnstableApiUsage` findings. Both revisions and `3779fa2` select the same analysis cache through the Spring XML blob `3c9deeb0d85d54bdd7d3a968093dc2545359c330`. Qodana persisted the editor profile to that cache. The cached copy matches the historical profile byte for byte, and the clean comparison required moving it out first. The historical result silently drops real diagnostics and can seed the same suppression into a later scan of a clean archive. [Recorded archive and cache control](../../quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md#deviations-from-plan)

**Fix:** Enforce the editor-profile exclusion when the launcher prepares every extracted scan snapshot. Advance the analysis-cache namespace so older cached IDE settings are bypassed while retaining the shared Gradle and plugin caches. Run the ordinary launcher against `e434f25`, then `3779fa2` and then `e434f25` using one cache. Require the Gradle diagnostics in all three reports and verify that the analysis cache contains no editor profile.
