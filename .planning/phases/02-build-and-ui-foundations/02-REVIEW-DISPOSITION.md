---
phase: 02
review: 02-REVIEW.md
titles: json
findings:
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
open: 0
total: 7
recorded: 2026-11-25T17:02:30.778Z
---

# Phase 02: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | 02-REVIEW-FIX.md |
| CR-02 | critical | fixed | 02-REVIEW-FIX.md |
| CR-03 | critical | fixed | 02-REVIEW-FIX.md |
| WR-01 | warning | fixed | 02-REVIEW-FIX.md |
| WR-02 | warning | fixed | 02-REVIEW-FIX.md |
| WR-03 | warning | fixed | 02-REVIEW-FIX.md |
| WR-04 | warning | fixed | 02-REVIEW-FIX.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
