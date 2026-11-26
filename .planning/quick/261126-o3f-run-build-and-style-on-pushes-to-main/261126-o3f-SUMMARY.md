---
phase: quick-261126-o3f
plan: "01"
subsystem: build-tooling
tags: [github-actions, workflow-policy, actionlint, shellcheck, gradle]
requires:
  - phase: 02-build-and-ui-foundations
    provides: The required build-and-style job, workflow checker, and shared style policy
provides:
  - Build and style checks for every revision pushed to main
  - Regression controls for missing, unrestricted, and misdirected push triggers
affects: [pull-request-ci, main-branch-ci]
tech-stack:
  added: []
  patterns: [Exact GitHub Actions event-map validation]
key-files:
  created: []
  modified:
    - .github/workflows/build.yml
    - tools/check_pr_workflow.py
    - docs/maintainer-guide.md
key-decisions:
  - Use the existing build-and-style job and default event checkout for both triggers.
requirements-completed: [QA-08]
actuals:
  tokens: 1507
  tasks: 2
  commits: 3
commits: 3
plan_head_before: e5740a10e25591057386af94be7666803e6d503c
plan_head_after: b51840d6e7f8e4549a9a74eb62241a28fa904693
duration: 4m 47s
completed: "2026-11-26"
status: complete
---

# Quick plan 261126-o3f: Build and style on pushes to main

The shared `build-and-style` job checks the PR merge revision and each revision pushed to `main`, including after a merge. Both events use read-only contents access, SHA-pinned actions, and checkout with credential persistence disabled.

## Verification

- RED. The real checker and the locked YAML parser accepted the original PR-only workflow. The targeted unittest `test_rejects_a_workflow_without_a_main_push_event` failed because no `WorkflowError` was raised. GSD accepted the complete assertion report as `RED_EVIDENCE_OK`.
- GREEN. The updated checker exited 1 against the original YAML with `Use pull_request without filters and limit push to the main branch.` The updated workflow passed `mise exec python -- python3 tools/check_pr_workflow.py`. The checker rejected all six controls for their intended reasons, including missing push, unrestricted push, a push to another branch, write access, an unpinned checkout action, and disabled ShellCheck.
- `mise exec aqua:rhysd/actionlint shellcheck -- actionlint -shellcheck=shellcheck -pyflakes=` passed.
- `mise exec java python ruff taplo -- ./gradlew --console=plain styleCheck` passed after the repository's managed Prettier formatted the revised Checkout row.
- The hosted PR check and the hosted `main` push check remain pending at local task completion.

## Task commits

- `66a7f76` added controls for unsafe workflow triggers.
- `afc7fc9` added the scoped push trigger and required it in the workflow checker.
- `b51840d` documented the event checkout revisions in the maintainer guide.

The repository's pre-commit hook ran for every task commit.

## Deviations from plan

Execution followed the approved plan.

## Self-Check: PASSED
