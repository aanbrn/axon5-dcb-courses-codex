---
phase: 02-build-and-ui-foundations
plan: "11"
subsystem: ui
tags: [storybook, vitest, playwright, axe, steiger, fsd, accessibility]
requires:
  - phase: 02-01
    provides: Managed Node and npm, the generated BFF client, and pinned Chromium
  - phase: 02-03
    provides: Per-tab role state and live browser recovery tests
  - phase: 02-06
    provides: Shared production controls and the responsive app stylesheet
provides:
  - A static Storybook with ten production shell states and three shared control stories
  - Chromium interactions and WCAG A and AA axe checks with failing negative controls
  - Steiger checks of authored Feature-Sliced Design boundaries in the normal web lifecycle
affects: [02-07, 02-09, 03, 08]
tech-stack:
  added: ["storybook@10.6.9", "@storybook/react-vite@10.6.9", "@storybook/addon-a11y@10.6.9", "@storybook/addon-vitest@10.6.9", "vitest@5.1.2", "@vitest/browser-playwright@5.1.2", "steiger@0.10.0", "@feature-sliced/steiger-plugin@0.8.2"]
  patterns: [production component stories, deterministic directory responses, public FSD entry points, disposable diagnostic controls]
key-files:
  created:
    - web/.storybook/main.ts
    - web/.storybook/preview.ts
    - web/src/pages/home/HomePage.stories.tsx
    - web/src/pages/home/index.ts
    - web/src/shared/api/index.ts
    - web/src/shared/ui/Controls.stories.tsx
    - web/steiger.config.ts
    - web/test/foundation-proof.mjs
    - web/vitest.config.ts
  modified:
    - web/build.gradle.kts
    - web/package.json
    - web/package-lock.json
    - web/src/app/main.tsx
    - web/src/pages/home/model/useDemoRoles.ts
    - web/src/pages/home/ui/HomePage.tsx
key-decisions:
  - "Build static Storybook during assemble and require explicit Chromium provisioning for storyTest and foundationProof."
  - "Use public FSD entry points for the home slice and shared API, with Steiger scanning authored source."
  - "Scope TypeScript 5.9.3 to the approved Steiger plugin to satisfy tsconfck's peer and review the package extension by 2026-12-02."
requirements-completed: [UI-01, UI-03]
coverage:
  - id: D1
    requirement: UI-01
    description: The built Storybook contains production shell states and shared controls that pass Chromium and axe checks.
    verification:
      - kind: automated_ui
        ref: "./gradlew --console=plain :web:provisionBrowser :web:buildStorybook :web:storyTest"
        status: pass
    human_judgment: false
  - id: D2
    requirement: UI-01
    description: Steiger and axe reject the specified disposable violations and accept the restored source.
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:foundationProof"
        status: pass
    human_judgment: false
  - id: D3
    requirement: UI-03
    description: The generated client still switches and restores roles from the live BFF and the shell preserves its recovery behavior.
    verification:
      - kind: e2e
        ref: "./gradlew --console=plain :web:provisionBrowser :web:shellSmoke"
        status: pass
    human_judgment: false
  - id: D4
    requirement: UI-01
    description: The native selector, focus, announcements, and 200% text zoom meet the phase accessibility acceptance.
    verification:
      - kind: manual_procedural
        ref: "02-UI-SPEC.md#accessibility-and-responsive-acceptance"
        status: unknown
    human_judgment: true
    rationale: Native dropdown presentation, browser text zoom, and spoken announcement order require manual phase UAT.
actuals:
  tokens: 41217
  tasks: 2
  commits: 3
commits: 3
plan_head_before: ca7de2cd48d4461eac4b524fa72f84c377482670
plan_head_after: bb50476bb6c24f9d213f7b66581a8d97698b5375
duration: 18m51s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 11: Storybook, Accessibility, and FSD Summary

**The same role shell and shared controls ship in static Storybook, with Chromium interaction tests and verified axe and Steiger failure paths.**

## Performance

- Started at `2026-11-25T14:48:53Z`.
- Completed implementation verification and measured the task commits by `2026-11-25T15:07:44Z`.
- Completed two tasks across fifteen files, including two source moves.

## Accomplishments

- Storybook imports the production theme and renders the real home page, role selector, buttons, and inline alert. Shell stories cover populated, loading, Administrator-only, missing saved student, initial error, retry pending, retry success, retry failure, narrow long names, and malformed responses. The one-student path participates in successful retry.
- The stories exercise Tab and Shift+Tab, selection and persistence, Enter and Space for retry, prevention of repeated requests, and focus restoration. They verify that the polite status element persists across transitions and that a failure preserves the saved role.
- Global axe settings fail each browser story on supported rules for the WCAG 2.2 AA target, including applicable earlier A and AA rules. Steiger uses the official recommended FSD rules on authored `src` and explicitly excludes build and dependency trees.
- The opt-in proof copies the project inputs into temporary directories, introduces one violation at a time, requires a failing command and its precise rule, then restores the input and verifies success. The normal web build includes the static Storybook and FSD check.

## Package Evidence

The approved eight direct package pins match the npm registry versions and SHA-512 integrities. GSD flagged each for age alone and the user approved the exact versions in 02-06. Gradle-managed Node `26.13.1` and npm `12.2.3` ran `npm ci --strict-peer-deps --ignore-scripts --no-audit --no-fund` followed by `npm ls --all --json` successfully for the Storybook graph and the final FSD graph. Both installs preserved their lock bytes. The final lock keeps all prior package versions and integrities, with 693 SHA-512 registry tarballs and six entries bundled by the integrity-checked Tailwind optional WASM dependency. Final SHA-256 is `df22f78ab802468eddba54c72e639a9c5b9a6d1bd2ef5392df8492ba6ee79916`.

Without the package extension, the merged install passed strict `npm ci` while `npm ls --all` exited 1 with `ELSPROBLEMS` and `invalid: typescript@7.0.2`. The affected tooling owner is `@feature-sliced/steiger-plugin@0.8.2`, which loads `tsconfck@3.1.6` under an optional TypeScript peer of `^5.0.0`. The recommended-rule plugin receives a scoped `typescript@5.9.3` dependency through npm's declarative extension. The app and Storybook retain native `typescript@7.0.2`. npm records the extension in lockfile version 4, and `npm explain typescript` confirmed both resolved versions and the original peer range. [npm package extensions](https://docs.npmjs.com/files/package.json/#packageextensions)

**Dependency follow-up.** The web tooling maintainer reviews the extension by 2026-12-02 and whenever the Steiger plugin or its TypeScript config reader is upgraded. npm marked the current `tsconfck` release unmaintained. Remove the extension when a disposable lock regenerated without it passes strict managed npm install, `npm ls --all`, native TypeScript compilation, and the Steiger and Chromium checks. The current extension-free graph reproduced the peer failure above.

## Verification

The Gradle commands ran on macOS ARM64 from a disposable project copy with Temurin `25.0.5.1`, Gradle `9.9.2`, and Chromium `159.0.8154.6`. Docker was pointed at an unavailable loopback endpoint.

| Check | Observed result |
| --- | --- |
| `./gradlew --console=plain :web:provisionBrowser :web:buildStorybook :web:storyTest` | Provisioned a fresh Chromium cache, compiled the generated client and TSX, and passed 13 stories across two files. The post-tracer-commit repeat passed. The same build and stories passed on the final lock. |
| `./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:foundationProof` | Steiger reported no problems. All 19 generated-client tests passed. Both proof tests passed with independent positive, failing, and restored runs. |
| Gate controls | The shared-to-pages import yielded only `fsd/forbidden-imports`. The production Button without an accessible name failed the Actions story on axe `button-name`. Turning off each gate made its proof fail on the expected nonzero exit assertion. Removing retry focus restoration failed `Retry Success` at `toHaveFocus()`. |
| Static Storybook | The published index contained 13 entries. Chromium loaded eight selected cold previews over loopback, including a visible pending retry, a completed retry selecting Maya Chen, and a 320px long-label shell with a visible wrapped selected name and no horizontal overflow. |
| `./gradlew --console=plain :web:clean :web:build` | Rebuilt the static Storybook and app, then ran Steiger and the generated-client suite. The specified absent browser directory stayed absent and no browser task entered the graph. |
| `./gradlew --console=plain :web:provisionBrowser :web:shellSmoke` | All 17 live BFF and real browser regressions passed. This includes the actual skip-link keyboard navigation, native selection, and responsive shell checks. |
| Formatting and lock | The repository's ktfmt `0.65` dry run accepted `web/build.gradle.kts`. The final strict managed npm install preserved the lock SHA-256. |

The build emitted informational Gradle deprecation, Node `module.register()` deprecation, and Storybook bundle-size messages.

## Task Commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-11-01 | `9494347` | Static Storybook, managed Chromium project, production stories, and axe settings |
| 02-11-02 RED | `6abfc3c` | Disposable Steiger and axe proof assertions |
| 02-11-02 GREEN | `bb50476` | FSD entry points, peer-compatible lock, and Gradle quality gates |

## TDD Gate Compliance

- **RED.** The targeted TAP test exited 1 at the baseline acceptance assertion. The existing home slice triggered `fsd/no-segmentless-slices` and the shared API triggered `fsd/public-api`. Both came from the actual Steiger run on authored source. GSD returned `RED_EVIDENCE_OK` and the TAP report contained no discovery or fixture error.
- **GREEN.** Both actual proof tests passed. Each tool rejected its named violation and passed after its restoration. Turning off either rule caused the corresponding proof to fail.
- **REFACTOR.** The GREEN commit contains the completed code without an additional refactor commit. RED records are retained in the ignored `.gsd/tdd-evidence/02-11/` directory.

## Deviations from Plan

1. **[Rule 2 - Missing critical functionality] Add the required authored FSD segments and public APIs.** Task 2 moved the existing page and role hook to `ui` and `model`, added slice and shared API entry points, and updated their callers. Steiger passed its recommended rules and the live shell passed all 17 regression tests. Commit `bb50476`.
2. **[Rule 3 - Blocking issue] Satisfy the Steiger toolchain peer in its own dependency graph.** Task 2 added the exact npm extension described above. The final strict install, dependency inspection, native compiler, Steiger, and Chromium passed. Commit `bb50476`.
3. **[Rule 3 - Blocking issue] Allow the proof to read the installed dependency directory.** Vite's scratch server initially refused the canonical path from the dependency symlink. The Vitest server now allows the specific project root and canonical installed dependency directory, with its cache under the build directory. The real axe proof passed. Commit `bb50476`.

## Outstanding Phase UAT

Record the browser and platform while verifying native dropdown opening and closing with arrow keys, visible focus in forced colors, screen-reader order for loading, fallback and retry, and layout at actual 200% browser text zoom across 320px, 768px, and 1280px viewports. Phase 02-09 retains integrated documentation navigation and launch verification.

## Self-Check: PASSED
