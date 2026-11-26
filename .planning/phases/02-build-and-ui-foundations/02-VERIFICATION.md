---
phase: 02-build-and-ui-foundations
verified: 2026-11-26T08:28:58Z
status: human_needed
score: 30/31 must-haves verified
covered_files: [
  ".gitattributes",
  ".githooks/pre-commit",
  ".github/workflows/build.yml",
  ".gitignore",
  ".idea/inspectionProfiles/Project_Default.xml",
  ".java-version",
  ".nvmrc",
  ".planning/phases/02-build-and-ui-foundations/02-01-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-01-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-02-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-02-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-03-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-03-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-04-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-04-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-05-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-05-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-06-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-06-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-07-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-07-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-08-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-08-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-09-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-09-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-10-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-10-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-11-PLAN.md",
  ".planning/phases/02-build-and-ui-foundations/02-11-SUMMARY.md",
  ".planning/phases/02-build-and-ui-foundations/02-CONTEXT.md",
  ".planning/phases/02-build-and-ui-foundations/02-REVIEW-DISPOSITION.md",
  ".planning/phases/02-build-and-ui-foundations/02-REVIEW.md",
  ".planning/phases/02-build-and-ui-foundations/02-UAT.md",
  ".planning/phases/02-build-and-ui-foundations/02-UI-SPEC.md",
  ".planning/phases/02-build-and-ui-foundations/02-VALIDATION.md",
  ".planning/quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md",
  ".qodana/profiles/spring-beans.xml",
  "AGENTS.md",
  "bff/build.gradle.kts",
  "bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt",
  "bff/src/main/kotlin/courses/bff/BffApplication.kt",
  "bff/src/main/resources/static/openapi.json",
  "bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt",
  "build-logic/build.gradle.kts",
  "build-logic/settings.gradle.kts",
  "build-logic/src/main/kotlin/courses.jvm.gradle.kts",
  "build-logic/src/main/kotlin/courses.kotlin-quality.gradle.kts",
  "build.gradle.kts",
  "config/detekt/comments.yml",
  "docs-site/build.gradle.kts",
  "docs-site/eleventy.config.mjs",
  "docs-site/package-lock.json",
  "docs-site/package.json",
  "docs-site/serve.mjs",
  "docs-site/src/_includes/page.11ty.js",
  "docs-site/src/feasibility/phase-01.11tydata.json",
  "docs-site/src/index.11ty.js",
  "docs-site/src/site.css",
  "docs-site/test/site.test.mjs",
  "docs-site/verify-site.mjs",
  "docs/feasibility/phase-01.md",
  "docs/maintainer-guide.md",
  "docs/quick-start.md",
  "fixtures/build.gradle.kts",
  "fixtures/src/testFixtures/kotlin/courses/fixtures/DirectoryFixtures.kt",
  "gradle/libs.versions.toml",
  "gradle/wrapper/gradle-wrapper.jar",
  "gradle/wrapper/gradle-wrapper.properties",
  "gradlew",
  "mise.toml",
  "probe/README.md",
  "probe/build.gradle.kts",
  "probe/kdoc/Specimen.kt",
  "probe/src/integrationTest/kotlin/probe/AxonProbeTest.kt",
  "probe/src/integrationTest/kotlin/probe/ProbeFixture.kt",
  "probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt",
  "probe/src/main/kotlin/probe/ProbeApplication.kt",
  "probe/src/main/kotlin/probe/ProbeProjection.kt",
  "probe/src/test/kotlin/probe/ProbeContractsTest.kt",
  "probe/src/typeIdProbe/kotlin/probe/TypeIdVectors.kt",
  "probe/typeid/check-vectors.ts",
  "probe/typeid/package-lock.json",
  "probe/typeid/package.json",
  "probe/typeid/vectors.json",
  "probe/verify_evidence.py",
  "probe/verify_secondary.py",
  "probe/web/build.gradle.kts",
  "probe/web/build.mjs",
  "probe/web/package-lock.json",
  "probe/web/package.json",
  "qodana.yaml",
  "settings.gradle.kts",
  "tools/check_kotlin_quality.py",
  "tools/check_pr_workflow.py",
  "tools/doctor.py",
  "tools/qodana-scan.sh",
  "tools/style/package-lock.json",
  "tools/style/package.json",
  "tools/style/policy.json",
  "tools/style/run.py",
  "tools/style/test_hook.py",
  "tools/test_phase2_build.py",
  "tools/verify_dependency_evidence.py",
  "web/.storybook/main.ts",
  "web/.storybook/preview.ts",
  "web/build.gradle.kts",
  "web/components.json",
  "web/index.html",
  "web/orval.config.ts",
  "web/package-lock.json",
  "web/package.json",
  "web/src/app/main.tsx",
  "web/src/app/theme.css",
  "web/src/pages/home/HomePage.stories.tsx",
  "web/src/pages/home/index.ts",
  "web/src/pages/home/model/useDemoRoles.ts",
  "web/src/pages/home/ui/HomePage.tsx",
  "web/src/shared/api/demoRoles.ts",
  "web/src/shared/api/index.ts",
  "web/src/shared/lib/utils.ts",
  "web/src/shared/ui/Controls.stories.tsx",
  "web/src/shared/ui/alert.tsx",
  "web/src/shared/ui/button.tsx",
  "web/src/shared/ui/index.ts",
  "web/src/shared/ui/native-select.tsx",
  "web/steiger.config.ts",
  "web/test/client-graph.py",
  "web/test/foundation-proof.mjs",
  "web/test/generated-client.test.ts",
  "web/test/role-states.test.tsx",
  "web/test/role-tracer.mjs",
  "web/test/site-smoke.mjs",
  "web/tsconfig.json",
  "web/vite.config.ts",
  "web/vitest.config.ts"
  ]
covered_digest: "v4:sha256:1086daa4c3951d843c943aa8dd460b68b9d9af7e0e9a6969b1bb8c9bcf6680c7"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 30/31
  gaps_closed:
    - "The maintainer accepted the four test-tier guarantees in UAT item 7."
  gaps_remaining:
    - "A successful hosted build-and-style check must match the reviewed revision or its verified PR merge commit."
  regressions: []
decision_coverage:
  honored: 15
  total: 15
  not_honored: []
human_verification:
  - test: "At authorized ship, inspect the hosted build-and-style job and reconcile its checked commit with the reviewed revision."
    expected: "Record the PR and run URL, checked SHA or verified PR merge mapping, runner architecture and passing wrapper validation, workflow lint, styleCheck and clean build."
    why_human: "The job runs on a pushed PR and the local refs or phase evidence contain no matching result."
---

# Phase 02 Build and UI Foundations Verification

**Phase goal** — As a maintainer, I want to build and test the demo shell and generated BFF client through shared conventions, so that I can verify later feature slices from a clean checkout.

**Verdict** — `human_needed` · 30/31 must-haves verified · reviewed head `3d0ea4593f4ff1dd764f3a3ed04ef844e750c5d0`

The clean-checkout outcome was demonstrated locally. The maintainer accepted all seven UAT checks at `3779fa2`. Plan 02-09 and QA-08 still require a successful hosted `build-and-style` job for the reviewed revision. CR-04 remains open for the optional historical Qodana scanner.

## User Flow Coverage

| Maintainer step | Expected outcome | Observed evidence | Status |
| --- | --- | --- | --- |
| Start from tracked files and check the required tools. | The documented owners and doctor identify the versions, sources and repairs. | The Gradle report resolved the launcher, BFF worker and managed Node/npm tools. Docker connectivity and architecture appeared under additional checks. | Verified |
| Build the project. | The contract generates the client before frontend compilation and the shared checks run. | A tracked-only candidate ran `clean build --no-build-cache` with Docker refused. The probe checked execution order, generated bytes, the app, Storybook, nine docs files and three JVM suites. | Verified |
| Open the documented app and docs paths. | The BFF feeds the role switcher and the docs remain reachable. | The quick-start probe launched the real BFF, Vite and docs preview. Chromium exercised app and docs navigation at `/courses/`, both docs launch modes and a BFF outage. | Verified |
| Extend the contract and run the shared checks. | Contract changes invalidate consumers, and the hook and CI use the same style policy. | A disposable operation rename regenerated the client, failed the unchanged frontend consumer at typecheck and prevented bundling. The hook and tracked-tree checker both use `tools/style/run.py`. | Verified locally |

## Goal Achievement

### Roadmap Success Criteria

| # | Observable truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | A clean `./gradlew build` builds the documentation site and generates the frontend client from the BFF OpenAPI contract before building the frontend. | Verified | Root `assemble` reaches BFF, web and docs. The BFF's `openApiElements` variant carries one local file, and `generateClient → typecheck → webBuild` is enforced. The clean harness exercised those tasks and output recovery. |
| 2 | A reader can open the React shell and switch between admin and individual demo students. Shared components and loading, empty, and error states are inspectable in Storybook. | Verified | Loopback Chromium reached both students and Administrator. Static Storybook renders the production page and primitives. All 13 Chromium stories passed with axe. |
| 3 | The initial UI-SPEC documents the design foundation, the frontend passes Steiger checks, and the contract gives feature slices an entry point for browser commands, reads, and live views. | Verified for D-04 | The UI-SPEC specifies the design and states. Steiger passed and rejected a deliberate cross-layer import. The live demo operation, generator and Maintainer Guide establish the extension path. Phase 3 adds the first application commands, reads and streams. |
| 4 | A maintainer can run `doctor`, audit authoritative version owners, and run JUnit 6 and Kotest through Gradle JVM Test Suites with shared Java Test Fixtures. The documented dependency maintenance process links recovered or reproduced evidence and keeps advisory inputs and results private. | Verified | Gradle doctor reported managed tools and build tiers. Jupiter ran two BFF unit cases, four loopback component cases and the Phase 1 smoke. Fixture isolation checks all four consumer classpaths. The public guide reconciles historical records and documents a private opt-in B8 procedure. |
| 5 | The pre-commit hook and CI use the same repository formatting and style checks. Representative Kotlin and KDoc pass ktfmt and detekt, and a Dokka warning fails the build. | Verified locally | Staged hook and tracked style use the same driver and policy. All 14 real hook fixtures passed. The ktfmt and detekt controls failed at their intended gates. Dokka emitted one warning per undocumented witness and failed each publication, then passed with the KDoc repaired. |

### Plan Must-Haves

| # | Plan | Observable truth | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | 02-01 | Administrator, Maya Chen and Alex Rivera are selectable from the live BFF directory. | Verified | The real browser tracer checks the request, the exact option order and chosen value against the executable BFF JAR. |
| 2 | 02-02 | One command runs JUnit 6 unit and Docker-free HTTP component suites, both using the published Java Test Fixtures variant. | Verified | The `courses.jvm` convention selects Jupiter and an actual Temurin worker. Both BFF suites consume `testFixtures(project(":fixtures"))`. `verifyFixtureIsolation` checks all four variant consumers and production runtime exclusions. |
| 3 | 02-02 | Independent HTTP schema validation rejects malformed responses and the served contract matches its source. | Verified | Four active `DirectoryHttpTest` cases passed. A separate validator selects schema by path, method, status and media type. Missing Administrator yields `required/administrator`, external references fail, and the published and packaged contract bytes match the source. |
| 4 | 02-03 | Administrator-only leaves Administrator selected and shows the empty-state message and quick-start link. | Verified | The Administrator-only browser and Storybook checks use the production page, assert the empty state and verify the link target. |
| 5 | 02-03 | Loading shows a visible disabled selector, retry retains its button while unavailable, and links render immediately. | Verified | Navigation is outside the state branches. Named tests observe the disabled select, the same button element, `aria-disabled` and initial links. |
| 6 | 02-03 | Transport and contract failures preserve the saved role and independent navigation. A failed retry restores the action. | Verified | Error, retry failure and partial-response deadline cases exercise the same production request path. Chromium observes the saved role and enabled retry again after timeouts. |
| 7 | 02-03 | Administrator is first, returned students keep their order, the current tab restores its valid selection, and an independent tab starts as Administrator. | Verified | The hook prepends Administrator. The live browser test reloads the first tab and checks separate selections within one browser context. |
| 8 | 02-03 | A valid response omitting the saved student selects Administrator and signals fallback once. Missing or invalid data triggers inline error. | Verified at DOM level | Fallback asserts the persistent polite node, stored Administrator and no repeat on reload. Malformed payloads reach inline error. Spoken delivery is a separate UAT check. |
| 9 | 02-03 | Zero students shows the empty state. One or more students are selectable with the same control. | Verified | Zero, one and multiple fixtures use the production selector. The one-student test selects with the keyboard while tab storage is denied. |
| 10 | 02-03 | IDs are complete case-sensitive strings. Unknown or differently cased IDs fall back only after a valid directory. | Verified | The hook uses full string equality. Browser tests exercise stale and case-different IDs alongside failure and recovery. |
| 11 | 02-04 | Configured launch shows one Open demo action. Local launch shows one Read quick start action. Navigation survives a deployment base. | Verified | Docs tests assert both variants and prefixed links. Chromium follows both launch paths, visits the feasibility report and loads both Geist font faces from `/courses/`. |
| 12 | 02-04 | Canonical feasibility Markdown renders the Phase 7 AMD64 handoff and retained probe criteria. | Verified | The staged Markdown matches the source bytes. Rendered output contains the handoff fragment. The canonical report lists the replacement criteria and preserves historical ARM64 scope. |
| 13 | 02-05 | Representative KDoc preserves semantics and ktfmt is byte-idempotent. | Verified | The quality control compares sections before and after the first format, then exact bytes after the second. The original unwrapped Phase 1 input is byte-identical to the Phase 1 revision and passed its own check. |
| 14 | 02-05 | A missing sentence terminator triggers the configured detekt rule and an actual Dokka warning fails publication. | Verified | The comment witness produces `EndOfSentenceFormat` under its original path, including a comma-bearing filename. Retained Gradle control output reports `warningCount=1 and errorCount=0` and failure for both publication tasks, then successful documented builds. |
| 15 | 02-06 | Header and feedback wrap. Wide samples and tables scroll in their regions. The page fits at 320px and actual 200% text zoom. | Verified by UAT | Chromium exercised 320, 768 and 1280 CSS px, scrollable regions and 200% CSS root sizing. The maintainer accepted actual 200% text zoom in [UAT test 3](02-UAT.md#3-actual-200-text-zoom). |
| 16 | 02-06 | Options retain complete names. A clipped selected value appears in full below the control. Long labels, links, headings and status wrap. | Verified | The production component measures clipping across font and size changes. The long-name story and Chromium responsive test check the full wrapping value. |
| 17 | 02-07 | Empty staged input is a no-op. Adjacent staged and unstaged edits remain distinct and overlaps preserve exact unstaged bytes. | Verified | Real Git fixtures assert index and worktree bytes, mode and overlap behavior. Publication affects the candidate index. |
| 18 | 02-07 | Format precedes lint on the candidate, and a rerun preserves bytes, modes and unaffected worktree content. | Verified | Candidate-config detekt and repeated-hook fixtures observe the formatting order and compare original and resulting Git and worktree state. |
| 19 | 02-07 | A competing writer, lock or formatter failure preserves staged and unstaged work. | Verified | The hook opens an exclusive lock and compares original index bytes before publishing. Independent concurrent-writer, existing-lock and failing-tool checks demonstrate preservation. |
| 20 | 02-08 | Doctor reports declared and observed versions, provenance, required tier and repair. Optional infrastructure failure allows a regular build. | Verified | The current eight-test run passed. Independent spot-checks confirmed exact Python patch rejection in both modes and informational GSD detection. The Gradle doctor report passed all required rows with refused Docker, and the same Docker setting allowed a clean build. |
| 21 | 02-08 | The public guide identifies actual selections, controls and missing records, and leaves B8 incomplete. | Verified | The public dependency runner checks selected Gradle graphs and pinned metadata. The guide cites unavailable historical paths and records the private scope and incomplete status. |
| 22 | 02-09 | An ordinary clean build regenerates the client and builds the app, Storybook and docs without infrastructure. | Verified | The post-review harness checked graph order, byte-identical client recovery, public startup, JVM cases, lock stability and failure on an injected opt-in edge. |
| 23 | 02-09 | The pushed PR has a successful read-only and SHA-pinned hosted job for the reviewed revision. | Uncertain · warning | Workflow wiring, actionlint with ShellCheck, local style and clean build passed. The hosted job conclusion and exact reviewed head or PR merge mapping belong to the ship checkpoint. |
| 24 | 02-10 | Generation uses the contract and managed tools, restores deleted output and invalidates consumers after changes. | Verified | The retained direct runner observed generation alone, a no-change `UP-TO-DATE`, byte-identical recovery, rejected external schema reference and a changed operation export that triggers `TS2305` before bundling. |
| 25 | 02-10 | The generated operation rejects malformed successful responses before exposing persona data. | Verified for the specified response boundary | The generated Zod schemas reject missing fields, zero-length strings and wrong discriminators. The adapter rejects duplicate IDs, undocumented status or media, and redirects. All 19 boundary checks passed. The open slice review records two contract gaps outside those assertions: whitespace-only inputs satisfy `minLength: 1`, and the published schema omits the uniqueness invariant. |
| 26 | 02-11 | Storybook publishes production role states and retries. Steiger and axe reject controlled violations. | Verified | Thirteen stories run against real page and control implementations. Steiger reports `fsd/forbidden-imports` and axe reports `button-name` on deliberately broken variants. Repair restores passing results. |

### Negative Guarantees

| Plan | Guarantee | Evidence and disposition |
| --- | --- | --- |
| 02-01 | Generation needs no BFF, runtime API call or Docker. | The published variant is a local file. The standalone runner checks the generation-only task set and rejects a remote schema reference. Public package and tool provisioning uses the declared pins. Accepted in [UAT test 7](02-UAT.md#7-test-tier-prohibition-review). |
| 02-01 | The initial contract publishes only the implemented demo operation. | `DirectoryHttpTest` asserts exact path, method and operation ID on the served contract. Accepted in [UAT test 7](02-UAT.md#7-test-tier-prohibition-review). |
| 02-03 | Demo selection grants no login or authorization. | The read-only endpoint supplies catalog values. React holds the active selection in tab storage and never sends it as a credential. Accepted in [UAT test 4](02-UAT.md#4-demo-role-boundary). |
| 02-04 | Keep private data outside the repository, site and CI. | The staged inputs and published outputs have exact allowlists, reject symlinks or contamination, and include a private-fixture control. The workflow runs only the public checks. Accepted in [UAT test 5](02-UAT.md#5-private-advisory-boundary). |
| 02-04 | Preserve the probe without claiming hosted AMD64 DCB proof. | The probe remains callable. The rendered guide retains its replacement criteria, and Phase 7 owns the first hosted runtime proof. Accepted in [UAT test 6](02-UAT.md#6-phase-1-handoff). |
| 02-07 | Preserve unstaged work and competing index updates. | Real Git fixtures cover overlap, editor saves during publication, and an independent index writer. Accepted in [UAT test 7](02-UAT.md#7-test-tier-prohibition-review). |
| 02-09 | Keep Docker, packaging and infrastructure test tasks out of ordinary builds. | The refused-Docker build, selected-task inspection, injected forbidden edge and opt-in task presence were exercised. Accepted in [UAT test 7](02-UAT.md#7-test-tier-prohibition-review). |

The maintainer explicitly accepted all four test-tier guarantees after reviewing the direct controls. The descriptor-less projections retain their fail-closed automatic status. UAT supplies the required human disposition and also records three judgment-tier acceptances.

## Required Artifacts and Key Links

Existence, substantive implementation and active consumption were checked for every declared artifact. The literal GSD scanner found two stale Plan 02-03 paths and misses links that use Gradle variants, task names, barrel exports or staged Markdown. Commit `bb50476` moved both home files into the expected FSD segments and updated their consumers. The table uses the current paths and resolves those links in source.

| Plan | Substantive artifacts | Verified wiring |
| --- | --- | --- |
| 02-01 | BFF `static/openapi.json`, `web/src/app/main.tsx`, `web/test/role-tracer.mjs` | `openApiElements` carries the contract to Orval. Generated `listDemoRoles` reaches the app through `shared/api` and the home page. The tracer resolves the executable BFF variant and consumes Vite output. |
| 02-02 | `courses.jvm.gradle.kts`, `DirectoryFixtures.kt`, `DirectoryHttpTest.kt` | BFF reaches the JVM convention through the quality convention. Both suites consume the fixture variant. The component tests validate serialized responses and compare the packaged and served contract with the checked-in file. |
| 02-03 | `web/src/pages/home/ui/HomePage.tsx`, `web/src/pages/home/model/useDemoRoles.ts`, `role-states.test.tsx` | The home barrel exports the page to `main.tsx`. The page invokes the hook, which calls the adapter. The returned request, selection and retry state drives the selector, accessible feedback and focus recovery. |
| 02-04 | `docs-site/build.gradle.kts`, `docs/feasibility/phase-01.md`, `docs/quick-start.md` | `stageDocs` copies only public sources and compares canonical bytes. Eleventy uses validated deployment settings. `docsCheck` executes output, link, fragment and allowlist assertions. |
| 02-05 | `courses.kotlin-quality.gradle.kts`, `config/detekt/comments.yml`, `tools/check_kotlin_quality.py` | The production convention passes comments rules to isolated detekt and wires ktfmt, detekt and Dokka into `check`. The quality script invokes the same tasks on disposable witnesses. |
| 02-06 | `web/src/shared/ui/native-select.tsx`, `web/src/app/theme.css` | The home page renders the labelled native select through the shared barrel. The runtime imports the theme with local fonts, focus and wrap behavior. |
| 02-07 | `.githooks/pre-commit`, `tools/style/policy.json`, `tools/style/test_hook.py` | The hook uses `run.py --staged`; root Gradle uses `run.py --check`. The real Git fixtures invoke that hook on disposable candidates. |
| 02-08 | `tools/doctor.py`, `docs/maintainer-guide.md` | Root Gradle supplies actual tool and worker observations. The guide links the canonical Phase 1 evidence and is rendered through the allowlist. |
| 02-09 | `.github/workflows/build.yml`, `tools/test_phase2_build.py`, `web/test/site-smoke.mjs` | The PR job reaches the actual Gradle tasks. The Python harness reproduces the documented startup from tracked sources. `siteSmoke` serves staged docs and the executable BFF on loopback. |
| 02-10 | `build.gradle.kts`, `web/test/client-graph.py`, `web/test/generated-client.test.ts` | Root assembly selects the ordered web tasks. Both production and boundary tests import the same generated-client adapter. The graph runner mutates disposable copies. |
| 02-11 | `web/.storybook/preview.ts`, `HomePage.stories.tsx`, `web/test/foundation-proof.mjs` | Storybook preview loads the live theme and enables accessibility failure. Stories mount the production page with controlled responses. Gradle makes the story and failure-control tasks discoverable. |

### Data-Flow Trace

| Output | Upstream source | Status |
| --- | --- | --- |
| Role options, ordering, label and selected value | Spring demo catalog → real serialized response → generated Fetch and Zod → adapter → hook → native options and rendered selection. The fixed catalog is the intended data source for this phase. | Flowing |
| Loading, outage, retry, fallback and empty state | Request lifecycle, active request deadline, validated response and tab storage determine state. The production page renders that state alongside independent docs URLs. | Flowing |
| Docs launch, navigation and feasibility report | Validated deployment properties and canonical Markdown → staged Eleventy sources → real built pages and prefixed links. Both local Geist fonts and licenses come from locked packages. | Flowing |
| Storybook state and control variants | Story-supplied HTTP and storage fixtures drive the same page and UI primitives. The ordinary app and integrated smoke independently use the real BFF. | Flowing |

## Behavioral Spot-Checks and Probe Execution

| Check | Observed result | Status |
| --- | --- | --- |
| Managed Node `--test --test-name-pattern='rejects a successful status other than HTTP 200' test/generated-client.test.ts` | Independently ran one matching test. One pass and zero failures. | Pass |
| `python3 tools/style/test_hook.py HookTest.test_competing_index_writer_keeps_its_update` | Independently ran under the GSD timeout. The concurrent index update and worktree were preserved. | Pass |
| `python3 tools/doctor.py --self-test`, `python3 tools/check_pr_workflow.py`, and `actionlint .github/workflows/build.yml` | Independently ran. Six doctor tests passed. The workflow checker rejected write permissions and an unpinned action, then accepted the regular workflow. actionlint emitted no diagnostics. | Pass |
| Hook syntax, original Phase 1 specimen and rendered handoff | Independently ran `sh -n`, original Git-byte comparison, staged Markdown `cmp` and rendered-anchor check. All passed. | Pass |
| `python3 tools/test_phase2_build.py` with refused Docker, run by the orchestrator | All three tracked-source checks passed. Observed seven JVM cases, five stable npm locks, nine docs files, byte-identical client restoration, documented quick start, rejection of an injected opt-in edge and preservation of hook worktree bytes. | Pass |
| `:web:shellSmoke`, `:docs-site:check`, `:web:siteSmoke` and `:web:storyTest`, run by the orchestrator | Passed 18 shell checks, 14 docs assertions, the live app/docs journey with both local fonts, and 13 axe-enabled stories. The shell includes stalled successful response-body recovery. | Pass |
| `python3 web/test/client-graph.py --clean`, `:web:verifyClientGraph` and `:web:webCheck` | Retained direct Gradle/TAP output shows clean success, contract-reference and typecheck negative controls, recovered assets and 19 passing client checks. | Pass |
| `:web:foundationProof` | Retained direct output confirms rejection of the boundary violation and unnamed button, followed by passing restored variants. | Pass |
| `python3 tools/check_kotlin_quality.py format-comments` and `publication` | The current style and quality checks passed under orchestrator testing. Retained control output shows the deliberate comment and publication failures and repaired positive runs. Both current Dokka sites exist. | Pass |
| Current JUnit XML and Phase 1 non-Docker regression | BFF unit and component XML and Phase 1 smoke, Kotest and TypeID JVM XML have no failures or skips. The orchestrator also exercised the TypeID exchange, frontend assets and two-pass KDoc. | Pass |
| Phase 1 integration and native packaging | Native ARM64 runs passed at `f879e15` and again after UAT at `aa577c5`. The four retained JVM reports for the latter contain six passes with zero failures, errors or skips. The captured trace and cleanup report confirm stale-append rejection and disposal of owned resources. The TypeScript exchange, two-pass KDoc and both Paketo variants also passed. Phase 7 owns the first hosted AMD64 DCB runtime proof. [Native follow-up](02-VALIDATION.md#native-phase-01-follow-up) | Pass |

Phase 2 probes use Python and Gradle entry points. No conventional or named `probe-*.sh` was declared. Retained direct runner results were inspected where available alongside the new local checks and build artifacts.

### Test Quality Audit

The linked suites have active contract, state and failure assertions. The JUnit XML shows no skips. A separate validator checks actual HTTP bodies using the checked-in contract and separately specified expected roles. Browser tests assert focus, retry, order, routes and visible output. Git tests compare exact bytes and modes after real operations. Repeated generation checks determinism, and explicit contract mutations verify independent consumer invalidation.

## Requirements Coverage

| Requirement | Plans | Status | Evidence |
| --- | --- | --- | --- |
| FND-02 | 01, 05, 07, 08, 09 | Satisfied | Wrapper, catalog, JDK and Node pins, scoped npm metadata and locks, mise and workflow pins align with the inventory. Doctor observed the actual Temurin 25.0.5.1+2-LTS worker and required tools. The follow-up confirms the exact Python patch and workflow lint pins. |
| FND-05 | 02 | Satisfied | Gradle JVM suites run Jupiter with Kotest assertions and properties. Both BFF suites resolve the shared fixture variant and production excludes test tools. |
| FND-06 | 01, 04, 09, 10 | Satisfied | Clean Gradle build emits web, docs and Storybook. The BFF contract is explicitly consumed before frontend checks and output. |
| CQRS-04 | 01, 02, 03, 09, 10 | Satisfied at Phase 2 scope (D-04) | The implemented GET directory is contract-first, served exactly, independently validated and consumed through its generated client. Full browser command, read and live operation coverage remains pending with the later slices, starting in Phase 3. |
| UI-01 | 03, 04, 06, 09, 11 | Foundation and manual checks verified | Approved UI-SPEC, production components, Steiger and its negative control, required Storybook states and axe checks. The maintainer accepted the three native and assistive checks in UAT. |
| UI-03 | 01, 03, 06, 09, 11 | Implemented behavior verified | Real browser selection of all three roles, tab independence, reload, validated fallback and retry. |
| QA-07 | 02, 05, 07, 09 | Satisfied | ktfmt semantics and two-pass proof, detekt negative witness, and both Dokka warning failures and repairs. The Phase 1 specimen is preserved. |
| QA-08 | 05, 07, 09 | Local implementation verified, hosted evidence pending | Shared staged and full-tree policy, real Git controls, validated PR workflow, workflow lint with ShellCheck and local clean build. The traceability row stays pending until the matching hosted job passes. |
| DOC-06 | 04, 08, 09 | Satisfied | Reconciled public B17/B8 provenance, public selected-graph reproduction, explicit incomplete B8 status and verified publication boundaries. |

All nine Phase 2 IDs occur in at least one plan. No orphaned requirements were found.

### Decision Coverage

GSD reported 15/15 trackable decisions honored. The shipped paths support the D-04 contract extension boundary and D-15 Phase 7 handoff.

### Anti-Patterns and Review Follow-Up

No unreferenced `TBD`, `FIXME` or `XXX` markers or disabled requirement-linked tests were found in the changed implementation. The fixed demo catalog and isolated story data serve their declared use cases. The reviewed corrections are present for index-only publication, path-limited commits, shell literal whitespace, partial-response deadlines, prefixed preview, malformed Node pins and comma-bearing detekt paths. The docs ship both Geist assets and licenses. Wide named docs regions support keyboard scrolling. The review accepted explicit sequential focus for those regions across widths.

### Targeted Re-verification After Quick Task 261126-fhh

On 2026-11-26, the stale fingerprint named `mise.toml` and `docs/maintainer-guide.md`. The diff in `d92322e` affects FND-02 and the maintainer setup instructions. The scope covered runtime selection, the CI entry points and rendered docs.

| Check | Observed evidence |
| --- | --- |
| Authoritative version files | `mise ls --current` showed Java feature `25` from `.java-version`, exact Node.js `26.13.1` from `.nvmrc`, and Pack, Ruff and Taplo from `mise.toml`. A disposable copy with conflicting `.sdkmanrc`, `.node-version` and `package.json` files selected the same owners. The documented `mise exec java node` commands reported Temurin build `25.0.5.1+2-LTS` and Node.js `v26.13.1`. |
| CI and Gradle runtime selection | The pinned CI setup action reads `.java-version` with `distribution: temurin`. At that revision, the workflow installed only Ruff and Taplo with mise, and an empty mise install directory produced no `JAVA_HOME` export. The JVM convention uses `.java-version` and `JvmVendorSpec.ADOPTIUM`. The Gradle Node consumers download from `.nvmrc` and select npm from their `packageManager` entries. `python3 tools/check_pr_workflow.py` accepted the reviewed workflow and rejected both negative controls. |
| Published maintainer guide | `cmp` confirmed the staged guide is byte-identical to the canonical Markdown. The rendered maintainer guide includes the trust and install commands, the runtime source and version checks, Gradle launcher inspection and the scoped style command. The [quick task results](../../quick/261126-fhh-document-mise-and-enable-canonical-java-/261126-fhh-SUMMARY.md#verification) record a passing `styleCheck`, `doctor` and all 14 `docsCheck` tests. |

FND-02 and roadmap criterion 4 remain verified. This re-verification used targeted checks and the quick task's build results. The phase score and acceptance checkpoints carry forward from the initial verification. Hosted execution remains a ship checkpoint.

### Targeted Re-verification After Qodana and Quick Task 261126-fxn

The stale status at `9af7b3f` identified six changed paths. The review checked the PR workflow, maintainer guide, Gradle catalog, mise configuration, workflow guard and doctor. It also covered the new `tools/qodana-scan.sh` entry point.

| Check | Observed evidence |
| --- | --- |
| Tool ownership and doctor | `mise.toml` owns Python `3.15.2`, actionlint `1.7.12` and ShellCheck `0.11.0`. Both doctor modes use the same exact-Python comparison. Two independently run named tests passed for same-minor patch drift and informational GSD path precedence. |
| PR workflow and guide | The workflow retains read-only permissions, pinned actions and Temurin selection from `.java-version`. Its mise allowlist installs the five CI tools. The actionlint command with ShellCheck passed independently. The workflow guard accepted the reviewed workflow and rejected write permission, unpinned checkout and disabled ShellCheck. The staged guide matched its source bytes and the rendered guide included the lint and Qodana commands. [Quick task results](../../quick/261126-fxn-pin-python-for-local-tooling-and-the-pr-/261126-fxn-SUMMARY.md#verification) record the passing style, doctor, hook and docs checks. |
| Opt-in Qodana runner | Shell syntax and ShellCheck passed independently. The script archives the selected revision, reads its `.java-version`, supplies Linux Temurin to the catalog-pinned Qodana image, and stores reports under the ignored `.gradle/qodana/runs/` path. The retained `e765a30` outputs contain HTML and a SARIF report with 61 results. The runner is invoked through the documented opt-in command. [Local Qodana evidence](02-VALIDATION.md#local-qodana-follow-up) |

FND-02 and the local checks for QA-08 remain verified. The hosted QA-08 check still needs a matching `build-and-style` run.

### Re-verification After UAT

The current source review covered the ten changed implementation and maintainer-guide paths from `393ae8c` to `3d0ea45`. The BFF, frontend, docs renderer and docs publication verifier are byte-identical across that range. The previous runtime evidence therefore still applies to those inputs. The Gradle changes preserve lazy `Provider<JavaLauncher>` resolution in both conventions and retain the ordered article, template and font allowlist in `stageDocs`. The changed guide is part of those staged public inputs.

| Check | Observed evidence |
| --- | --- |
| Clean current build and style | In a disposable checkout of `3d0ea45`, `DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain styleCheck clean build --no-build-cache` passed in 1m37s with the managed tools. Generation preceded typecheck and Vite bundling. The executable BFF JAR, generated TypeScript, Vite and Storybook entry pages, and nine documentation files exist. All 19 client checks, 14 docs checks and seven JVM cases passed. Steiger, ktfmt, detekt and the Dokka publications passed. The staged canonical guide and feasibility report match the checkout. The executed task log omits the Docker, packaging and browser suites. |
| Disposable Git and toolchain controls | The named competing-index-writer test passed after the clean build. The doctor self-tests passed using the pinned Python. |
| Workflow, style runner and scanner syntax | `tools/check_pr_workflow.py` accepted the current job and rejected write permissions, an unpinned checkout and disabled ShellCheck. Managed actionlint with ShellCheck, managed ShellCheck on `tools/qodana-scan.sh`, `sh -n` and `git diff --check 393ae8c..HEAD` passed. |
| Native Phase 1 regression | The verifier inspected the retained post-UAT JUnit XML, DCB trace, cleanup record, TypeID outputs, formatted KDoc and native packaging artifacts. The probe, Gradle build conventions and JDK and Node version files are unchanged from the tested revision `aa577c5`. [Native Phase 1 follow-up](02-VALIDATION.md#native-phase-01-follow-up) |
| Qodana and editor configuration | The current archive contains `qodana.yaml` and the Spring entry-point XML. The launcher keys plugin files by the YAML blob, installs the XML in the archive's `.idea/misc.xml` and keys analysis by the XML blob. The retained paired runs identify four Axon handlers and three existing Spring factories plus a genuine Spring control. An unannotated control and the lookalike `Bean` remain reportable. Native IntelliJ results show Gradle incubation diagnostics falling from 97 to zero while preserving both Guava `@Beta` diagnostics. The checked-in IDE profile applies on project open and the current archive omits it. [Axon control](../../quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md), [Spring control](../../quick/261126-jp0-recognize-spring-bean-entry-points-in-qo/261126-jp0-SUMMARY.md), [IDE and archive control](../../quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md) |

### Open Review Findings

| Finding | Scope and observed failure | Owner |
| --- | --- | --- |
| CR-04 · Critical | The optional historical Qodana scan can suppress Gradle diagnostics. `git archive e434f25` contains the editor profile. Its retained SARIF reports successful `recommended` analysis with zero findings. After the cached profile was removed, `fff0b35` reported 51 `UnstableApiUsage` findings. Both revisions and the current head select analysis cache `3c9deeb0d85d54bdd7d3a968093dc2545359c330`. The saved cache profile matches the historical profile byte for byte. The runner relies on revision-local archive attributes. This finding blocks reliable historical scanning and sits outside the Phase 2 must-have score. [Incremental review](02-REVIEW.md#cr-04-historical-qodana-scans-silently-use-the-editor-profile-and-can-contaminate-later-scans), [open disposition](02-REVIEW-DISPOSITION.md) | Inspection tooling owner. Exclude the editor profile when preparing every scan and version the analysis cache. Verify historical, current and historical scans against the same cache. |
| Slice WR-01 · Warning | An invalid `VITE_DOCS_BASE` can build successfully and throw before React mounts. Both documented deployment bases passed the live journey. [Reproduction](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md#wr-01-an-invalid-documentation-base-can-prevent-the-entire-app-from-mounting) | Web build owner. |
| Slice WR-02 · Warning | A whitespace-only student label passes the published schema and becomes a blank selectable option. The adapter rejects duplicate IDs, and the published contract leaves that invariant undocumented. The fixed live directory returns its expected labels and distinct IDs. [Reproduction](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md#wr-02-the-published-directory-contract-admits-blank-options-and-omits-its-id-uniqueness-rule) | BFF and web owners before contract expansion. |
| Slice WR-03 · Warning | Multiple published command samples under one heading share an accessible landmark name. The accepted UAT covers named regions and their keyboard scrolling. [Reproduction](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md#wr-03-published-command-samples-share-indistinguishable-landmark-names) | Documentation and accessibility owners. |
| Slice WR-04 · Warning | Root publication misses a broken raw HTML link with whitespace around `=`. Prefixed output normalizes the attribute and the same control fails there. The current positive navigation and prefixed negative control passed. [Reproduction](../../quick/261126-g7q-reassess-the-tooling-built-in-phases-1-a/261126-g7q-SLICE-REVIEW.md#wr-04-the-root-publication-check-misses-valid-html-links) | Documentation build owner. |

## Manual Acceptance

The maintainer accepted all seven UAT items at `3779fa2`, covering the native selector and forced colors, screen-reader announcements, actual 200% text zoom, the demo role and private advisory boundaries, the Phase 1 handoff and the four test-tier controls. The UAT record has zero pending or blocked rows. [Completed UAT](02-UAT.md)

## Hosted Evidence at Ship

The local remote-tracking refs contain `origin/main` and the Phase 1 branch. The available evidence contains no hosted Phase 2 job for the reviewed head. After the authorized ship lifecycle pushes the branch and opens the PR, the ship owner runs `gh pr checks --watch` and inspects the matching run with `gh run view <run-id>`. Before merge, record the run link, matched head SHA or PR merge mapping, runner architecture, and successful wrapper validation, actionlint with ShellCheck, `styleCheck` and `clean build --no-build-cache`. Changes to the reviewed head require a matching new run.

## Gaps Summary

The matching hosted PR job is the sole remaining uncertain must-have. The private B8 scan is incomplete pending authorized inputs. The first hosted AMD64 DCB runtime proof belongs to Phase 7.

_Initially verified 2026-11-25T17:10:17Z by gsd-verifier._
_Targeted re-verification completed 2026-11-26T04:20:12Z by gsd-verifier._
_Tooling and UAT follow-up verified 2026-11-26T04:42:31Z by gsd-verifier._
_Post-UAT re-verification completed 2026-11-26T08:28:58Z by gsd-verifier._
