---
phase: 02-build-and-ui-foundations
reviewed: 2026-11-26T09:32:38Z
depth: standard
base_revision: c96780221b9fa19af5987c68927ebdced67a9351
reviewed_revision: 1ca7bf947420172fcfb24b52e85b227d89de8410
files_reviewed: 4
files_reviewed_list:
  - docs-site/package-lock.json
  - docs-site/package.json
  - docs-site/test/site.test.mjs
  - docs-site/verify-site.mjs
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
  necessity: 0
status: clean
---

# Phase 02 Code Review Report

- **Reviewed** 2026-11-26T09:32:38Z
- **Depth** standard
- **Files reviewed** 4
- **Status** clean

## Summary

The source review covers the four documentation-site files changed from `c967802` to `1ca7bf9`, including the dependency manifest and lock. It follows the initial 17-file review in `c22c7c9` and the corrective review in `f4b7210`. WR-08 is fixed.

The verifier uses the parsed HTML document tree to distinguish literal textarea content, inert template descendants and active elements. The active HTML base check still rejects an empty `href`. The index accepts live IDs across namespaces and legacy named anchors in HTML. Exact pathname lookup, decoded fragment matching, private-fixture checks and the nine-file allowlist retain their original behavior. The manifest pins `parse5@8.1.1`. The managed installation preserved the lock bytes and the existing Eleventy transitive resolutions. [Parser correction evidence](../../quick/261126-mq2-use-browser-conforming-html-parsing-for-/261126-mq2-SUMMARY.md)

The retained RED run had 38 passes and six intended failures across both bases. Both managed Gradle documentation runs passed all 44 tests. An independent run against fresh outputs with the pinned Node passed 44 at `/` and 44 at `/courses/`. In both freshly rendered Quick start fixtures, Chromium observed the exact literal textarea value, zero base elements and no live ID for the text-only target. The retained preview run also returned HTTP 200 for both fixtures. [RED, GREEN and preview evidence](../../quick/261126-mq2-use-browser-conforming-html-parsing-for-/261126-mq2-SUMMARY.md)

The earlier Vite correction passed both the Gradle wrapper and direct client graph harness. Changing only an inherited value updated the loaded bundle URL, and changing only the inherited port to an invalid value failed with the fixed diagnostic without printing the value. A repeated default build stayed `UP-TO-DATE`. The strict optional configuration-cache graph encountered the same pre-existing `:web:npmInstall` script-object serialization error before and after the change. With npm already provisioned and that task excluded, Gradle stored and reused the configuration cache while still detecting new dotenv files and inherited changes. [Vite correction evidence](../../quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md)

## Narrative Findings (AI reviewer)

No findings in this corrective source scope.

## Prior review dispositions

<a id="cr-04-historical-qodana-scans-silently-use-the-editor-profile-and-can-contaminate-later-scans"></a>

The ledger records CR-01 through CR-04 and the original Phase 02 WR-01 through WR-04. Slice labels refer to the separate application review. The original corrective findings and reproductions appear in the Phase 02 reviews at `c22c7c9` and `f4b7210`. [Phase 02 disposition ledger](02-REVIEW-DISPOSITION.md) · [Application slice review](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md)

| Finding | Disposition at `1ca7bf9` | Evidence |
| --- | --- | --- |
| Phase 02 CR-04 | Fixed | The launcher excludes the editor profile when creating archives of historical revisions and uses a fresh analysis namespace. The retained historical, delivery and historical-repeat sequence on one analysis cache recovered all 51 reference Gradle diagnostics. The first historical scan had one additional Gradle diagnostic. The workspace profile and existing Gradle and plugin cache directories were preserved. [Historical scan verification](../../quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-VERIFICATION.md) |
| Phase 02 CR-05 | Fixed | Production dotenv files force Vite to run. The original inherited-path and invalid-port cases pass, and the default no-file build still reuses its bundle. The positive direct process override and explicit-empty rejection also pass. [Vite regression evidence](../../quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md) |
| Phase 02 WR-05 | Fixed | At `cca11b1`, Chromium applied the override and the guide link returned 404 at both deployment bases. At `c967802`, Eleventy rejected the original active base and the empty active base. Both rejections still pass at `1ca7bf9`. [Active base regression evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Phase 02 WR-06 | Fixed | At `cca11b1`, Chromium found the target only in a template document fragment. At `c967802`, a template-only target fails at both bases. The template's own ID and a later live sibling remain addressable. [Template regression evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Phase 02 WR-07 | Fixed | The gate now uses exact preview path keys. Encoded slash and encoded letter aliases fail at both bases. Normal route aliases, query values and decoded live fragments pass. At `cca11b1`, Chromium preserved the encoded slash and received a 404 from the preview. [Path regression evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Phase 02 WR-08 | Fixed | At `c967802`, the raw-text sample failed at both bases because the verifier treated the displayed markup as an active base. At `1ca7bf9`, both builds publish the fixture. Live links to the text-only ID are rejected and Chromium confirms that the text creates neither a base element nor a live target. [Textarea regression evidence](../../quick/261126-mq2-use-browser-conforming-html-parsing-for-/261126-mq2-SUMMARY.md) |
| Slice WR-01 | Fixed | Vite rejects invalid effective URLs through build and dev. The targeted checks include the original malformed port, explicit empty override, selected deployment prefix and the Gradle dotenv changes in CR-05. [Shell validation evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Slice WR-02 | Fixed | OpenAPI and Kotlin use the same whitespace character set, with independent NetworkNT and generated Zod checks. The directory enforces exact case-sensitive ID uniqueness on the server and client. Its immutable student snapshot preserves the server invariant after validation. Chromium exercises invalid directory responses and recovery. [Role directory evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Slice WR-03 | Fixed | All 26 regions across the current articles have distinct, contextual names within each article. Chromium found them by exact accessible name and checked tab order, visible focus and arrow-key scrolling on overflowing regions. [Landmark evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |
| Slice WR-04 | Fixed for the reported attribute syntax | Both deployment bases reject the original raw anchor with spaced equals, an unquoted image source, and broken Markdown destinations. [Publication evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |

_Reviewed by gsd-code-reviewer at standard depth._
