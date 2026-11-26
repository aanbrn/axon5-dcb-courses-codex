---
phase: 02-build-and-ui-foundations
plan: "03"
subsystem: ui
tags: [react, typescript, session-storage, playwright, accessibility]
requires:
  - phase: 02-01
    provides: "Live BFF launcher, generated client, and pinned managed Node and Playwright"
  - phase: 02-10
    provides: "Validated demo-role adapter and integrated web checks"
provides:
  - "Independent, reloadable demo roles with exact identifier reconciliation"
  - "Keyboard retry, persistent status, and conditional selector focus restoration"
  - "Opt-in shellSmoke checks that begin with the live BFF response"
affects: [02-04, 02-06, 02-08, 02-09, 02-11]
tech-stack:
  added: []
  patterns:
    - "Page-owned React state and tab-scoped sessionStorage"
    - "Abortable directory requests with one active request at a time"
    - "Managed Node TAP and Playwright exercises against the built shell"
key-files:
  created:
    - web/src/pages/home/HomePage.tsx
    - web/src/pages/home/useDemoRoles.ts
    - web/test/role-states.test.tsx
  modified:
    - web/src/app/main.tsx
    - web/build.gradle.kts
    - web/test/role-tracer.mjs
key-decisions:
  - "Keep role selection in tab-local storage and reconcile the whole stored identifier after directory validation."
  - "Run browser component checks using the pinned Playwright and Vite dependencies in the opt-in smoke task."
  - "Capture retry focus when the button leaves the DOM and restore it after the selector is enabled."
patterns-established:
  - "Keep initial, loading, failed, retrying, and ready states in the page hook."
  - "Use one BrowserContext and independent same-origin pages to prove tab isolation."
requirements-completed: [UI-03, CQRS-04]
requirements-contributed: [UI-01]
coverage:
  - id: D1
    requirement: UI-03
    description: "Administrator, Maya, and Alex appear in directory order. The two student selections survive reload independently, and missing or differently cased IDs fall back after validation."
    verification:
      - kind: e2e
        ref: "web/test/role-tracer.mjs#retains independent live BFF selections across same-context tab reloads"
        status: pass
      - kind: automated_ui
        ref: "web/test/role-tracer.mjs#reconciles a differently cased student ID only after a valid directory loads"
        status: pass
      - kind: automated_ui
        ref: "web/test/role-tracer.mjs#reconciles a removed student in an administrator-only directory only after a valid directory loads"
        status: pass
    human_judgment: false
  - id: D2
    requirement: UI-01
    description: "The React shell preserves navigation and selector access through loading, empty, and retry states."
    verification:
      - kind: automated_ui
        ref: "web/test/role-states.test.tsx#keeps navigation and a polite region available through the initial load and an empty directory"
        status: pass
      - kind: automated_ui
        ref: "web/test/role-states.test.tsx#keeps retry mounted, ignores repeat keys and restores focus after recovery"
        status: pass
      - kind: automated_ui
        ref: "web/test/role-states.test.tsx#preserves docs focus when the reader moves away during retry"
        status: pass
    human_judgment: false
  - id: D3
    requirement: CQRS-04
    description: "The browser uses the live generated-client response and keeps the saved role through invalid directory replies."
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :web:webCheck"
        status: pass
      - kind: automated_ui
        ref: "web/test/role-states.test.tsx#preserves the saved role after malformed JSON in an HTTP 200"
        status: pass
    human_judgment: false
actuals:
  tokens: 8245
  tasks: 2
  commits: 4
commits: 4
plan_head_before: 5baf69d117c8feb626546c76bdbabbac9d84d23b
plan_head_after: ef34bb27381a0e8a79114cb39d20d9198c0e3a62
duration: 16m40s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 03 — Demo Role Persistence and Recovery Summary

**The demo restores the exact selected role per browser tab and keeps documentation and keyboard recovery available when the role directory fails.**

## Performance

- Started at `2026-11-25T13:17:35Z`.
- Completed verification by `2026-11-25T13:34:15Z`.
- Completed both tasks across six changed files.

## Accomplishments

- The home page restores the opaque role ID from `courses.demo.role` after a validated response. A fresh tab selects Administrator. A missing saved ID is replaced with the directory administrator ID and an announcement appears once.
- The labeled native selector remains visible while loading or unavailable. A directory containing just Administrator keeps the selector usable and displays the quick start link, including when an absent student triggers a fallback.
- Failed responses preserve the saved role. Retry remains mounted during the pending request and accepts Enter and Space. A failed retry re-enables the action. A successful retry restores focus to the selector when the retry button still has focus and respects focus on other controls.
- Only the active directory request can change the selection or write the fallback. The browser tests resolve an already aborted request after its replacement and verify the selection and storage remain correct.

## Task Commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-03-01 RED | `01d3884` | Live BFF, independent tabs, reload, and exact-ID reconciliation checks |
| 02-03-01 GREEN | `60d2d09` | Tab storage and page-owned role state, with the `:web:shellSmoke` entry point |
| 02-03-02 RED | `124a8da` | Browser component checks for failure, recovery, and focus |
| 02-03-02 GREEN | `ef34bb2` | Guarded retry, polite feedback, empty state, focus handling, and Gradle smoke inputs |

## Verification

Runs used a disposable archive of the checked-out revision with private Gradle project and dependency caches, npm outputs, and Playwright browsers. Docker was pointed to an unavailable loopback endpoint. Observed versions were Gradle 9.9.2, Temurin 25.0.5.1+2-LTS, Node 26.13.1, Vite 8.3.8, and Chromium 159.0.8154.6.

| Command or control | Observed result |
| --- | --- |
| `./gradlew --console=plain :web:provisionBrowser :web:shellSmoke` | Exit 0 before and after the tracer commit. The three tests verified the live response, two independent same-origin tabs in one BrowserContext, reloads, and both exact-ID fallback cases. |
| `./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:shellSmoke :web:roleTracer` | Exit 0 after restoring the disposable controls. The API client suite passed 19 tests and the Chromium suite passed 15 tests, with zero failures or skips in either suite. The earlier `roleTracer` task delegated to `shellSmoke`. |
| Shared storage control | Swapping `sessionStorage` for `localStorage` failed the targeted live test at the fresh tab’s Administrator assertion. |
| Focus control | Restoring focus on every successful load failed the targeted test at the focused documentation link assertion. |
| Storage mutation control | Writing a new saved ID on failure failed the targeted malformed HTTP 200 test at the saved-role assertion. |
| Source and dependency inputs | ktfmt 0.65 with Kotlin coding conventions made no changes to `web/build.gradle.kts`. The package manifest and lock remained byte-identical and the lock SHA-256 was `265a68b1127838d40126679373f6b2004a97e6e8c6284234d4faa98215689b12`. |

## TDD Gate Compliance

- **02-03-01 RED.** Managed Node TAP exited 1 on three intended assertions. After selecting Maya from the live BFF, the baseline reloaded to Administrator. The unknown and differently cased IDs remained in storage after valid responses. The GSD classifier returned `RED_EVIDENCE_OK`.
- **02-03-01 GREEN.** All three browser scenarios passed and the post-commit tracer feedback repeat passed.
- **02-03-02 RED.** The targeted managed Node TAP run exited 1. Chromium received a controlled HTTP 503 and rendered the alert. The test found zero accessible retry buttons when it expected one. The GSD classifier returned `RED_EVIDENCE_OK`.
- **02-03-02 GREEN.** The full browser suite passed all 15 tests. Both recovery focus paths, a failed retry, repeated keys, malformed and invalid responses, blocked storage, and stale completion passed.
- Raw records and command output are retained under the ignored `.gsd/tdd-evidence/02-03/` directory.

## Decisions and Adjustments

- The existing Vite module loader transpiles the TypeScript browser test file for Node’s TAP runner. The stale-response case uses the Vite development entry point to exercise React Strict Mode’s effect restart. The remaining browser cases use the production bundle.
- The smoke task declares the fixture and development source inputs used by the browser component checks. The planned package manifest needed no edit because Vite and Playwright were already pinned.
- The standalone headless Chromium control committed native typeahead and did not commit arrow-key popup selection. The one-student test uses native typeahead to verify keyboard selection and the complete option label.
- The first sandboxed Gradle invocation failed to open its file-lock socket. A scoped local run completed the Gradle, BFF, and Chromium checks.

## Outstanding Evidence

Plan 02-04 supplies the documentation site. Plan 02-06 supplies the shared primitives and responsive behavior. Plan 02-08 documents the future signed-cookie decision. Plan 02-09 tests actual documentation navigation, and 02-11 supplies Storybook and FSD checks for full UI-01 coverage. Native popup behavior and assistive-technology announcement judgment are part of the phase accessibility acceptance.

## Self-Check: PASSED
