---
phase: quick-261126-fxn
plan: "01"
subsystem: build-tooling
tags: [mise, python, actionlint, shellcheck, github-actions, doctor]
requires:
  - phase: 02-build-and-ui-foundations
    provides: The shared style driver, pre-commit hook, doctor, and pull request workflow guard
provides:
  - A shared Python patch pin for local repository tooling and the PR style check
  - Pinned actionlint and ShellCheck in the read-only PR build job
  - Informational detection of GSD for Codex in both doctor modes
affects: [local-tooling, pull-request-ci]
tech-stack:
  added: [Python 3.15.2 pin, actionlint 1.7.12, ShellCheck 0.11.0]
  patterns:
    [mise backend-qualified workflow tools, exact interpreter validation]
key-files:
  created: []
  modified:
    [
      mise.toml,
      .github/workflows/build.yml,
      tools/check_pr_workflow.py,
      tools/doctor.py,
      docs/maintainer-guide.md,
    ]
key-decisions:
  - Use the explicit aqua backend for actionlint in the inventory, CI filter, installation, and invocation.
  - Report GSD for Codex from CLI file presence as an informational observation.
requirements-completed: [FND-02]
requirements-pending: [QA-08]
commits: 2
plan_head_before: b17d03c05ee087cb633d1aefac51310fa4d03f37
plan_head_after: 99f4d3276fca59e8202689fd749b0d4901ce93b4
duration: 6m 31s
completed: "2026-11-26"
status: complete
---

# Pin Python and lint the PR workflows

Python 3.15.2 drives repository style tooling, and the read-only `build-and-style` job checks workflows with actionlint 1.7.12 and ShellCheck 0.11.0 before running Gradle style checks.

## What changed

- `mise.toml` owns all three pins. CI installs and reports those exact versions alongside Ruff and Taplo.
- Both doctor modes compare the running Python to the tracked patch pin and report actionlint and ShellCheck versions from their output. GSD for Codex is an informational CLI file-presence observation with checkout precedence, followed by `CODEX_HOME` or `~/.codex`.
- The local workflow guard checks the exact lint command and tool selection alongside the existing permission and action controls. The maintainer guide shows the setup, style, diagnostics, hook and Python script commands.

## Verification

| Check                                                                                                                                   | Local result                                                                                                                                            |
| --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact CI `MISE_ENABLE_TOOLS`, `mise install`, and version steps                                                                         | The five configured tools resolved. Python reported 3.15.2, actionlint 1.7.12, and ShellCheck 0.11.0. Direct Gradle used the supplied Temurin 25.0.5.1. |
| `mise exec python -- python3 tools/doctor.py --self-test`                                                                               | Eight tests passed, including same-minor Python patch drift in both modes and isolated GSD location checks.                                             |
| Bootstrap doctor                                                                                                                        | Required checks passed with Python 3.15.2. A separate run with Python 3.14.10 exited 1 with the pin, observed version and repair command.               |
| `mise exec python ruff taplo -- python3 tools/style/test_hook.py`                                                                       | All 14 real pre-commit hook fixtures passed.                                                                                                            |
| `mise exec python -- python3 tools/check_pr_workflow.py`                                                                                | The reviewed workflow passed. Controls for write permission, unpinned checkout and disabled ShellCheck were rejected.                                   |
| `mise exec aqua:rhysd/actionlint shellcheck -- actionlint -shellcheck=shellcheck -pyflakes=`                                            | The checked-in workflow passed. An isolated workflow with an unquoted shell expansion returned exit 1 with ShellCheck SC2086.                           |
| `mise exec java python aqua:rhysd/actionlint shellcheck ruff taplo -- ./gradlew --console=plain styleCheck doctor :docs-site:docsCheck` | Gradle succeeded. Doctor observed Gradle-managed Node 26.13.1 and npm 12.2.3, and all 14 documentation checks passed.                                   |

QA-08 requires a hosted Ubuntu PR run for the revised workflow.

## Task commits

- `f1fe925` added the RED regression. The target test executed and showed that both pre-change doctor modes returned exit 0 for another Python patch in the same minor. GSD accepted the actual unittest report as `RED_EVIDENCE_OK`.
- `99f4d32` implemented and verified the pins, workflow lint, doctor and maintainer guide. The repository pre-commit hook ran for both commits.

## Execution decisions

- The explicit `aqua:rhysd/actionlint` form identifies the same configured tool across mise commands. The short form made mise attempt runtime version resolution in the local checkout.
- User steering added informational GSD installation detection. The check uses file presence and has no effect on the diagnostic exit status.

## Self-Check: PASSED
