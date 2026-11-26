---
phase: "02"
slug: "build-and-ui-foundations"
status: approved
shadcn_initialized: false
preset: nova
created: "2026-11-25"
reviewed_at: "2026-11-25T10:38:02Z"
---

# Phase 02 — UI Design Contract

Phase 02 delivers the React demo shell, the demo-role directory, the Storybook foundation, and the documentation launch path. This contract implements UI-01 and UI-03 and the browser portion of CQRS-04 with Phase 02 Context D-01 through D-11. Phase 03 owns the first enrollment workflows and live views.

## Design System

| Property | Value |
| --- | --- |
| Tool | shadcn/ui, official registry, project-owned source in the FSD shared UI layer |
| Preset | Official named `nova` preset with `--base radix`. Apply the project’s neutral and indigo tokens after initialization. |
| Component library | Radix foundation. Use shadcn `NativeSelect` for browser-native role selection. |
| Icon library | Lucide (`lucide-react`). Icons supplement visible labels and are hidden from assistive technology. |
| Font | Geist for the interface and Geist Mono for code, with system sans-serif and monospace fallbacks. Serve application fonts with the static assets. |
| Theme | Light only, with neutral gray surfaces and indigo for the specified accents. |

The user selected shadcn/ui, the light neutral and indigo theme, and the wrapping shared header with a visible role selector. Nova, Radix, Lucide, Geist, and the choices below provide the initial design defaults.

During Phase 02 implementation, initialize the application with the documented `--base radix --preset nova` settings using the project’s npm tooling. Keep the light palette and geometry below in the app theme, with shared styles used by Storybook. Configure the shadcn UI alias as `@/shared/ui` and keep demo-specific data and state outside shared primitives. Resolve and record the CLI version through the project’s build tooling. [shadcn CLI](https://ui.shadcn.com/docs/cli) · [Official preset guidance](https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/design-system.md) · [shadcn theming](https://ui.shadcn.com/docs/theming)

## Component Inventory

Could not enumerate: the Phase 02 React application, shadcn configuration, and component source directory have yet to be created.

The table lists proposed registry primitives for the Phase 02 shell and Storybook. Once the app is initialized, run `npx shadcn info --json` from the app directory, count and list the component sources in the resolved `aliases.ui` directory, and record the resolved CLI version and date with the inventory. Cite both results if the CLI and the files disagree.

| Proposed primitive | Expected import path | Use |
| --- | --- | --- |
| Button | `@/shared/ui/button` | Primary launch or report link treatment and secondary retry button |
| NativeSelect, NativeSelectOption | `@/shared/ui/native-select` | Labeled, single-choice demo role control with native browser behavior |
| Alert | `@/shared/ui/alert` | Shared inline failure treatment with a message and recovery action |

[shadcn Button](https://ui.shadcn.com/docs/components/radix/button) · [shadcn Native Select](https://ui.shadcn.com/docs/components/radix/native-select) · [shadcn Alert](https://ui.shadcn.com/docs/components/radix/alert)

## Spacing Scale

| Token | Value | Usage |
| --- | --- | --- |
| xs | 4px | Label and status gaps |
| sm | 8px | Control groups and icon gaps |
| md | 16px | Narrow viewport gutters, wrapping header groups, and compact section padding |
| lg | 24px | Header gutters above the compact breakpoint and panel padding |
| xl | 32px | Section separation and wide page gutters |
| 2xl | 48px | Minimum block size for standalone actions and major section separation |
| 3xl | 64px | Wide layout main-content inset |

Use an 8px corner radius for interactive controls and notice surfaces. Use full-width input and button hit areas where their labels wrap. The 2px focus outline and its 2px offset are focus geometry.

## Typography

| Role | Size | Weight | Line height |
| --- | --- | --- | --- |
| Label and supporting status | 14px | 600 for labels, 400 for status | 1.5 |
| Body and control value | 16px | 400 | 1.5 |
| Section heading | 24px | 600 | 1.25 |
| Page title | 32px | 600 | 1.2 |

Use rem equivalents with a 16px reference root and respect the browser’s text settings. Reuse the body and label sizes for code and captions.

## Color

| Role | Token and value | Usage |
| --- | --- | --- |
| Dominant (60%) | `--background` `#FFFFFF` | Main app canvas and selector fill |
| Secondary (30%) | `--secondary` `#F5F5F5` | Header, supporting panels, and neutral controls |
| Accent (10%) | `--primary`, `--ring` `#4338CA` | Primary actions and keyboard focus |
| Accent hover | `--primary-hover` `#3730A3` | Hover and active variant of the primary action |
| Primary action text | `--primary-foreground` `#FFFFFF` | Text on primary actions |
| Text | `--foreground` `#171717` | Body, headings, selected role value, and standard links |
| Supporting text | `--muted-foreground` `#525252` | Status, helper text, and disabled selector text |
| Control boundary | `--input` `#737373` | Enabled selector and secondary button outlines |
| Divider | `--border` `#D4D4D4` | Decorative separators |
| Error | `--error-foreground` `#991B1B`, `--error-surface` `#FEF2F2` | Inline role-directory error text, icon, and background |
| Destructive | Not applicable | Phase 02 actions are navigation, role selection, and retry |

The 60/30/10 split describes visual emphasis. Reserve indigo for the app’s `Read feasibility report` action, the docs home launch action, and visible keyboard focus outlines. Render supporting links with neutral text and an underline, and indicate the current docs page with `aria-current="page"` and underlining. Use a neutral surface for generic shadcn hover and selection styling. Keep retry text and outline on a white fill, including inside the error surface.

Calculated sRGB contrast against white and neutral surfaces is 17.93:1 and 16.44:1 for body text, 7.81:1 and 7.17:1 for supporting text, 7.90:1 and 7.25:1 for the focus outline, and 4.74:1 and 4.35:1 for control boundaries. White action text is 7.90:1 on indigo and 9.93:1 on hover indigo. Error text is 7.60:1 on the error surface. [WCAG 2.2 contrast criteria and relative luminance](https://www.w3.org/TR/WCAG22/)

## Copywriting Contract

| Element | Copy |
| --- | --- |
| App page title | `Axon 5 DCB Courses` |
| App introduction | `Explore how Axon 5 uses Dynamic Consistency Boundaries to enforce course enrollment rules.` |
| App primary CTA | `Read feasibility report` |
| Docs home title and primary CTA | `Run the demo` with `Open demo` when the app URL is configured or `Read quick start` for local launch instructions |
| App navigation | `Documentation`, `Quick start` |
| Docs navigation | `Home`, `Quick start`, `Feasibility report`, `Maintainer guide` |
| Role label and persona labels | `Demo role` with `Administrator`, `Maya Chen`, and `Alex Rivera` |
| Loading status | `Loading demo roles…` |
| Empty state heading | `No demo students available` |
| Empty state body | `You can continue as Administrator or read the quick start.` Link the quick start text. |
| Error state | `Could not load demo roles. Try again to switch roles.` |
| Unavailable selector value and retry action | `Roles unavailable` and `Retry loading roles` |
| Saved student fallback notice | `Your previous demo student is unavailable. You’re now using Administrator.` |
| Skip link | `Skip to main content` |
| Destructive confirmation | Not applicable. |

Use the same two student names in the BFF fixture, Storybook, quick start, and examples. The app displays the names returned by the BFF.

## Screens and Navigation

- **React shell.** Use a single app route at `/`. In the shared header, place the `DCB Courses` home link first, documentation links second, and the role group third. Keep the label, selector, and any role feedback together. The main title is the visual anchor. Follow it with the introduction and then the feasibility report link. Use a centered container of at most 1120px with main text limited to 72ch. Above 768px, use 32px outer gutters and 64px top spacing for main content. At 768px and below, use 16px outer gutters and 32px top spacing. Let the header wrap in its DOM order. At 480px and below, give the role group its own row with a full-width selector. Documentation links remain visible in every role state.
- **Documentation site.** The docs home has `Run the demo` as its visual anchor and one launch action. If an app URL is configured, `Open demo` navigates to that URL. Otherwise, `Read quick start` navigates to the local launch instructions. Provide working destinations for the docs home, quick start, Phase 1 feasibility report, and maintainer guide. Page titles anchor each article. Publish the report from `docs/feasibility/phase-01.md` as its single content source. Keep application documentation links independent of the role-directory request and resolve them against the configured docs site base.
- **Storybook.** Use a layout sample with the shared header and separate controls and status stories. The shared selector, button, and inline alert use the same tokens, labels, and variants as the app.

## Role Selector Behavior

Use the generated TypeScript client to load the demo-role directory from the contract-first BFF. Display Administrator first and follow it with the returned students in directory order. A fresh independent tab defaults to Administrator. Persist the selected role identifier for the current tab and restore it on reload after a successful directory response. A different tab keeps its own selection. Use links without an opener relationship when deliberately opening the app in another tab.

| State | Rendering and behavior |
| --- | --- |
| First load | Keep the labeled selector visible and disabled with the loading status as its placeholder. Announce loading politely after the live region is present. |
| Populated | Show Administrator and all returned students. The default directory has two students. A directory with one student still lets the reader choose Administrator or that student. A role change updates the selection in place and keeps focus on the selector. |
| Administrator only | Keep Administrator selected in the visible selector. Show the empty student message and quick start link next to it. |
| Saved student absent | On a successful response that still contains Administrator, fall back to Administrator, update the stored selection, and announce the fallback notice once. If the student list is empty, show the fallback notice and retain the quick start link. |
| Directory failure | Keep the shell visible. Disable the selector with `Roles unavailable` and show the inline error with `Retry loading roles`. A failed request preserves the previously saved selection. Apply the same behavior when a response violates the contract, including missing or invalid required role data. |
| Retrying | Keep the retry button mounted with its label and use `aria-disabled="true"` while the request is pending. Guard repeated activation. Show the loading status beside the selector. On failure, enable the button and announce the error. On success, focus the enabled selector if focus was still on retry. Preserve focus if the user moved elsewhere. |

## Accessibility and Responsive Acceptance

- Target WCAG 2.2 AA. Provide header, navigation, and main landmarks, one page heading, and a skip link that becomes visible on focus and moves focus to main content. Keep the tab order aligned with the DOM order as the header wraps.
- Associate a visible `Demo role` label with the native select. Verify Tab and Shift+Tab, native arrow-key selection, and the browser’s open and close behavior for the dropdown. Retry works with Enter and Space. Show a 2px solid focus outline with a 2px offset on keyboard focus. In forced colors, use the system focus color and preserve the control boundary.
- Use a persistent polite status region for loading and fallback, and an inline alert for load failures. Convey state with text and preserve focus when a status changes. Keep a minimum 48px block size for the selector, buttons, and standalone links.
- Verify the header and main content at 320px, 768px, and 1280px viewport widths and at 200% text zoom. The shell fits without page-level horizontal scrolling. The role group, feedback, links, and focus outlines stay visible. Allow long navigation text and status text to wrap. Constrain the native selector to its container, preserve full option names, and show the complete selected name in a wrapping line below if the collapsed value is clipped. Allow wide code samples and tables in the docs to scroll inside their own keyboard-accessible regions.
- In Storybook, provide populated, loading, Administrator-only, missing saved student, initial error, retry pending, retry success, and retry failure stories. Include a narrow shell story with long names or copy. Check the rendered stories with axe and exercise role selection, retry, and focus restoration with keyboard interaction. Verify the one-student and malformed-response paths in component tests or Storybook interactions. In the running shell verify that a selection survives reload, an independently opened tab starts as Administrator, and the docs links remain usable when the BFF is unavailable. Verify both configured and local-launch paths on the docs home. [Storybook accessibility tests](https://storybook.js.org/docs/writing-tests/accessibility-testing)

## UI Considerations

| Category | Elements | Status | Resolution |
| --- | --- | --- | --- |
| empty | Role directory | ✅ covered | A valid directory containing only Administrator keeps Administrator selected and shows the empty-state message and quick start link. |
| loading | Role directory, selector, retry, navigation and launch links | ✅ covered | While roles load, keep the selector visible and disabled with the loading status. During a retry, keep its button mounted and temporarily unavailable. Render all applicable navigation and launch links with the initial page. |
| error | Role directory, selector, retry, navigation and launch links | ✅ covered | A failed request or invalid directory shows the inline retry state and preserves the stored selection. Navigation and launch links remain available independently of the directory. A failed retry restores the retry action. |
| populated | Role directory | ✅ covered | Display Administrator first, followed by the returned students in directory order. Restore a stored persona present in the response and default a fresh independent tab to Administrator. |
| partial | Role directory | ✅ covered | A valid response missing the saved student selects Administrator and announces the fallback once. Missing or invalid required role data follows the inline error path. |
| overflow | Role directory, feedback, navigation and launch links, shell and docs content | ✅ covered | Keep the selector and links within the wrapping header and allow feedback to wrap. Wide code samples and tables scroll in their own accessible regions. The page fits at 320px and at 200% text zoom. |
| zero-one-many | Role directory | ✅ covered | Zero students shows the empty student state. One or more students can each be selected with the same control. |
| long-text | Role selector, feedback, navigation and launch links, shell and docs content | ✅ covered | Preserve complete option names and show the full selected name below the control if it is clipped. Allow long labels, links, headings, and status text to wrap. |

## Registry Safety

| Registry | Blocks Used | Safety Gate |
| --- | --- | --- |
| shadcn official | `button`, `native-select`, `alert` | Third-party vetting is inapplicable. Review the generated source and diff during Phase 02 implementation. |

## Checker Sign-Off

- [x] Dimension 1 Copywriting
- [x] Dimension 2 Visuals
- [x] Dimension 3 Color
- [x] Dimension 4 Typography
- [x] Dimension 5 Spacing
- [x] Dimension 6 Registry Safety
- [x] Dimension 7 Inventory Provenance (advisory)

**Approval** recorded on 2026-11-25. Record installed inventory provenance and review the generated registry source during Phase 02 implementation.
