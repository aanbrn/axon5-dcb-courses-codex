---
status: complete
phase: 02-build-and-ui-foundations
source: [02-VERIFICATION.md]
started: 2026-11-25T17:17:41Z
updated: 2026-11-26T08:11:08.168Z
---

## Setup

Start the BFF, web app and prefixed docs using the [deployment base preview commands](../../../docs/maintainer-guide.md#documentation-build). The local shell uses `http://127.0.0.1:5173/` and the docs use `http://127.0.0.1:8081/courses/`. Build Storybook with `./gradlew :web:buildStorybook`, then run `python3 -m http.server 6006 --bind 127.0.0.1 --directory web/build/storybook` and use the `Shell/Home` stories at `http://127.0.0.1:6006/`.

For each browser observation record the OS, browser and any assistive technology settings. The hosted workflow result is tracked in the verification report's ship section.

## Current Test

[testing complete]

## Tests

### 1. Native role selector and forced colors

expected: In the running shell use Tab and Shift+Tab to reach Demo role. Open the native list with the platform shortcut, move through the options with arrows, select a student, then reopen it and close it with Escape. Repeat in a platform-supported forced-colors mode. Record browser, OS and mode. The popup opens and closes, offers Administrator, Maya Chen and Alex Rivera in that order, and keeps the selected role when Escape cancels a tentative choice. Focus returns to the selector and remains visibly outlined.
result: pass

### 2. Screen-reader announcements

expected: With a real screen reader, exercise the loading, initial error, retry failure, retry success and missing saved student Storybook states. Retry once with focus on the button and once after moving to Quick start. Record the browser, OS, reader and spoken sequence. Loading and fallback are spoken through the polite status, and failure is announced inline. Retry becomes available again after failure. Fallback selects Administrator and is announced once. Successful retry restores selector focus only if focus remained on Retry loading roles.
result: pass

### 3. Actual 200% text zoom

expected: Use a browser with text-only zoom at 200%. Inspect the app and prefixed docs at 320, 768 and 1280 CSS px, plus the narrow long-name story. Tab through the header and the feasibility report's wide table and code sample. Header, feedback, controls and focus rings fit without page-wide scrolling. A clipped selection has its full wrapped name below the control. Wide content scrolls within its named, keyboard-accessible region.
result: pass

### 4. Demo role boundary

expected: Review the production selector, its storage and the BFF route before resolving the role-boundary prohibition. Approve the tab-local teaching selection and confirm that it grants no login session or authorization.
result: pass

### 5. Private advisory boundary

expected: Review the docs output allowlist, workflow permissions and public guide using the public evidence. Approve that private inventories, feeds, credentials and scanner output remain outside the repository, site, CI and logs. B8 remains incomplete until authorized inputs and scanner are available.
result: pass

### 6. Phase 1 handoff

expected: Read the rendered feasibility handoff and confirm Phase 7 owns the first hosted AMD64 DCB runtime run. Approve the historical ARM64 scope and the preservation of the runnable probe until the replacement criteria are met.
result: pass

### 7. Test-tier prohibition review

expected: Review the four test-tier prohibition projections against the linked task-level controls. Record the maintainer's disposition for local contract generation, the single-operation OpenAPI contract, staged-file isolation and the ordinary build graph.
result: pass

The maintainer accepted all four guarantees after reviewing their local evidence. [Verification controls](02-VERIFICATION.md#negative-guarantees)

## Summary

total: 7
passed: 7
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
