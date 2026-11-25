---
phase: 02-build-and-ui-foundations
plan: "06"
subsystem: ui
tags: [react, shadcn, radix, tailwind, playwright, accessibility]
requires:
  - phase: 02-01
    provides: Managed Node and npm, Vite, generated client, and pinned Chromium
  - phase: 02-03
    provides: Production shell and per-tab role selection and recovery tests
provides:
  - Reviewed Nova/Radix Button, NativeSelect, and Alert sources in shared UI
  - A single production stylesheet with local fonts, responsive tokens, and keyboard focus
  - Chromium checks of the compiled shell at narrow and wide widths with enlarged text
affects: [02-11, 02-07, 02-08, 02-09, 03]
tech-stack:
  added: ["shadcn@4.23.0", "tailwindcss@4.3.5", "@tailwindcss/vite@4.3.5", "lucide-react@1.80.0", "tailwind-merge@3.7.1", "radix-ui@1.8.1", "class-variance-authority@0.7.1", "clsx@2.1.1", "@fontsource-variable/geist@5.3.0", "@fontsource-variable/geist-mono@5.3.0"]
  patterns: [project-owned registry sources, native option semantics, measured text clipping, shared light theme]
key-files:
  created:
    - web/components.json
    - web/src/app/theme.css
    - web/src/shared/lib/utils.ts
    - web/src/shared/ui/alert.tsx
    - web/src/shared/ui/button.tsx
    - web/src/shared/ui/index.ts
    - web/src/shared/ui/native-select.tsx
  modified:
    - web/package.json
    - web/package-lock.json
    - web/tsconfig.json
    - web/vite.config.ts
    - web/src/app/main.tsx
    - web/src/pages/home/HomePage.tsx
    - web/test/generated-client.test.ts
    - web/test/role-tracer.mjs
key-decisions:
  - "Generate only the official radix-nova primitives and use the project-owned clsx and tailwind-merge helper."
  - "Measure native selected text against the control content width and display the complete value when it clips."
requirements-completed: [UI-03]
requirements-pending: [UI-01]
coverage:
  - id: D1
    description: The live shell uses reviewed shared primitives for native demo role selection and directory recovery.
    requirement: UI-03
    verification:
      - kind: e2e
        ref: "./gradlew --console=plain :web:provisionBrowser :web:shellSmoke"
        status: pass
    human_judgment: false
  - id: D2
    description: The production shell fits at 320, 768, and 1280 pixels through 200% text scaling and preserves complete clipped selections and keyboard focus.
    requirement: UI-01
    verification:
      - kind: automated_ui
        ref: "web/test/role-tracer.mjs"
        status: pass
    human_judgment: false
actuals:
  tokens: 89501
  tasks: 2
  commits: 2
commits: 2
plan_head_before: 26753e467fedb44d3e111253af2406f8526d4572
plan_head_after: b3f56b2b6833ab014ada8bdb29367977fdd50f4d
duration: 15m50s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 06: Responsive Shell and Shared UI Summary

**The production demo uses reviewed Nova/Radix primitives and local Geist fonts, with native role switching, retry, visible focus, and full selected names on narrow screens.**

## Accomplishments

- The header keeps the home link, documentation links, and label and selector in DOM order. The role group takes a full row at 480px and below. The centered shell applies the approved light palette, spacing, typography, and 48px minimum standalone hit areas.
- The live role directory keeps its existing loading, Administrator-only, fallback, and retry behaviors. A hidden measurement follows the select width and the bundled font metrics. When a value clips, a wrapping line displays the complete text. The native option exposes that same full name to assistive technology.
- The skip link becomes visible on focus and moves focus to main. Links stay underlined, the report action uses the approved indigo, and the outline switches to the system highlight color in forced colors. The sole app stylesheet is available to the Storybook preview.

## Registry and Package Evidence

On 2026-11-25, Gradle-managed Node `26.13.1` and npm `12.2.3` ran `npm exec -- shadcn init --base radix --preset nova --no-monorepo --yes` in a disposable copy. After routing the aliases to `src/shared`, `npm exec -- shadcn add button native-select alert --dry-run` reported three files and one proposed package. The same command with `--yes` wrote the three sources while a temporary wrapper logged dependency requests. Init proposed `cn`, `shadcn@latest`, CVA, `tw-animate-css`, Radix, Lucide, and Geist. The committed graph uses the approved exact CLI and a local `cn` composed from the approved `clsx` and `tailwind-merge`. The generated animation import had no consumer in these primitives. [Official CLI](https://ui.shadcn.com/docs/cli) · [shadcn 4.23.0 publisher release](https://github.com/shadcn-ui/ui/releases/tag/shadcn%404.23.0)

| Registry item | Registry source SHA-256 | Reviewed differences |
| --- | --- | --- |
| [alert](https://ui.shadcn.com/r/styles/radix-nova/alert.json) | `f253568242c1c69b343f12474002fdbe229f603158171c59e21c491ab79f2e6e` | The CLI output matched the payload. The app uses the local helper and adds a variant attribute for shared theme styling. |
| [button](https://ui.shadcn.com/r/styles/radix-nova/button.json) | `08e5f87833c5db8436e89337ebde0f776bcdbf649d3de69fb89be6441ca2e366` | The CLI output matched the payload. The app uses the local helper. |
| [native-select](https://ui.shadcn.com/r/styles/radix-nova/native-select.json) | `17552c2df3b8f5ee44675979c3c29a02f48454e9204f2a02b64f4b7f28bdfc2c` | Nova replaced the registry icon placeholder with Lucide `ChevronDownIcon` and preserved `aria-hidden`. The app uses the local helper. |

`npm exec -- shadcn --version` returned `4.23.0` from the verified web checkout. `npm exec -- shadcn info --json` reported Vite, Tailwind `v4`, preset `nova`, style `radix-nova`, base `radix`, alias `@/shared/ui`, and official registry template `https://ui.shadcn.com/r/styles/{style}/{name}.json`. It listed `alert`, `button`, and `native-select`. The resolved `src/shared/ui` directory contained those three `.tsx` sources and the app's `index.ts` re-export. The CLI reported `frameworkVersion: null` while the locked Vite version was `8.3.8`.

GSD flagged `shadcn@4.23.0`, `tailwindcss@4.3.5`, `@tailwindcss/vite@4.3.5`, `lucide-react@1.80.0`, and `tailwind-merge@3.7.1` for package age alone. The user explicitly approved those versions. The classifier returned `OK` for Radix `1.8.1`, CVA `0.7.1`, `clsx` `2.1.1`, and both Fontsource packages at `5.3.0`. Direct versions and SHA-512 values matched the exact npm registry manifests. The final lock contains 499 SHA-512 registry tarballs and six entries bundled in the integrity-checked optional Tailwind Oxide WASM tarball. The tracer preserved all previously locked package versions. The theme added only the two font entries. [Tailwind release](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.5) · [Lucide release](https://github.com/lucide-icons/lucide/releases/tag/1.80.0) · [Geist](https://fontsource.org/fonts/geist) · [Geist Mono](https://fontsource.org/fonts/geist-mono)

Approval for `storybook@10.6.9`, `@storybook/react-vite@10.6.9`, `@storybook/addon-a11y@10.6.9`, `@storybook/addon-vitest@10.6.9`, `vitest@5.1.2`, `@vitest/browser-playwright@5.1.2`, `steiger@0.10.0`, and `@feature-sliced/steiger-plugin@0.8.2` applies to 02-11. Approval for `prettier@3.10.1` applies to 02-07. Those dependencies remain for their designated plans.

## Verification

| Check | Observed result |
| --- | --- |
| `npm ci --strict-peer-deps --ignore-scripts --no-audit --no-fund` and `npm ls --all --json` | Both passed on the managed runtime for each proposed lock. The tracer installed 395 packages and the final lock installed 397 on macOS ARM64. Each `npm ci` preserved the lock bytes. |
| `./gradlew --console=plain :web:provisionBrowser :web:shellSmoke` | Chromium `159.0.8154.6` passed all 15 browser checks before and after the tracer commit. The actual BFF supplied the three expected personas in order, and independent same-origin tabs restored distinct selections. |
| `./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:shellSmoke` | Native TypeScript compilation and Vite production packaging passed. The generated-client suite passed 19 tests and Chromium passed 17, without failures or skips. Both Geist families emitted local WOFF2 assets and Chromium confirmed the interface face loaded. |
| Responsive and trust-boundary assertions | At 320, 768, and 1280 CSS pixels and 100% and 200% root text size, the shell fit without page overflow. A value appeared in full when the viewport narrowed and disappeared again when it fit. An option with markup-like characters remained literal in both the native option and the wrapping line. A long heading, label, link, and status wrapped at 320px. |
| Keyboard and error assertions | Tab and Shift+Tab followed DOM order. Enter on the skip link focused main. Chromium observed the 2px indigo outline and 2px offset, then the system `Highlight` outline and `ButtonText` select boundary in forced colors. The retry control retained its white fill and 48px minimum target at 320px and 200% text size. Existing retry tests covered Enter, Space, focus restoration, and retry failure. |
| Visual inspection | Chromium screenshots of the 1280px shell and the 320px shell at 200% text size showed the expected hierarchy, selection clipping, full wrapped label, and report action within the page. |

Gradle used Temurin `25.0.5.1` with Docker pointed to an unreachable loopback endpoint. The first checkout-local run hit stale generated Kotlin DSL accessors in `:build-logic:compileKotlin`. An isolated source snapshot with the exact task files ran every planned command successfully and was reused for the tracer feedback run and final verification. The preexisting Gradle deprecation advisory remained informational. The final lock SHA-256 was `c9af5b49463d7eb9a00a7c464844bb65f6d1f1404f54f1acac78b2831efca21b`.

## Task Commits

1. `fd23df4` uses the reviewed Nova primitives on the production shell and adds exact dependencies and aliases.
2. `b3f56b2` applies the responsive theme, adds the local font assets and clipping behavior, and verifies the layout and keyboard contract in Chromium.

## Deviations from Plan

- **[Rule 3 - Blocking issue] Initialize the Tailwind theme and Vite plugin in the tracer.** Nova's Vite preflight requires an actual Tailwind CSS entry point. The tracer commit includes the stylesheet and plugin to prove the primitive integration independently. The second commit adds the complete responsive theme and font imports. Both Gradle commands passed.
- **[Rule 1 - Bug] Apply the focus outline immediately.** The new keyboard test caught a transient gray outline from the generated component transitions. Commit `b3f56b2` removes those transitions in the shared stylesheet. Chromium verified the exact outline on every tab stop.
- **[Rule 1 - Bug] Disable dependency discovery for test-only Vite loaders.** The unit and browser test loaders use Vite for TypeScript transformations with project configuration disabled. Alias discovery scanned the application and emitted unresolved import warnings. Commit `b3f56b2` disables that unused scan in both loaders. The application still resolves the alias through the production and development Vite config. The final typecheck and both suites passed without the scan warning.

## Outstanding Evidence

Plan 02-11 owns Storybook, axe, and Steiger for full UI-01 coverage. Plan 02-09 owns the integrated app and docs navigation, including the outage and launch paths. Phase accessibility acceptance still includes human observation of native dropdown opening and closing, actual browser text zoom, and assistive-technology announcements.

## Self-Check: PASSED
