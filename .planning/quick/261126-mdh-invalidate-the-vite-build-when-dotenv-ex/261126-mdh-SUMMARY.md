---
phase: quick-261126-mdh
plan: "01"
subsystem: web build
tags: [gradle, vite, dotenv, build-cache]
requires:
  - phase: "02"
    provides: The Gradle-managed Vite production build and disposable client graph verification
provides:
  - Production bundle invalidation for inherited dotenv expansion values
  - Regression checks against the HTML-referenced JavaScript and Vite diagnostics
affects: [FND-06]
tech-stack:
  added: []
  patterns:
    - Execution-time output reuse check over the existing production dotenv file tree
key-files:
  created: []
  modified: [web/build.gradle.kts, web/test/client-graph.py]
key-decisions:
  - Reuse production bundle outputs only when the existing production dotenv file tree is empty.
requirements-completed: [FND-06]
actuals:
  tokens: 1186
  tasks: 2
  commits: 4
commits: 4
plan_head_before: 8715e4a4e4f9791f7e6c24bb6282947c23f73630
plan_head_after: 68c43a0614acac68d5d5e7a3c4b3124abcd6d689
duration: 8m
completed: 2026-11-26
status: complete
---

# Vite Production Dotenv Invalidation Summary

Gradle runs Vite whenever a production dotenv file is present, so inherited values reach the bundled documentation URL and Vite validation. A repeated default build reuses the bundle.

## Regression Evidence

- The pre-fix invalidation command observed `:web:webBuild UP-TO-DATE` after changing only the inherited path. A separate baseline assertion also verified that the HTML-referenced entry retained `https://docs.example.test/first/`.
- Before the fix, changing only the inherited port also left `:web:webBuild UP-TO-DATE`. Gradle exited successfully and skipped the Vite diagnostic. GSD classified both baseline assertions as `RED_EVIDENCE_OK`. Each failure came from its target assertion after the initial bundle succeeded.

## Verification

- `./gradlew --console=plain :web:verifyClientGraph` and `python3 web/test/client-graph.py --invalidation` passed with managed Java and Python. The suite preserved contract generation and recovery, Vite dev validation, direct override precedence, explicitly empty override rejection, and the lockfile bytes.
- With `--build-cache`, changing the inherited path executed `:web:webBuild` and changed the URL in the loaded entry from `/first/` to `/second/`. The invalid inherited port produced `:web:webBuild FAILED` and `VITE_DOCS_BASE must be an absolute HTTP(S) documentation directory URL.` The captured output excluded the synthetic port value.
- The second default build reported `:web:webBuild UP-TO-DATE`, and its loaded entry retained `http://127.0.0.1:8081/`.
- The strict full `--configuration-cache` graph reported the same pre-existing `:web:npmInstall` script-object serialization errors before and after the fix. With npm provisioned and that task excluded, Gradle stored and reused the cache. The unchanged default build stayed `UP-TO-DATE`. Creating the dotenv file and then changing only the inherited path both executed `webBuild` and produced the expected URL in the loaded entry.
- The repository pre-commit hook passed on all three source commits. The scoped `git diff --check` and Ruff checks passed.

## Task Commits

| Commit    | Change                                              |
| --------- | --------------------------------------------------- |
| `4f60ab3` | Reproduce stale dotenv expansion in the Vite bundle |
| `2ff478c` | Rerun Vite when a production dotenv file exists     |
| `68c43a0` | Verify dotenv rejection and default bundle reuse    |

The measured branch range includes the three task commits and the concurrent docs-site commit `22c389f`.

## Self-Check: PASSED
