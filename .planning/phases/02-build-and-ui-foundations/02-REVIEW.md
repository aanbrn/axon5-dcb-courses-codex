---
phase: 02-build-and-ui-foundations
reviewed: 2026-11-26T09:22:00Z
depth: standard
base_revision: cca11b1248b4f1c6b64aab557c98afa1173fc46b
reviewed_revision: c96780221b9fa19af5987c68927ebdced67a9351
files_reviewed: 5
files_reviewed_list:
  - docs-site/test/site.test.mjs
  - docs-site/verify-site.mjs
  - docs/maintainer-guide.md
  - web/build.gradle.kts
  - web/test/client-graph.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
  necessity: 0
status: issues_found
---

# Phase 02 Code Review Report

- **Reviewed** 2026-11-26T09:22:00Z
- **Depth** standard
- **Files reviewed** 5
- **Status** issues_found

## Summary

This corrective review covers the five source changes from `cca11b1` to `c967802` and follows the initial 17-file review recorded in `c22c7c9`. CR-05 and WR-05 through WR-07 pass their original failing controls. The correction introduces one publication warning for raw markup in a textarea. The current docs contain no textarea case.

The wrapper and direct client graph harness passed. With the output build cache enabled, changing only an inherited variable changed the loaded bundle URL from `/first/` to `/second/`. Changing only the inherited port to an invalid value then failed with the fixed Vite diagnostic. Command output omitted the supplied value. A repeated default build reported `UP-TO-DATE`. The strict optional configuration-cache run encountered the same pre-existing script-object serialization failure in `:web:npmInstall` before and after the change. After npm provisioning and exclusion of that task, the isolated graph stored and reused the configuration cache while still detecting newly created dotenv files and inherited-variable changes. [Vite correction evidence](../../quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md)

The Gradle docs suite passed all 40 checks at both deployment bases. A second pass used the pinned Node directly against fresh outputs at both bases. The new positive cases retain the exact nine-file output, decoded fragments, template-element IDs and live targets after nested templates. Separate local HTTP probes returned 200 for the canonical path, its `index.html` alias and a query containing an encoded slash. They returned 404 for encoded path aliases. [Publication correction evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md)

## Narrative Findings (AI reviewer)

## Warnings

### WR-08: The publication gate mistakes literal textarea content for an active base

**Severity:** WARNING

**File:** `docs-site/verify-site.mjs:18-32`

**Issue:** The pinned `htmlparser2` 7.2.0 tokenizer reports a tag inside `textarea` through the same callback as active markup. The new guard then rejects it as an active `<base href>`. A disposable staged Quick start containing `<textarea aria-label="Example markup"><base href="../feasibility/phase-01/"></textarea>` built at `/` and `/courses/` with the `cca11b1` verifier. The `c967802` verifier rejected both builds with `Active base href in quick-start/index.html`. Chromium reported zero base elements and the exact markup as the textarea's value. An author can therefore trigger a publication failure by displaying otherwise valid literal markup in a textarea.

**Fix:** Base the active-element check on a parser mode that recognizes textarea content as text. Add the textarea fixture as a positive at both bases alongside the existing active-base negatives.

## Prior review dispositions

<a id="cr-04-historical-qodana-scans-silently-use-the-editor-profile-and-can-contaminate-later-scans"></a>

The ledger records CR-01 through CR-04 and the original Phase 02 WR-01 through WR-04. Slice labels refer to the separate application review. The original corrective findings and reproductions appear in the Phase 02 review at `c22c7c9`. [Phase 02 disposition ledger](02-REVIEW-DISPOSITION.md) · [Application slice review](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md)

| Finding | Disposition at `c967802` | Evidence |
| --- | --- | --- |
| Phase 02 CR-04 | Fixed | The launcher excludes the editor profile when creating archives of historical revisions and uses a fresh analysis namespace. The retained historical, delivery and historical-repeat sequence on one analysis cache recovered all 51 reference Gradle diagnostics. The first historical scan had one additional Gradle diagnostic. The workspace profile and existing Gradle and plugin cache directories were preserved. [Historical scan verification](../../quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-VERIFICATION.md) |
| Phase 02 CR-05 | Fixed | Production dotenv files force Vite to run. The original inherited-path and invalid-port cases pass, and the default no-file build still reuses its bundle. The positive direct process override and explicit-empty rejection also pass. [Vite regression evidence](../../quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md) |
| Phase 02 WR-05 | Fixed for active base elements | At `cca11b1`, Chromium applied the override and the guide link returned 404 at both deployment bases. At `c967802`, Eleventy rejects the original active base and the empty active base. WR-08 covers the newly introduced false rejection of literal text. [Active base regression evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Phase 02 WR-06 | Fixed | At `cca11b1`, Chromium found the target only in a template document fragment. At `c967802`, a template-only target fails at both bases. The template's own ID and a later live sibling remain addressable. [Template regression evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Phase 02 WR-07 | Fixed | The gate now uses exact preview path keys. Encoded slash and encoded letter aliases fail at both bases. Normal route aliases, query values and decoded live fragments pass. At `cca11b1`, Chromium preserved the encoded slash and received a 404 from the preview. [Path regression evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Slice WR-01 | Fixed | Vite rejects invalid effective URLs through build and dev. The targeted checks include the original malformed port, explicit empty override, selected deployment prefix and the Gradle dotenv changes in CR-05. [Shell validation evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Slice WR-02 | Fixed | OpenAPI and Kotlin use the same whitespace character set, with independent NetworkNT and generated Zod checks. The directory enforces exact case-sensitive ID uniqueness on the server and client. Its immutable student snapshot preserves the server invariant after validation. Chromium exercises invalid directory responses and recovery. [Role directory evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Slice WR-03 | Fixed | All 26 regions across the current articles have distinct, contextual names within each article. Chromium found them by exact accessible name and checked tab order, visible focus and arrow-key scrolling on overflowing regions. [Landmark evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |
| Slice WR-04 | Fixed for the reported attribute syntax | Both deployment bases reject the original raw anchor with spaced equals, an unquoted image source, and broken Markdown destinations. [Publication evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |

_Reviewed by gsd-code-reviewer at standard depth._
