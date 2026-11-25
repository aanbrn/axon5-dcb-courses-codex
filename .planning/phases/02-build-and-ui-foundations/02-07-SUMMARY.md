---
phase: 02-build-and-ui-foundations
plan: "07"
subsystem: build
tags: [git, hooks, formatting, gradle, kotlin, prettier, ruff, taplo, steiger]
requires:
  - phase: 02-04
    provides: Approved Prettier version and registry evidence
  - phase: 02-05
    provides: Shared ktfmt and detekt commands and comments configuration
  - phase: 02-11
    provides: Steiger configuration and installed web dependencies
provides:
  - One style policy for the Git index and full tracked checkout
  - Opt-in pre-commit formatting with isolated lint and atomic index publication
  - Disposable parity, concurrency, failure and full-tree controls
  - Exact tracked formatting baseline for integration
affects: [02-08, 02-09]
tech-stack:
  added: [Prettier 3.10.1, git-format-staged 4.0.2, Ruff 0.17.4, Taplo 0.10.0]
  patterns: [isolated source snapshots, shared formatter and lint dispatch, locked index comparison and replacement]
key-files:
  created:
    - .githooks/pre-commit
    - tools/style/package-lock.json
    - tools/style/package.json
    - tools/style/policy.json
    - tools/style/run.py
    - tools/style/test_hook.py
  modified:
    - build.gradle.kts
    - mise.toml
key-decisions:
  - Use the same rules over raw staged blobs and checked-out tracked files, with configuration from the corresponding snapshot.
  - Validate the whole candidate before taking the Git index lock and replacing the original index.
  - Preserve Phase 01 evidence and npm-owned lock bytes while checking their text or structured content.
requirements-completed: [QA-07]
requirements-pending: [QA-08, FND-02]
coverage:
  - id: D1
    description: Staged and tracked modes match on Kotlin and Markdown and preserve check-only inputs.
    requirement: QA-07
    verification:
      - kind: integration
        ref: "python3 tools/style/run.py --self-test"
        status: pass
    human_judgment: false
  - id: D2
    description: Real Git commits format selected blobs and preserve overlapping edits and competing index updates.
    requirement: QA-08
    verification:
      - kind: integration
        ref: "python3 tools/style/test_hook.py"
        status: pass
    human_judgment: false
  - id: D3
    description: The normalized disposable checkout passes all rules, and both snapshots reject deliberate lint violations.
    requirement: QA-08
    verification:
      - kind: integration
        ref: "python3 tools/style/test_hook.py --full-tree"
        status: pass
    human_judgment: false
actuals:
  tokens: 14173
  tasks: 3
  commits: 4
commits: 4
plan_head_before: 9693ceac2d96e4de34157d4300be9766c95ce2ff
plan_head_after: 0ee10d400db64e347ad711d90c26e5b0a5f36ef3
duration: 21m00s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 07: Shared Repository Style and Staged Git Formatting Summary

**One style policy covers the tracked checkout and the active Git index. The opt-in hook formats and validates staged content before publishing the index, and preserves overlapping edits and competing Git writes.**

## Accomplishments

- `styleRuntime` provisions Gradle-managed Node and npm, installs the strict-peer lock, and exports ktfmt, detekt, Prettier and Steiger commands. `installGitHooks` opts in through repo-local `core.hooksPath`. `styleCheck` checks the tracked checkout.
- The staged driver reads raw blobs and configuration from a copy of the active index. It validates the isolated candidate, then compares and replaces the index under the standard Git lock. The working copy receives formatted bytes where a staged formatting edit safely merges with existing unstaged edits.
- All 153 tracked paths have a rule and reason. The inventory includes 56 evidence Markdown, 51 Prettier, 25 Kotlin, six Python, five npm lock, four wrapper, two version, two TOML, one shell, and one default text path. The policy checks the Gradle wrapper checksums and modes, npm lock structure and registry integrity, version files and shell syntax. GSD and feasibility records preserve in-line evidence bytes, and normal Markdown formatting preserves embedded code.

## Task Commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-07-01 | `5670319` | Locked runtime, shared routes and formatter parity |
| 02-07-02 RED | `196035c` | Disposable Git safety tests |
| 02-07-02 GREEN | `0f60c37` | Atomic candidate publication, opt-in hook and pinned CLIs |
| 02-07-03 | `0ee10d4` | Full-tree, configuration and lint parity tests |

## Verification

| Command | Observed result |
| --- | --- |
| `./gradlew --console=plain styleRuntime` | Passed on macOS ARM64 with Temurin 25.0.5.1+2-LTS, Gradle 9.9.2, and managed Node 26.13.1/npm 12.2.3. |
| `python3 tools/style/run.py --self-test` | Both modes named the intentional Kotlin/KDoc and Markdown differences. Both produced the same formatted bytes, and the second pass was identical. The original fixture index and working bytes were unchanged. Passed again after the tracer commit and after the final task commit. |
| `python3 tools/style/test_hook.py` | Ten tests passed. They cover adjacent, disjoint and overlapping edits, executable mode, empty and repeated invocations, rename/delete, tabs, newlines and shell quoting in paths, a relative alternate index on an unborn branch, a linked worktree, malformed output, formatter abort, lint failure, an unmerged index, an existing lock, and a live writer. |
| `python3 tools/style/test_hook.py --full-tree` | Three tests passed. The staged Prettier options controlled the hook despite a conflicting working policy. detekt received formatted Kotlin and rejected `EndOfSentenceFormat` in both modes when using the same config bytes. The normalized clone passed check-only. Both modes rejected `fsd/forbidden-imports`, and check-only rejected a whitespace-only mutation without modifying the file. |
| `./gradlew --console=plain installGitHooks` | Passed in a fresh temporary clone. Gradle set `.githooks` in local config, and a real commit stored the formatted witness blob. |
| `python3 tools/style/run.py --inventory` | Classified every tracked path and printed its stable name, rule and reason. |
| `./gradlew --console=plain styleCheck` | Returned exit 1 for the 37 pre-existing formatting differences below. There were no linter findings. |

The TDD RED command `python3 tools/style/test_hook.py HookTest.test_commit_formats_staged_adjacent_edits_and_mode` ran one real commit and failed its exact HEAD blob assertion. The blob kept three trailing spaces and excluded the adjacent unstaged edit. GSD returned `RED_EVIDENCE_OK`. The same test passed after implementation. Direct failure controls preserved byte-identical index files. Real `git commit` failures preserved HEAD, every staged object and mode, and working bytes even when Git refreshed its internal index cache before invoking the hook. The tests covered formatter exit 7, successful output containing a NUL, and Ruff exit 1 with `F401`.

## Tool Qualification

- The two npm dependencies matched their reviewed registry identities and had no package install hooks. The exact `prettier@3.10.1` approval covered its age-only flag. The strict-peer install and `npm ci --strict-peer-deps --ignore-scripts --no-audit --no-fund` preserved lock SHA-256 `7e346929fdb52806c9a42417d0d8967968ab54bff1f15a737b6e2ed55f3003f8`. `npm ls --all` confirmed both dependencies. The hook adapts git-format-staged's verified staged-blob and worktree patch semantics to publish all candidate files together. [Prettier release](https://github.com/prettier/prettier/releases/tag/3.10.1), [git-format-staged source](https://github.com/hallettj/git-format-staged/blob/v4.0.2/git-format-staged)
- The native Ruff 0.17.4 ARM64 tarball matched the publisher SHA-256 `6ef8b3a7fd5294f5e8384ceb29784a6f5657da0853824312b1d2cef53aef17af`. It formatted and rejected the positive and unused-import controls respectively. Taplo 0.10.0 formatted and linted valid TOML, then returned exit 1 with `unexpected EOF` for a malformed array. Its ARM64 artifact had observed SHA-256 `713734314c3e71894b9e77513c5349835eefbd52908445a0d73b0c7dc469347d`. The macOS binary needed an escalated local test invocation due to the managed sandbox's SystemConfiguration denial. [Ruff release](https://github.com/astral-sh/ruff/releases/tag/0.17.4), [Taplo release](https://github.com/tamasfe/taplo/releases/tag/0.10.0)
- The wrapper JAR and distribution digests matched the Gradle publisher. The policy also checks the tracked wrapper launchers. [JAR checksum](https://services.gradle.org/distributions/gradle-9.9.2-wrapper.jar.sha256), [distribution checksum](https://services.gradle.org/distributions/gradle-9.9.2-bin.zip.sha256)

## Deviations from Plan

- **[Rule 3 - Blocking] Regenerated stale Gradle Kotlin DSL accessors.** The first `styleRuntime` run failed on generated references. A fresh project cache and `--rerun-tasks` regenerated the accessors and passed with no repository source changes.
- **[Rule 2 - Correctness] Selected explicit Ruff lint rules.** Ruff 0.17.4 default rules added unrelated changes to the existing probe harness. The policy enables `E4,E7,E9,F` and scopes `E402` to the verifier whose intentional setup disables bytecode output before importing its sibling. This retains the current probe behavior. Committed in `0f60c37`.

## Baseline Handoff for 02-09

The full-tree test formats an unborn branch containing the tracked files in a disposable clone. The exact baseline here contains 22 Prettier, 12 Kotlin and three Python paths. The shared checkout retains these differences until 02-09.

```text
AGENTS.md                                                    prettier
build-logic/src/main/kotlin/courses.jvm.gradle.kts           kotlin
docs-site/eleventy.config.mjs                                prettier
docs-site/serve.mjs                                          prettier
docs-site/test/site.test.mjs                                 prettier
docs-site/verify-site.mjs                                    prettier
docs/maintainer-guide.md                                     prettier
probe/build.gradle.kts                                       kotlin
probe/kdoc/Specimen.kt                                       kotlin
probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt      kotlin
probe/src/integrationTest/kotlin/probe/ProbeFixture.kt       kotlin
probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt      kotlin
probe/src/main/kotlin/probe/ProbeApplication.kt              kotlin
probe/src/main/kotlin/probe/ProbeProjection.kt               kotlin
probe/src/test/kotlin/probe/ProbeContractsTest.kt            kotlin
probe/src/typeIdProbe/kotlin/probe/TypeIdVectors.kt          kotlin
probe/typeid/check-vectors.ts                                prettier
probe/verify_evidence.py                                     python
probe/verify_secondary.py                                    python
probe/web/build.gradle.kts                                   kotlin
probe/web/build.mjs                                          prettier
settings.gradle.kts                                          kotlin
tools/check_kotlin_quality.py                                python
web/src/app/theme.css                                        prettier
web/src/pages/home/HomePage.stories.tsx                      prettier
web/src/pages/home/model/useDemoRoles.ts                     prettier
web/src/pages/home/ui/HomePage.tsx                           prettier
web/src/shared/ui/Controls.stories.tsx                       prettier
web/src/shared/ui/alert.tsx                                  prettier
web/src/shared/ui/button.tsx                                 prettier
web/src/shared/ui/index.ts                                   prettier
web/src/shared/ui/native-select.tsx                          prettier
web/test/foundation-proof.mjs                                prettier
web/test/role-states.test.tsx                                prettier
web/test/role-tracer.mjs                                     prettier
web/vite.config.ts                                           prettier
web/vitest.config.ts                                         prettier
```

## Next Phase Readiness

- Plan 02-08 owns the FND-02 inventory and doctor evidence.
- Plan 02-09 owns tracked baseline normalization and PR workflow integration. QA-08 stays pending until the hosted PR check confirms shared style and clean build on the reviewed head.

## Self-Check: PASSED

All eight files exist, the hook is executable, and all four task commits are ancestors of the execution branch. The commit count matches the plan ledger.
