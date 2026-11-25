---
phase: 02-build-and-ui-foundations
plan: "09"
subsystem: build-and-ci
tags: [gradle, github-actions, playwright, openapi, eleventy, pre-commit]

requires:
  - phase: 02-07
    provides: Shared repository style policy, staged Git hook, and tracked baseline
  - phase: 02-08
    provides: Toolchain diagnostics and documented version owners
  - phase: 02-11
    provides: Built Storybook, authored FSD rules, and managed Chromium
provides:
  - Reproducible Docker-free build and quick-start checks
  - Live Chromium reader coverage for BFF recovery and both docs launch modes
  - A SHA-pinned, read-only pull request build
  - An installed style hook that survives Gradle clean
affects: [03-core-enrollment-and-live-views, 07-local-operations-and-delivery, ship]

tech-stack:
  added: []
  patterns:
    - Scoped source fixtures for clean Gradle and installed-hook verification
    - Exact parsed workflow policy checked with the existing locked YAML dependency

key-files:
  created:
    - .github/workflows/build.yml
    - tools/check_pr_workflow.py
    - tools/test_phase2_build.py
    - web/test/site-smoke.mjs
  modified:
    - build.gradle.kts
    - web/build.gradle.kts
    - tools/style/run.py
    - tools/style/test_hook.py
    - docs/maintainer-guide.md
    - .planning/phases/02-build-and-ui-foundations/02-VALIDATION.md
key-decisions:
  - Keep the style hook's generated tool manifest in Gradle project state so the installed hook remains usable after a clean build.
  - Use the existing locked YAML parser to verify the exact read-only pull request workflow and its approved actions.
requirements-completed: [FND-02, FND-06, UI-01, UI-03, QA-07, DOC-06]
requirements-pending: [CQRS-04, QA-08]
coverage:
  - id: D1
    description: A clean Gradle build regenerates the application client, publishes the three web outputs, and passes the documented local launch commands.
    requirement: FND-06
    verification:
      - kind: integration
        ref: "python3 tools/test_phase2_build.py"
        status: pass
    human_judgment: false
  - id: D2
    description: Readers can select a live BFF role and keep navigating the shell and docs through a BFF outage and recovery.
    requirement: UI-03
    verification:
      - kind: automated_ui
        ref: "./gradlew --console=plain :web:provisionBrowser :web:siteSmoke"
        status: pass
    human_judgment: false
  - id: D3
    description: Native select controls, browser text zoom and screen-reader announcements work across the documented reader journey.
    requirement: UI-01
    verification:
      - kind: automated_ui
        ref: "web/test/site-smoke.mjs"
        status: pass
    human_judgment: true
    rationale: Chromium CSS text sizing and event checks require native browser and assistive technology observations during phase UAT.
  - id: D4
    description: GitHub runs the shared style checks and clean build for the reviewed pull request head.
    requirement: QA-08
    verification:
      - kind: integration
        ref: "python3 tools/check_pr_workflow.py"
        status: pass
    human_judgment: true
    rationale: The authorized ship run must provide the matching hosted job and head evidence.
  - id: D5
    description: The installed pre-commit hook formats staged Kotlin and TypeScript after the ordinary clean build.
    requirement: QA-08
    verification:
      - kind: integration
        ref: "python3 tools/test_phase2_build.py Phase2BuildTest.test_installed_hook_survives_a_clean_build"
        status: pass
    human_judgment: false
actuals:
  tokens: 116215
  tasks: 2
  commits: 4
commits: 4
plan_head_before: ad02148b5d9f50dd444a06b08ae8df5c9f1cb3cc
plan_head_after: dffefb39c93607214864df2a3dd0755598370081
duration: 28m05s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 09: Local Build and Pull Request Verification Summary

**The clean Gradle build regenerates the BFF client and builds the app, Storybook and docs. Chromium verifies the live reader journey, and the pinned PR job runs the same local build and style checks.**

## Performance

- **Duration** 28m05s
- **Started** 2026-11-25T15:57:25Z
- **Completed** 2026-11-25T16:25:30Z
- **Tasks** 2
- **Files changed by task commits** 45

## Task commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-09-01 RED | `8722dda` | Requested Gradle verification task absent |
| 02-09-01 GREEN | `e0b770e` | Clean build, exact quick start, graph controls and Chromium journey |
| 02-09-02 | `8e2cf73` | Read-only pinned PR job, workflow checker and shared style baseline |
| 02-09-02 regression fix | `dffefb3` | Installed hook survives the same clean build |

## Local verification

| Command | Observation |
| --- | --- |
| `python3 tools/test_phase2_build.py` | All three harness tests passed in 143 seconds. A scoped candidate started from empty outputs. The ordinary graph excluded infrastructure and browser tasks. All seven JVM tests passed, the client and Zod schema regenerated, and the BFF JAR packaged the exact OpenAPI document. The build produced two Vite entry assets, 13 Storybook entries and five Eleventy files. A repeat build kept the cacheable outputs up to date, and five lockfiles were byte-identical. The three published quick-start commands served the expected loopback routes. |
| `./gradlew --console=plain :web:provisionBrowser :web:siteSmoke` | Chromium 159.0.8154.6 passed on macOS ARM64. The first request went through Vite to the live BFF. Maya survived reload, and an independent no-opener tab in the same BrowserContext retained Administrator. Stopping the BFF rendered the exact retry error while navigation stayed available. Restart and keyboard retry restored Maya and selector focus. |
| `python3 tools/check_pr_workflow.py` and `actionlint .github/workflows/build.yml` | Both passed. Independent scratch CLI invocations exited 1 for write permission, an unpinned action and executing Gradle before wrapper validation. |
| `mise exec ruff taplo -- ./gradlew --console=plain styleCheck` | The candidate passed with both new workflow files included. The root passed again after moving the hook manifest. |
| `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain clean build --no-build-cache` | Passed in 24 seconds on the normalized root and after the hook fix. The root check reported 19 generated-client and 14 docs tests with no failures or skips. The installed hook manifest retained its SHA-256 across clean. |
| `python3 tools/test_phase2_build.py Phase2BuildTest.test_installed_hook_survives_a_clean_build` | The disposable Git regression failed before the fix with `Style runtime missing`. It passed in 56 seconds after installation, the same clean build and an ordinary Git commit. The hook formatted the staged Kotlin and returned the deliberately dirty TypeScript file to its original style. |
| `python3 tools/style/test_hook.py` and `python3 tools/style/test_hook.py --full-tree` | Ten staged safety tests and three full-tree parity tests passed with the retained manifest. |
| `mise exec ruff taplo -- env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain doctor` | Passed. Doctor inventoried the four action pins, Gradle 9.9.2, Temurin 25.0.5.1+2-LTS, and managed Node 26.13.1 and npm 12.2.3. Ruff 0.17.4 and Taplo 0.10.0 matched `mise.toml`. |

The tracer RED ran the named unittest with a successful Gradle task query. Its missing `siteSmoke` assertion failed, and GSD returned `RED_EVIDENCE_OK`. Both tracer checks passed after the GREEN commit. The operation rename control regenerated the client and broke the real TypeScript import, then restoring the contract restored the generated bytes. The graph check caught an injected `:probe:integrationTest` edge in a real dry run. Disposable Chromium runs rejected a missing docs fragment and a browser constant that bypassed the live directory request. The restored copy passed.

Browser navigation covered all four docs pages under `/courses/` in both launch modes. The configured home returned to the live app and the local home opened quick-start instructions. Both sites fit at 320px, 768px and 1280px with 100% and 200% root text sizing. Real keyboard events exercised the docs skip target, named table and code scrolling regions, the role selector, retry and focus restoration. The long-name case verified the complete clipped label.

## Publisher refs

GitHub's latest release entries and official Git tag refs were checked on 2026-11-25. The Gradle action uses the annotated tag's peeled commit. The pinned metadata confirmed checkout credential behavior, wrapper validation, the JDK version file and mise's restricted tool installation.

| Action | Release | Verified commit |
| --- | --- | --- |
| [Checkout](https://github.com/actions/checkout/releases/tag/v7.0.1) | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| [Gradle Wrapper Validation](https://github.com/gradle/actions/releases/tag/v6.4.1) | v6.4.1 | `8da46b539cd8fe6ab27ca75128919a18d757604c` |
| [Setup Java](https://github.com/actions/setup-java/releases/tag/v6.3.0) | v6.3.0 | `d1374f8ac74474200d16ef8ecee22c7ae7a51880` |
| [Mise Action](https://github.com/jdx/mise-action/releases/tag/v5.3.0) | v5.3.0 | `924e7c586e33d7d4bae9c14e26c5d22e2beb6e78` |

The PR workflow uses `ubuntu-24.04` x64, `contents: read`, a checkout without persisted credentials, wrapper validation before any Gradle invocation, and [mise 2026.11.14](https://github.com/jdx/mise/releases/tag/v2026.11.14) with Ruff and Taplo as its enabled tools. Runner and effective tool versions are logged. Gradle owns Node and npm selection through the existing pins.

## Exact formatting baseline

The candidate check reproduced the 37 tracked diagnostics from 02-07 and identified a Ruff difference in the new `tools/check_pr_workflow.py`. The shared formatters normalized these specific paths. The canonical feasibility record, Phase 1 planning evidence, and all npm locks were byte-identical to the execution base. Markdown code block contents were preserved.

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

## Deviations from Plan

**[Rule 1 - Bug] Preserve the installed pre-commit hook after clean build**

- **Found during** Task 02-09-02. Gradle clean removed `build/style/commands.json`, and a normal commit failed before formatting.
- **Fix** The existing runtime task writes the manifest under `.gradle/style`. The hook's existing driver reads it there, and the managed formatter and linter binaries retain their existing locations. The new integration case installs the real hook, runs clean build and makes a normal commit.
- **Files** `build.gradle.kts`, `tools/style/run.py`, `tools/style/test_hook.py`, and `tools/test_phase2_build.py`.
- **Commit** `dffefb3`.

A local daemon initially selected a Python without `tomllib` on the final style rerun. Restarting through a single-use Gradle daemon picked up Python 3.12.1 and the check passed. The workflow and tool owner declarations stayed the same.

## Outstanding evidence

- QA-08 awaits the authorized hosted `build-and-style` run for the reviewed PR head. The local workflow, style and build records are complete.
- CQRS-04 has role-directory evidence. Commands, reads and live view contracts follow in the feature slices.
- Phase UAT will record native dropdown open and close behavior, browser text zoom presentation and screen-reader announcements. The automated checks used Chromium keyboard events and CSS text sizing.

## Self-Check: PASSED

The 11 key artifacts exist. All four task commits are ancestors of the execution branch, and the commit count and endpoint match the plan ledger.
