---
phase: 02-build-and-ui-foundations
verified: 2026-11-26T09:37:20Z
status: passed
score: 30/30 local must-haves verified
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
covered_digest: "v4:sha256:875d6411a91237671c8beecfc45b9eb8873513c071c80c93acff52839363dc4d"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 30/31
  gaps_closed:
    - "The maintainer accepted all seven UAT checks, including the four test-tier guarantees."
    - "The final source corrections passed their regression checks and close the remaining code review findings."
  gaps_remaining: []
  regressions: []
decision_coverage:
  honored: 15
  total: 15
  not_honored: []
---

# Phase 02 Build and UI Foundations Verification

**Phase goal** — As a maintainer, I want to build and test the demo shell and generated BFF client through shared conventions, so that I can verify later feature slices from a clean checkout.

**Verdict** — `passed` · 30/30 local must-haves verified · reviewed source `1ca7bf947420172fcfb24b52e85b227d89de8410`

The final clean checkout produced the generated client, browser shell, Storybook, and documentation site through the shared build. The live browser checks passed and the maintainer accepted all seven UAT items. The hosted `build-and-style` job passed for the reviewed source. Plan 02-09 requires a matching successful job on the current PR head at merge. [02-09 plan](02-09-PLAN.md) · [Completed UAT](02-UAT.md) · [Hosted evidence](#hosted-evidence-at-ship)

## User Flow Coverage

| Maintainer step | Expected outcome | Observed evidence | Status |
| --- | --- | --- | --- |
| Start from tracked files and check the required tools. | The documented owners and doctor identify the versions, sources and repairs. | The Gradle report resolved the launcher, BFF worker and managed Node/npm tools. Docker connectivity and architecture appeared under additional checks. | Verified |
| Build the project. | The contract generates the client before frontend compilation and the shared checks run. | A clean clone of the reviewed source ran `clean build --no-build-cache` with Docker refused. The log shows producer order and the generated client, app, Storybook, nine docs files and JVM reports are present. The earlier tracked-only harness independently checked byte-identical recovery. | Verified |
| Open the documented app and docs paths. | The BFF feeds the role switcher and the docs remain reachable. | Chromium on the reviewed source exercised both documentation launch modes at `/courses/`, independent role selections, and a live BFF outage and recovery. | Verified |
| Extend the contract and run the shared checks. | Contract changes invalidate consumers, and the hook and CI use the same style policy. | A disposable operation rename regenerated the client, failed the unchanged frontend consumer at typecheck and prevented bundling. The hook and tracked-tree checker both use `tools/style/run.py`. | Verified locally |

## Goal Achievement

### Roadmap Success Criteria

| # | Observable truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | A clean `./gradlew build` builds the documentation site and generates the frontend client from the BFF OpenAPI contract before building the frontend. | Verified | Root `assemble` reaches BFF, web and docs. The BFF's `openApiElements` variant carries one local file, and `generateClient → typecheck → webBuild` is enforced. The clean harness exercised those tasks and output recovery. |
| 2 | A reader can open the React shell and switch between admin and individual demo students. Shared components and loading, empty, and error states are inspectable in Storybook. | Verified | Loopback Chromium reached both students and Administrator. Static Storybook renders the production page and primitives. All 13 Chromium stories passed with axe. |
| 3 | The initial UI-SPEC documents the design foundation, the frontend passes Steiger checks, and the contract gives feature slices an entry point for browser commands, reads, and live views. | Verified for D-04 | The UI-SPEC specifies the design and states. Steiger passed and rejected a deliberate cross-layer import. The live demo operation, generator and Maintainer Guide establish the extension path. Phase 3 adds the first application commands, reads and streams. |
| 4 | A maintainer can run `doctor`, audit authoritative version owners, and run JUnit 6 and Kotest through Gradle JVM Test Suites with shared Java Test Fixtures. The documented dependency maintenance process links recovered or reproduced evidence and keeps advisory inputs and results private. | Verified | Gradle doctor reported managed tools and build tiers. The final JVM reports record nine BFF unit cases and six loopback component cases. The Phase 1 regression covers Jupiter and Kotest. Fixture isolation checks all four consumer classpaths. The public guide reconciles historical records and documents a private opt-in B8 procedure. |
| 5 | The pre-commit hook and CI use the same repository formatting and style checks. Representative Kotlin and KDoc pass ktfmt and detekt, and a Dokka warning fails the build. | Verified locally | Staged hook and tracked style use the same driver and policy. All 14 real hook fixtures passed. The ktfmt and detekt controls failed at their intended gates. Dokka emitted one warning per undocumented witness and failed each publication, then passed with the KDoc repaired. |

### Plan Must-Haves

| # | Plan | Observable truth | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | 02-01 | Administrator, Maya Chen and Alex Rivera are selectable from the live BFF directory. | Verified | The real browser tracer checks the request, the exact option order and chosen value against the executable BFF JAR. |
| 2 | 02-02 | One command runs JUnit 6 unit and Docker-free HTTP component suites, both using the published Java Test Fixtures variant. | Verified | The `courses.jvm` convention selects Jupiter and an actual Temurin worker. Both BFF suites consume `testFixtures(project(":fixtures"))`. `verifyFixtureIsolation` checks all four variant consumers and production runtime exclusions. |
| 3 | 02-02 | Independent HTTP schema validation rejects malformed responses and the served contract matches its source. | Verified | Six active `DirectoryHttpTest` cases passed. An independent validator selects the schema by path, method, status and media type. Controls reject a missing Administrator, an external reference and whitespace-only role fields. Packaged and served contract bytes match the source. |
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
| 16 | 02-06 | Options retain complete names. A clipped selected value appears in full below the control. Long labels, links, headings and status wrap. | Verified | The production component measures clipping across font and size changes. The long-name story and Chromium responsive test check the full wrapping value. Chromium also exercises the docs regions' unique contextual names, tab order and scrolling. |
| 17 | 02-07 | Empty staged input is a no-op. Adjacent staged and unstaged edits remain distinct and overlaps preserve exact unstaged bytes. | Verified | Real Git fixtures assert index and worktree bytes, mode and overlap behavior. Publication affects the candidate index. |
| 18 | 02-07 | Format precedes lint on the candidate, and a rerun preserves bytes, modes and unaffected worktree content. | Verified | Candidate-config detekt and repeated-hook fixtures observe the formatting order and compare original and resulting Git and worktree state. |
| 19 | 02-07 | A competing writer, lock or formatter failure preserves staged and unstaged work. | Verified | The hook opens an exclusive lock and compares original index bytes before publishing. Independent concurrent-writer, existing-lock and failing-tool checks demonstrate preservation. |
| 20 | 02-08 | Doctor reports declared and observed versions, provenance, required tier and repair. Optional infrastructure failure allows a regular build. | Verified | The current eight-test run passed. Independent spot-checks confirmed exact Python patch rejection in both modes and informational GSD detection. The Gradle doctor report passed all required rows with refused Docker, and the same Docker setting allowed a clean build. |
| 21 | 02-08 | The public guide identifies actual selections, controls and missing records, and leaves B8 incomplete. | Verified | The public dependency runner checks selected Gradle graphs and pinned metadata. The guide cites unavailable historical paths and records the private scope and incomplete status. |
| 22 | 02-09 | An ordinary clean build regenerates the client and builds the app, Storybook and docs with infrastructure unavailable. | Verified | The final clone passed with Docker refused. The earlier tracked-only harness also demonstrated byte-identical recovery, public startup, lock stability and detection of an injected opt-in edge. |
| 23 | 02-10 | Generation uses the contract and managed tools, restores deleted output and invalidates consumers after changes. | Verified | The direct runner observed generation alone, an unchanged run `UP-TO-DATE`, byte-identical recovery, rejection of an external schema reference and a changed operation export that triggers `TS2305` before bundling. Current invalidation controls also verify Vite revalidation after inherited dotenv changes and bundle reuse with the default configuration. |
| 24 | 02-10 | The generated operation rejects malformed successful responses before exposing persona data. | Verified | All 32 client checks passed. Generated Zod schemas reject missing fields, blank or empty strings and wrong discriminators. The adapter rejects duplicate IDs, undocumented status or media and redirects. OpenAPI describes case-sensitive ID uniqueness, and the BFF enforces it against an immutable student snapshot. |
| 25 | 02-11 | Storybook publishes production role states and retries. Steiger and axe reject controlled violations. | Verified | The final clone built Storybook and ran Steiger. The retained proof shows 13 stories against real page and control implementations. Deliberate changes trigger `fsd/forbidden-imports` and `button-name`, and repair restores passing results. |

The score covers the five roadmap criteria and 25 local plan truths. The remaining Plan 02-09 truth, successful hosted execution for the reviewed PR revision, applies at [ship and merge acceptance](#hosted-evidence-at-ship).

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
| 02-04 | `docs-site/build.gradle.kts`, `docs/feasibility/phase-01.md`, `docs/quick-start.md` | `stageDocs` copies allowlisted public sources and compares canonical bytes. Eleventy invokes the parse5-based verifier on disk output. `docsCheck` exercises both deployment bases, active links and fragments, preview path keys, contextual region names, the output allowlist and synthetic private-data exclusion. |
| 02-05 | `courses.kotlin-quality.gradle.kts`, `config/detekt/comments.yml`, `tools/check_kotlin_quality.py` | The production convention passes comments rules to isolated detekt and wires ktfmt, detekt and Dokka into `check`. The quality script invokes the same tasks on disposable witnesses. |
| 02-06 | `web/src/shared/ui/native-select.tsx`, `web/src/app/theme.css` | The home page renders the labelled native select through the shared barrel. The runtime imports the theme with local fonts, focus and wrap behavior. |
| 02-07 | `.githooks/pre-commit`, `tools/style/policy.json`, `tools/style/test_hook.py` | The hook uses `run.py --staged`; root Gradle uses `run.py --check`. The real Git fixtures invoke that hook on disposable candidates. |
| 02-08 | `tools/doctor.py`, `docs/maintainer-guide.md` | Root Gradle supplies actual tool and worker observations. The guide links the canonical Phase 1 evidence and is rendered through the allowlist. |
| 02-09 | `.github/workflows/build.yml`, `tools/test_phase2_build.py`, `web/test/site-smoke.mjs` | The PR job reaches the actual Gradle tasks. The Python harness reproduces the documented startup from tracked sources. `siteSmoke` serves staged docs and the executable BFF on loopback. |
| 02-10 | `build.gradle.kts`, `web/test/client-graph.py`, `web/test/generated-client.test.ts` | Root assembly selects the ordered web tasks. Both production and boundary tests import the same generated-client adapter. The disposable graph runner proves contract regeneration and Vite invalidation. |
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
| QA-08 | 05, 07, 09 | Satisfied | Shared staged and full-tree policy, real Git controls, workflow lint with ShellCheck and clean build passed locally and the matching hosted job passed for the reviewed source. [Hosted evidence](#hosted-evidence-at-ship) |
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

FND-02 and the local checks for QA-08 remained verified at this checkpoint. The later hosted QA-08 result is recorded below.

### Re-verification After UAT

The current source review covered the ten changed implementation and maintainer-guide paths from `393ae8c` to `3d0ea45`. The BFF, frontend, docs renderer and docs publication verifier are byte-identical across that range. The previous runtime evidence therefore still applies to those inputs. The Gradle changes preserve lazy `Provider<JavaLauncher>` resolution in both conventions and retain the ordered article, template and font allowlist in `stageDocs`. The changed guide is part of those staged public inputs.

| Check | Observed evidence |
| --- | --- |
| Clean current build and style | In a disposable checkout of `3d0ea45`, `DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain styleCheck clean build --no-build-cache` passed in 1m37s with the managed tools. Generation preceded typecheck and Vite bundling. The executable BFF JAR, generated TypeScript, Vite and Storybook entry pages, and nine documentation files exist. All 19 client checks, 14 docs checks and seven JVM cases passed. Steiger, ktfmt, detekt and the Dokka publications passed. The staged canonical guide and feasibility report match the checkout. The executed task log omits the Docker, packaging and browser suites. |
| Disposable Git and toolchain controls | The named competing-index-writer test passed after the clean build. The doctor self-tests passed using the pinned Python. |
| Workflow, style runner and scanner syntax | `tools/check_pr_workflow.py` accepted the current job and rejected write permissions, an unpinned checkout and disabled ShellCheck. Managed actionlint with ShellCheck, managed ShellCheck on `tools/qodana-scan.sh`, `sh -n` and `git diff --check 393ae8c..HEAD` passed. |
| Native Phase 1 regression | The verifier inspected the retained post-UAT JUnit XML, DCB trace, cleanup record, TypeID outputs, formatted KDoc and native packaging artifacts. The probe, Gradle build conventions and JDK and Node version files are unchanged from the tested revision `aa577c5`. [Native Phase 1 follow-up](02-VALIDATION.md#native-phase-01-follow-up) |
| Qodana and editor configuration | The current archive contains `qodana.yaml` and the Spring entry-point XML. The launcher keys plugin files by the YAML blob, installs the XML in the archive's `.idea/misc.xml` and keys analysis by the XML blob. The retained paired runs identify four Axon handlers and three existing Spring factories plus a genuine Spring control. An unannotated control and the lookalike `Bean` remain reportable. Native IntelliJ results show Gradle incubation diagnostics falling from 97 to zero while preserving both Guava `@Beta` diagnostics. The checked-in IDE profile applies on project open and the current archive omits it. [Axon control](../../quick/261126-ink-qualify-axon-and-spring-inspection-suppo/261126-ink-SUMMARY.md), [Spring control](../../quick/261126-jp0-recognize-spring-bean-entry-points-in-qo/261126-jp0-SUMMARY.md), [IDE and archive control](../../quick/261126-jsl-reduce-intentional-gradle-incubation-noi/261126-jsl-SUMMARY.md) |

### Final Pre-Ship Re-verification

The clean test checkout identifies its source as `1ca7bf947420172fcfb24b52e85b227d89de8410`. The candidate differs only in planning records. The verifier inspected the current source changes, task log, JUnit XML, generated output and retained targeted regression evidence.

| Check | Observed evidence | Result |
| --- | --- | --- |
| Final clean build | The isolated clone passed `styleCheck` and `clean build --no-build-cache` with `DOCKER_HOST=tcp://127.0.0.1:1`. The log orders `:web:generateClient`, `:web:typecheck` and `:web:webBuild`. It records Steiger, ktfmt, detekt, both Dokka publications and fixture isolation. No Docker, packaging or infrastructure test task ran. The build produced the executable BFF JAR, generated client and schemas, Vite and Storybook entry pages, and all nine public docs files. Staged feasibility and maintainer Markdown match their sources. The nine public files are byte-identical to the independently built `c967802` output. Local log `/private/tmp/phase02-verified.0JVmk1/local-checks.log`. | Pass |
| Counts on the final source | The clean-build log records 44 docs and 32 generated-client tests. The BFF XML records 9 unit and 6 HTTP component tests with zero failures, skips or errors. The final `:web:siteSmoke` and `:web:shellSmoke` runs passed 1 live journey and 19 shell scenarios, including stalled response recovery, invalid directory responses, and cancellation of a stale request. | Pass |
| Named generated-client test | The managed Node runner selected `the generated schema rejects student label containing only zero-width no-break space` in the final clone. It passed with zero failures. | Pass |
| Workflow controls and source checks | The current workflow checker independently accepted the configured job and rejected write permissions, an unpinned checkout and disabled ShellCheck. actionlint 1.7.12 with ShellCheck 0.11.0, the launcher ShellCheck and syntax check, and the source-range Git whitespace check passed. | Pass |
| Phase 1 native regression | At `cca11b1248b4f1c6b64aab557c98afa1173fc46b`, Docker 29.10.0 `linux/arm64` ran the opt-in checks. The retained command selected `:probe:test`, `:probe:kotestProbe`, `:probe:typeIdProbe`, `:probe:kdocProbe`, `:probe:integrationTest` and `:probe:frontendImageProbe` with `--rerun-tasks`. The root log `.gradle/phase02-ship/regression.log` records build success. The four JVM XML reports contain six passing cases with zero failures, errors or skips. Git confirms that probe sources, build conventions, version owners and Gradle inputs match the reviewed source. The retained Phase 1 evidence also covers TypeID exchange, KDoc idempotence, and both native Paketo variants. [Validation record](02-VALIDATION.md#native-phase-01-follow-up) | Pass |

### Review Disposition

The final review of `1ca7bf9` is clean. The Phase 02 ledger has zero open findings out of 13. The related application slice reproductions also have fixes verified in real build or browser paths. No new unreferenced debt markers or disabled requirement-linked tests appeared in the changed sources. [Final review](02-REVIEW.md) · [Disposition ledger](02-REVIEW-DISPOSITION.md)

| Correction | Current evidence |
| --- | --- |
| Historical Qodana scanning | The launcher excludes the editor profile before building the historical Git snapshot and selects the new analysis namespace using the Spring XML blob or the no-entry-points key. The verifier checked the unchanged launcher inputs and read all three retained successful SARIF runs. Their 52, 51 and 51 Gradle findings include the 51 reference diagnostics on one cache. The Spring and Axon entry-point controls and the existing editor configuration remain documented in the independent task verification. [Quick task summary](../../quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-SUMMARY.md) · [Independent verification](../../quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-VERIFICATION.md) |
| Demo shell and directory | Vite validates the resolved docs URL before bundling or dev startup. The live process configuration takes precedence and an explicitly empty value fails. OpenAPI, the independent HTTP validator, the Kotlin model and the generated Zod schemas agree on which role strings are blank. Both sides enforce case-sensitive uniqueness and the server preserves student order after validation. Final Java, Node and Chromium cases exercise the new code. [Shell and directory evidence](../../quick/261126-lmn-reject-invalid-demo-shell-settings-and-r/261126-lmn-SUMMARY.md) |
| Docs markup and landmarks | Both deployment bases reject missing raw anchor, image and Markdown destinations. The 26 code and table regions in the three published articles have distinct contextual names within each article. The live site test asserts names, keyboard focus, and scrolling. [Publication and landmark evidence](../../quick/261126-lmx-validate-rendered-docs-links-and-disting/261126-lmx-SUMMARY.md) |
| Preview paths and fragment targets | The publication check uses the preview's exact pathname keys and rejects active HTML base overrides, inert template targets and encoded path aliases. Tests cover both bases, live IDs, the explicit HTML route alias, encoded fragment characters and query parameters. [Preview and fragment evidence](../../quick/261126-mcu-match-published-link-verification-to-bro/261126-mcu-SUMMARY.md) |
| Gradle invalidation | Production dotenv files make Gradle rerun Vite so inherited configuration changes reach the bundle or the validation failure. The targeted regression also verifies default bundle reuse. The strict optional configuration-cache run still encounters the pre-existing npm task serialization issue. [Invalidation evidence](../../quick/261126-mdh-invalidate-the-vite-build-when-dotenv-ex/261126-mdh-SUMMARY.md) |
| Active HTML parsing | Eleventy calls the pinned parse5 verifier after publishing. At both bases the 44 docs tests cover textarea strings, active and empty base elements, inert templates, named HTML anchors, live SVG IDs, the private fixture and the nine-file inventory. Chromium independently observed the exact literal textarea value and zero active base or text-only ID matches. [Parser evidence](../../quick/261126-mq2-use-browser-conforming-html-parsing-for-/261126-mq2-SUMMARY.md) |

### Advisory (New Scope, Unevidenced)

None.

## Manual Acceptance

The maintainer accepted all seven UAT items at `3779fa2`, covering the native selector and forced colors, screen-reader announcements, actual 200% text zoom, the demo role and private advisory boundaries, the Phase 1 handoff and the four test-tier controls. The UAT record has zero pending or blocked rows. [Completed UAT](02-UAT.md)

The ASVS Level 1 security audit records zero open threats. The pre-ship validation recorded the local outcome and the separate hosted acceptance condition. [Security audit](02-SECURITY.md) · [Validation](02-VALIDATION.md) · [UI review](02-UI-REVIEW.md)

## Hosted Evidence at Ship

On 2026-11-26, the SHA-pinned, read-only `build-and-style` job passed in 4m49s for [PR #2](https://github.com/aanbrn/axon5-dcb-courses-codex/pull/2). GitHub Actions reported event `pull_request` and head `013d29c170f3da98a78797a92039ebb410771da2`. Checkout fetched and reported test merge `39c39b3f0c8f331ce1423cd356bb7faaaf9bf6a3`. The GitHub commit API confirmed its parents as base `44589a41ea50672fb86554742b5b41c5a0cf0b45` and that PR head. The job ran on `ubuntu-24.04`, with `uname -sm` reporting `Linux x86_64`. [Run 45795044228](https://github.com/aanbrn/axon5-dcb-courses-codex/actions/runs/45795044228)

Gradle wrapper validation, actionlint with ShellCheck, `styleCheck` and `clean build --no-build-cache` all passed. Gradle reported 2m51s for style and 1m34s for the clean build. This run verifies the reviewed source and closes QA-08. Before merge, verify a successful run for the current head or its corresponding test merge. The PR verification checklist records the latest run and mapping after planning-only commits. [Plan 02-09](02-09-PLAN.md) · [Job 139823423852](https://github.com/aanbrn/axon5-dcb-courses-codex/actions/runs/45795044228/job/139823423852)

## Gaps Summary

All local must-haves are verified, and the hosted PR job passed for the reviewed source. Plan 02-09 requires a matching successful job for the head used at merge. Private B8 remains incomplete within its documented Maven inventory and advisory-feed scope, pending an authorized feed, scanner and inputs. The first hosted AMD64 DCB runtime proof belongs to Phase 7. [Private review scope](../../../docs/maintainer-guide.md#private-jvm-advisory-procedure-b8) · [Phase 7 handoff](../../../docs/feasibility/phase-01.md#hosted-amd64-verification-and-retirement)

_Initially verified 2026-11-25T17:10:17Z by gsd-verifier._
_Targeted re-verification completed 2026-11-26T04:20:12Z by gsd-verifier._
_Tooling and UAT follow-up verified 2026-11-26T04:42:31Z by gsd-verifier._
_Post-UAT re-verification completed 2026-11-26T08:28:58Z by gsd-verifier._
_Final pre-ship re-verification completed 2026-11-26T09:37:20Z by gsd-verifier._
