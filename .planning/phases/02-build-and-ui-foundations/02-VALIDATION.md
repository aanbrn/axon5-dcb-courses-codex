---
phase: "02"
slug: build-and-ui-foundations
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-25"
---

# Phase 02 — Validation Strategy

## Test Infrastructure

| Property | Value |
| --- | --- |
| Frameworks | Gradle JVM Test Suites, JUnit 6, Kotest assertions and properties, Vitest, Storybook, axe, and a Chromium shell smoke |
| Configuration | Owned by the relevant Gradle and npm subprojects. The first execution wave wires their test tasks. |
| Quick checks | Owning task command from the per-task verification map |
| Full build | `DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew clean build --no-build-cache` |
| Additional checks | Repository style, staged-file fixtures, dependency evidence, and explicit browser provisioning and tests |

## Sampling Rate

- Run the owning quick check after each task and retain failures for deliberate negative cases.
- At each integration wave, run the available clean build and the owning checks. Add full style once its driver exists. Prior to baseline normalization, use the disposable full-tree fixture and record any outstanding diagnostics.
- Before local phase verification, exercise the live BFF, shell and documentation together and collect the manual observations below. Obtain hosted evidence when the authorized ship lifecycle pushes the workflow and opens or updates the PR.
- Measure quick and full feedback with the first clean runs. Report any command that exceeds its planning budget and identify the cause in the wave summary.

## Per-Task Verification Map

Execution results stay pending until the named command runs against its implementation. Paths, commands and task names below are planned artifacts. Registry metadata and static checks alone cannot close human or hosted gates.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 02-01-01 | 02-01 | 1 | FND-02 | T-02-SC | Recheck registry evidence before the first install | Registry + conditional checkpoint | `bash -ec 'packages=(orval zod react react-dom typescript vite @vitejs/plugin-react @types/react @types/react-dom storybook @storybook/react-vite @storybook/addon-a11y @storybook/addon-vitest vitest @vitest/browser-playwright playwright @playwright/test steiger @feature-sliced/steiger-plugin shadcn tailwindcss @tailwindcss/vite lucide-react @fontsource-variable/geist @fontsource-variable/geist-mono radix-ui tw-animate-css class-variance-authority clsx tailwind-merge @11ty/eleventy prettier git-format-staged); for pkg in "${packages[@]}"; do if ! npm view "$pkg" name version repository.url time engines peerDependencies scripts.preinstall scripts.install scripts.postinstall --json; then printf "%s\n" "METADATA_UNAVAILABLE $pkg" >&2; fi; done; node .codex/gsd-core/bin/gsd-tools.cjs query package-legitimacy.check --ecosystem npm "${packages[@]}"'` | Existing GSD CLI / npm | Pending |
| 02-01-02 | 02-01 | 1 | FND-06 CQRS-04 UI-03 | T-02-01 | Open the running React page and select a role from the first BFF response | Build/browser | `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :web:provisionBrowser :web:roleTracer` | Planned | Pending |
| 02-02-01 | 02-02 | 2 | FND-05 | T-02-03 | Run a seeded Jupiter property under the shared JVM convention | JVM | `./gradlew --console=plain :bff:bootJar :bff:test --tests 'courses.bff.DirectoryUnitTest'` | Planned | Pending |
| 02-02-02 | 02-02 | 2 | FND-05 | T-02-03 | Share Kotlin helpers between two Jupiter suites | JVM | `./gradlew --console=plain :bff:test :bff:verifyFixtureIsolation` | Planned | Pending |
| 02-02-03 | 02-02 | 2 | CQRS-04 FND-05 QA-07 | T-02-03 T-02-04 | Compare loopback responses with the published OpenAPI document | JVM | `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :bff:test :bff:componentTest :bff:verifyFixtureIsolation` | Planned | Pending |
| 02-10-01 | 02-10 | 2 | FND-06 | T-02-02 | Build the generated application without starting infrastructure | Build/contract | `python3 web/test/client-graph.py --clean` | Planned | Pending |
| 02-10-02 | 02-10 | 2 | FND-06 CQRS-04 | T-02-02 T-02-18 | Detect invalidation and malformed generated-client responses | Build/contract | `./gradlew --console=plain :web:verifyClientGraph :web:webCheck` | Planned | Pending |
| 02-03-01 | 02-03 | 3 | UI-03 | T-02-05 | Select a returned role, reload it and open a fresh tab | Browser/component | `./gradlew --console=plain :web:provisionBrowser :web:shellSmoke` | Planned | Pending |
| 02-03-02 | 02-03 | 3 | UI-03 UI-01 CQRS-04 | T-02-05 T-02-06 | Keep navigation and focus usable through failure and retry | Browser/component | `./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:shellSmoke` | Planned | Pending |
| 02-04-01 | 02-04 | 3 | FND-06 DOC-06 | T-02-07 T-02-08 | Open the canonical Phase 1 report through a Gradle-built docs home | Static site | `./gradlew --console=plain :docs-site:docsBuild` | Planned | Pending |
| 02-04-02 | 02-04 | 3 | DOC-06 UI-01 | T-02-07 T-02-08 | Publish the quick start, guide route and corrected feasibility handoff | Static site | `./gradlew --console=plain :docs-site:docsBuild -PdocsBase=/courses/` | Planned | Pending |
| 02-04-03 | 02-04 | 3 | FND-06 DOC-06 UI-01 | T-02-07 T-02-08 | Test launch modes, allowlisting and relative links | Static site | `./gradlew --console=plain :docs-site:check` | Planned | Pending |
| 02-05-01 | 02-05 | 3 | QA-07 QA-08 | T-02-09 | Format public KDoc and fail verification on a real comments violation | JVM quality | `./gradlew --console=plain :bff:ktfmtCheck :bff:detektComments` | Planned | Pending |
| 02-05-02 | 02-05 | 3 | QA-07 | T-02-09 | Make an actual Dokka warning fail and preserve the good publication | JVM quality | `python3 tools/check_kotlin_quality.py format-comments && python3 tools/check_kotlin_quality.py publication && ./gradlew --console=plain :bff:dokkaGeneratePublicationHtml` | Planned | Pending |
| 02-06-01 | 02-06 | 4 | UI-01 UI-03 | T-02-10 T-02-SC | Use the approved shared primitives on the real page | Browser/component | `./gradlew --console=plain :web:provisionBrowser :web:shellSmoke` | Planned | Pending |
| 02-06-02 | 02-06 | 4 | UI-01 | T-02-10 | Apply the responsive light theme and prepare the browser toolchain | Browser/component | `./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:shellSmoke` | Planned | Pending |
| 02-11-01 | 02-11 | 5 | UI-01 UI-03 | T-02-11 | Render production stories and exercise them in Chromium | Browser/FSD | `./gradlew --console=plain :web:provisionBrowser :web:buildStorybook :web:storyTest` | Planned | Pending |
| 02-11-02 | 02-11 | 5 | UI-01 | T-02-11 | Prove accessibility and slice-boundary checks reject controlled violations | Browser/FSD | `./gradlew --console=plain :web:provisionBrowser :web:webCheck :web:foundationProof` | Planned | Pending |
| 02-07-01 | 02-07 | 6 | QA-08 QA-07 | T-02-12 | Check and format the same file with the same owned rules | Disposable Git | `python3 tools/style/run.py --self-test` | Planned | Pending |
| 02-07-02 | 02-07 | 6 | QA-08 FND-02 | T-02-12 T-02-13 | Commit only formatted staged bytes and protect unstaged work | Disposable Git | `python3 tools/style/test_hook.py` | Planned | Pending |
| 02-07-03 | 02-07 | 6 | QA-08 | T-02-12 T-02-13 | Verify repository-wide parity and baseline existing tracked artifacts | Disposable Git | `python3 tools/style/test_hook.py --full-tree` | Planned | Pending |
| 02-08-01 | 02-08 | 7 | FND-02 DOC-06 | T-02-14 | Diagnose a regular build in the presence of missing optional tools | CLI/evidence | `python3 tools/doctor.py --self-test && env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain doctor` | Planned | Pending |
| 02-08-02 | 02-08 | 7 | DOC-06 FND-02 | T-02-14 T-02-15 | Reproduce the cited public records and document the private procedure | CLI/evidence | `python3 tools/verify_dependency_evidence.py && ./gradlew --console=plain :docs-site:check` | Planned | Pending |
| 02-09-01 | 02-09 | 8 | FND-06 CQRS-04 UI-01 UI-03 | T-02-16 | Open both sites and exercise the complete local launch guide | Integration/CI | `python3 tools/test_phase2_build.py && ./gradlew --console=plain :web:provisionBrowser :web:siteSmoke` | Present | Local pass |
| 02-09-02 | 02-09 | 8 | FND-02 FND-06 QA-07 QA-08 DOC-06 | T-02-16 T-02-17 | Bring the tracked tree under the shared formatter and pin the PR workflow | Integration/CI | `python3 tools/check_pr_workflow.py && mise exec ruff taplo -- ./gradlew --console=plain styleCheck && env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain clean build --no-build-cache` | Present | Local pass, hosted pending |

### Plan 02-09 local evidence

- On macOS ARM64, Temurin 25.0.5.1+2-LTS and Gradle 9.9.2 built from empty outputs with an unreachable Docker endpoint. The post-commit candidate exercise took 82 seconds. It verified fresh BFF, generated TypeScript, Vite, Storybook and docs artifacts, seven JVM tests, unchanged build outputs on repetition and five stable npm locks. The three documented quick-start commands served the expected loopback routes.
- An operation rename regenerated the client and failed its consumer's TypeScript compilation. Restoring the contract restored the exact generated bytes. A separate dry run exposed the injected probe integration dependency, and the graph check rejected it before it could run.
- Chromium 159.0.8154.6 exercised the live BFF, Maya selection and reload, a no-opener Administrator tab in the same BrowserContext, the exact outage and retry UI, and focus restoration. It navigated the four docs pages at a nested base in both modes. Rendered checks covered 320px, 768px and 1280px, 100% and 200% text sizing, the app's complete clipped role name, the docs skip fragment, and keyboard scrolling of the report table and code sample. A broken fragment and browser-only roles failed separate disposable runs. A restored copy passed.
- The parsed workflow check and actionlint passed. Scratch invocations returned exit 1 for write permission, an unpinned action and early wrapper execution. The shared candidate style check passed after normalizing the 37 recorded baseline paths and the new checker. The same clean-build command the workflow uses passed locally in 24 seconds, with 19 generated-client and 14 documentation tests.
- A disposable Git checkout reproduced the installed hook's failure after a clean build deleted its command manifest. The same installation, clean build and ordinary commit passed after Gradle moved the manifest under its ignored project state. The hook formatted staged Kotlin and TypeScript with the surviving managed tools.
- Use the manual-only rows below for native menu behavior, browser text settings and screen-reader observations. The Chromium run used CSS root text sizing and keyboard events for its automated checks.

### Evidence at the ship gate

| Gate | Depends on | Required observation | Status |
| --- | --- | --- | --- |
| Hosted `build-and-style` | Locally verified 02-09-02 workflow committed and pushed by the authorized GSD ship lifecycle | `gh pr checks --watch`, then `gh run view <run-id>`. Record PR, workflow, reviewed head SHA or verified PR merge mapping, URL/ID, runner architecture, wrapper validation, style and clean build conclusions. Repeat on head changes. | Pending ship |
| Private B8 | Authorized inventory generation, scanner and private feed available outside the repository | Keep the public status incomplete while prerequisites are missing. Any check, coverage and findings belong only in the authorized private location. | Open |
| Hosted AMD64 DCB runtime | Phase 7 | Use application suites if equivalent or the retained probe. Both image child digests and an AMD64 hosted build do not establish DCB runtime coverage. | Phase 7 |

### Fallback edge and prohibition review

The phase has an approved UI-SPEC and no separate phase SPEC. The eight covered UI resolutions are quoted in 02-03 and 02-06 truths. The docs and integrated overflow checks are in 02-04 and 02-09.

| Requirement | Probe class | Disposition and evidence target |
| --- | --- | --- |
| UI-03 | boundary, precision | Zero/one/many students, missing admin, unknown/stale complete case-sensitive IDs and valid/invalid response boundaries in 02-10-02 and both 02-03 tasks. Numeric rounding is inapplicable to opaque strings. |
| QA-08 | adjacency, empty, ordering, idempotency, concurrency | Real Git fixtures in 02-07-02 and 02-07-03 cover adjacent hunks, empty index diff, format before lint, repeated calls, locks and conflicting index publication. |
| FND-02 | unclassified, unresolved | Flagged assumption. Report actual launcher/worker and managed tool identities, optional Docker failure and required-version mismatch in 02-08-01. |
| FND-05 | unclassified, unresolved | Flagged assumption. Two suites consume a real fixture variant and production classpath leakage fails in 02-02. |
| FND-06 | unclassified, unresolved | Flagged assumption. Changed/deleted generated output, stable repeat build, Docker isolation and complete clean assets in 02-10/02-09-01. |
| CQRS-04 | unclassified, unresolved | Flagged assumption. Independent wire and generated-client corruption controls in 02-02-03 and 02-10-02. |
| UI-01 | unclassified, unresolved | Flagged assumption. Responsive/keyboard and screen-reader behavior require browser and human observations in 02-11-01/02-11-02 and 02-09-01. |
| QA-07 | unclassified, unresolved | Flagged assumption. Deliberate, diagnostic-specific rule/warning failures in 02-05. |
| DOC-06 | unclassified, unresolved | Flagged assumption. Public provenance, private boundaries and incomplete status in 02-04-03 and 02-08-02. |

The fallback prohibitions in the owner plans use the descriptor-less `projectProhibitions` projection. The decisions are resolved, their machine disposition stays flagged-unverified without wired enforcement evidence. The task-level controls supply scoped observations, and judgment-tier fences retain explicit review. ASVS 1 high/critical findings block release pending verified mitigation.

## Wave 0 Requirements

- [ ] Runnable BFF and browser tracer with a contract, generated client, and positive and negative response checks.
- [ ] Gradle-owned Node/npm execution, browser tests that provision their runtime explicitly, and JVM test suite and fixture conventions.
- [ ] Reproducible docs inputs and style checks, with disposable Git and negative quality-gate fixtures.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
| --- | --- | --- | --- |
| Native select interaction, focus outline, and screen-reader announcements | UI-01, UI-03 | Native browser behavior and announcement order need assistive-technology observation | Use a keyboard and screen reader to switch roles, trigger a failure, retry, and observe fallback. Follow the approved UI-SPEC. |
| Text zoom and native control presentation | UI-01 | Browser and platform rendering differ | Review the shell at narrow, medium, and wide widths and at 200% text zoom. Check long names, the navigation wrap, and visible focus. |
| Hosted job and private advisory evidence | QA-08, DOC-06 | Hosted evidence follows the first pushed workflow and private evidence has external prerequisites | Apply the ship gate above. Public records contain only the private procedure and its scoped completion status. |

## Validation Sign-Off

- [ ] Every task has an automated check or a Wave 0 dependency.
- [ ] Every requirement has a mapped command or scoped manual check.
- [ ] Each deliberate negative check fails for the expected reason.
- [ ] Commands finish without watch mode and their feedback latency is recorded.
- [ ] Actual verification supports `nyquist_compliant: true`.

**Approval** pending execution evidence.
