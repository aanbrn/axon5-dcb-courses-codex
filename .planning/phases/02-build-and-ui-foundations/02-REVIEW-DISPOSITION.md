---
phase: 02
review: 02-REVIEW.md
titles: json
findings:
  - id: WR-08
    severity: warning
    disposition: open
    title: "The publication gate mistakes literal textarea content for an active base"
  - id: CR-05
    severity: critical
    disposition: fixed
    title: "Gradle skips documentation URL validation after a dotenv substitution changes"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "The publication gate resolves relative URLs against the wrong base"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "Inert template content can satisfy a fragment check"
  - id: WR-07
    severity: warning
    disposition: fixed
    title: "The verifier accepts encoded paths that the preview cannot serve"
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Worktree reconciliation can erase an editor save"
  - id: CR-02
    severity: critical
    disposition: fixed
    title: "A path-limited commit leaves an unformatted change staged after success"
  - id: CR-03
    severity: critical
    disposition: fixed
    title: "Staged shell formatting changes literal output"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "A stalled directory response keeps retry unavailable"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The documented prefixed preview leaves the app pointing at the root"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "Bootstrap doctor accepts a missing or malformed Node version pin"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "Gradle's comment check breaks on a path containing a comma"
  - id: CR-04
    severity: critical
    disposition: fixed
    title: "Historical Qodana scans silently use the editor profile and can contaminate later scans"
open: 1
total: 13
recorded: 2026-11-26T09:23:07.411Z
---

# Phase 02: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-08 | warning | open | - |
| CR-05 | critical | fixed | [`68c43a0` and Gradle invalidation tests](../../quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md) (not in the current review) |
| WR-05 | warning | fixed | [`c967802` and the two-base publication tests](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) (not in the current review) |
| WR-06 | warning | fixed | [`c967802` and the two-base publication tests](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) (not in the current review) |
| WR-07 | warning | fixed | [`c967802` and local preview HTTP checks](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) (not in the current review) |
| CR-01 | critical | fixed | 02-REVIEW-FIX.md (not in the current review) |
| CR-02 | critical | fixed | 02-REVIEW-FIX.md (not in the current review) |
| CR-03 | critical | fixed | 02-REVIEW-FIX.md (not in the current review) |
| WR-01 | warning | fixed | 02-REVIEW-FIX.md (not in the current review) |
| WR-02 | warning | fixed | 02-REVIEW-FIX.md (not in the current review) |
| WR-03 | warning | fixed | 02-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 02-REVIEW-FIX.md (not in the current review) |
| CR-04 | critical | fixed | [`3df371b` and three verified scans](../../quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-VERIFICATION.md) (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
