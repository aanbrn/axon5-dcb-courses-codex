# Phase 02 — UI Review

**Audited** on 2026-11-25 against the approved [Phase 02 UI design contract](02-UI-SPEC.md).

Plan 02-06 records prior visual inspection of the 1280px shell and the 320px shell with a 200% CSS root font size. The audit used the source and prior Chromium and Storybook results.

## Pillar Scores

| Pillar            | Score | Key finding                                                                                |
| ----------------- | ----- | ------------------------------------------------------------------------------------------ |
| Copywriting       | 4/4   | The app, docs launch modes, and role feedback use the specified labels.                    |
| Visuals           | 4/4   | The page titles anchor their layouts, and Lucide icons support visible text.               |
| Color             | 3/4   | The docs launch action omits the active color declared in the contract.                    |
| Typography        | 3/4   | The docs name Geist without shipping it and introduce undocumented type treatments.        |
| Spacing           | 4/4   | The app uses the specified gutters, wrap breakpoints, focus geometry, and minimum targets. |
| Experience Design | 3/4   | The docs add keyboard stops for code and table wrappers even when their content fits.      |

**Overall: 21/24.** No shipping blocker was identified in the reviewed evidence. Native popup behavior, spoken announcements, and browser zoom remain open for manual acceptance.

## Follow-Up

Commit `0898e19` publishes local Geist and Geist Mono with their licenses, uses the body size for article subheadings, and gives the launch action the specified weight and pressed color. The integrated Chromium check loaded both fonts from `/courses/` and fetched them with `font/woff2`. The 14 documentation assertions verified the staged assets and the publication allowlist. Documentation scroll regions retain explicit sequential focus so their keyboard entry remains consistent across widths. The manual checks below are still pending.

## Top 3 Priority Fixes

1. **Ship the docs fonts and align the type scale.** Publish local Geist and Geist Mono assets through the docs build. Apply the declared weights and sizes to the launch action and article subheadings.
2. **Skip the extra docs tab stops when there is no overflow.** Make table and code wrappers sequentially focusable when they can scroll. Preserve their accessible names and keyboard scrolling at narrow widths and after resizing.
3. **Apply the specified active color to the docs launch link.** Give `:active` the same `--primary-hover` background as `:hover`, matching the app report action.

## Detailed Findings

### Pillar 1 — Copywriting (4/4)

- App title, introduction, report action, navigation, and all role states match the contract. The empty state retains a linked “quick start” when accompanied by a saved-role fallback. See `web/src/pages/home/ui/HomePage.tsx:12`, `:75`, and `:120–167`.
- Both docs launch labels come from the launch configuration, and the home heading is “Run the demo.” The docs nav, BFF fixture, Storybook, and quick start preserve the specified names. See `docs-site/src/index.11ty.js:3–8`, `docs-site/src/_includes/page.11ty.js:1–6`, `bff/src/main/kotlin/courses/bff/BffApplication.kt:47–48`, `web/src/shared/ui/Controls.stories.tsx:22–29`, and `docs/quick-start.md:36`.

### Pillar 2 — Visuals (4/4)

- The main title, introduction, and single report action establish the shell hierarchy. The docs home has a corresponding launch hierarchy, and the docs layout gives each article its own main landmark. The native chevron and inline warning icon are hidden from assistive technology and paired with visible text. See `web/src/pages/home/ui/HomePage.tsx:134–166`, `web/src/shared/ui/native-select.tsx:29–33`, `docs-site/src/index.11ty.js:5–8`, and `docs-site/src/_includes/page.11ty.js:26–34`.
- Plan 02-06 records visual inspection of the wide and narrow shell. Plan 02-11 records a rendered 320px story where the clipped selector value was available as wrapping text. See [responsive shell evidence](02-06-SUMMARY.md) and [Storybook evidence](02-11-SUMMARY.md).

### Pillar 3 — Color (3/4)

- Dominant white canvases and neutral header surfaces match the contract. Across the two production entry points there are two indigo action placements, one per home page. Focus outlines use the same indigo, docs current-page links stay neutral and underlined, and the retry retains its white fill and control boundary. This establishes the intended 60/30/10 emphasis qualitatively. No pixel-area measurement was made. See `web/src/app/theme.css:24–36`, `:85–97`, `:258–285`, and `docs-site/src/site.css:25–28`, `:51–59`, `:91–122`.
- **WARNING** The docs launch style uses the specified hover background only for `:hover`. The app explicitly applies it to both hover and active states. The docs action can retain its default fill when activated without a hovering pointer. Extend the docs selector to `.launch-action:is(:hover, :active)`. See `docs-site/src/site.css:91–103` and `web/src/app/theme.css:258–260`.

### Pillar 4 — Typography (3/4)

- The app applies the four declared sizes (14, 16, 24, and 32px at the reference root) and the two declared weights (400 and 600). It bundles local variable fonts and preserves system fallbacks. See `web/src/app/theme.css:1–3`, `:47–50`, `:59–83`, `:160–165`, and `:185–189`.
- **WARNING** The docs CSS names Geist and Geist Mono without declaring font faces. The docs build passes through the stylesheet without font assets, and the local docs build contains only HTML and CSS. A reader without local font installations receives the system fallback. The docs also introduce an 18px third-level heading and use 600 weight on the 16px launch action where the contract's body and control value role specifies 400. Publish the local font faces and map these treatments to the approved scale. See `docs-site/eleventy.config.mjs:55–59` and `docs-site/src/site.css:1–14`, `:65–98`, `:163–166`.

### Pillar 5 — Spacing (4/4)

- The shell uses the 4/8/16/24/32/48/64px scale at the reference root. Above 768px it uses 32px main gutters, 24px header gutters, and 64px main inset. At 768px and below those become 16px, 16px, and 32px. At 480px and below the selector occupies its own row. Shell controls use the 8px radius and a 48px minimum block size, and body copy is capped at 72ch inside the centered shell. See `web/src/app/theme.css:37–55`, `:100–105`, `:128–169`, `:228–245`, and `:320–336`.
- The recorded browser checks kept the shell and all four docs routes within the viewport at 320px, 768px, and 1280px with 100% and 200% CSS root sizing. The docs report's wide table and code sample scrolled within their own regions. See `web/test/site-smoke.mjs:207–275` and the [integrated run](02-09-SUMMARY.md).

### Pillar 6 — Experience Design (3/4)

- The persistent status node starts empty and receives loading or fallback text after mount. Errors render inline with an alert. The retry preserves its button while pending, prevents duplicate requests, and returns focus only if the user kept focus on retry. An Administrator-only response preserves the quick-start link. Read/write failures from tab storage fall back to in-memory behavior, and malformed directory responses use the existing failure state. See `web/src/pages/home/ui/HomePage.tsx:34–49`, `:120–150`, `web/src/pages/home/model/useDemoRoles.ts:18–83`, and `web/src/shared/api/demoRoles.ts`.
- Recorded Chromium checks cover the live BFF, per-tab selection, reload, failure and keyboard retry, focus restoration, docs navigation during an outage, and both docs launch modes. The 13 rendered Storybook stories cover the production states and shared controls with axe. See the [integration run](02-09-SUMMARY.md), [Storybook run](02-11-SUMMARY.md), and [phase validation](02-VALIDATION.md).
- **WARNING** The docs renderer emits `tabindex="0"` for every fenced code sample and table, regardless of whether it can scroll. Readers tab through short samples and wide-layout tables that have no scrolling action. Preserve the accessible regions and add sequential focus when their scroll width exceeds their client width. See `docs-site/eleventy.config.mjs:80–106`. The automated check verifies arrow scrolling on two known overflowing report regions at 320px and 200% CSS root sizing. See `web/test/site-smoke.mjs:234–275`.
- **Pending manual UAT.** Record the browser and platform while using Tab, Shift+Tab, arrow keys and Escape through the native select's open, select and close behavior. Observe focus in the platform's forced-colors mode and listen for loading, initial failure, retry failure, successful recovery, and saved-student fallback. At actual 200% browser text zoom, evaluate header wrap, selected-name visibility, and focus outlines at the contract widths. CSS root scaling and scripted keyboard events are automated evidence for the exercised layout and DOM behavior. Spoken announcements, native popup presentation, and actual zoom remain unverified.

## Registry Safety

Registry audit covered zero third-party blocks. `web/components.json` declares no custom registries, and the contract lists only the official button, select and alert. The [Plan 02-06 inventory and provenance](02-06-SUMMARY.md#registry-and-package-evidence) records the installed shadcn 4.23.0 Nova/Radix sources and reviewed local adaptations.

## Files Audited

- App and theme — `web/src/pages/home/ui/HomePage.tsx`, `web/src/pages/home/model/useDemoRoles.ts`, `web/src/shared/api/demoRoles.ts`, `web/src/app/theme.css`
- Shared UI and stories — `web/components.json`, `web/src/shared/ui/button.tsx`, `web/src/shared/ui/native-select.tsx`, `web/src/shared/ui/alert.tsx`, `web/src/shared/ui/Controls.stories.tsx`, `web/src/pages/home/HomePage.stories.tsx`
- Docs and fixture — `docs-site/src/site.css`, `docs-site/src/_includes/page.11ty.js`, `docs-site/src/index.11ty.js`, `docs-site/eleventy.config.mjs`, `docs/quick-start.md`, `bff/src/main/kotlin/courses/bff/BffApplication.kt`
- Browser evidence — `web/test/site-smoke.mjs`, phase context, design contract, and the relevant plan, summary, and validation records
