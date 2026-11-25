---
phase: 02-build-and-ui-foundations
verified: 2026-11-25T17:10:17Z
status: human_needed
score: 29/31 must-haves verified
covered_files: [
  ".githooks/pre-commit",
  ".github/workflows/build.yml",
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
  ".planning/phases/02-build-and-ui-foundations/02-UI-SPEC.md",
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
  "settings.gradle.kts",
  "tools/check_kotlin_quality.py",
  "tools/check_pr_workflow.py",
  "tools/doctor.py",
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
covered_digest: "v4:sha256:bfe1405eae3a3da7a5dad304afb8cd7c89e9d1b2b9b8483914460fb68fb7429d"
behavior_unverified: 0
overrides_applied: 0
decision_coverage:
  honored: 15
  total: 15
  not_honored: []
human_verification:
  - test: "Native role selector and forced colors. In the running shell use Tab and Shift+Tab to reach Demo role. Open the native list with the platform shortcut, move through the options with arrows, select a student, then reopen it and close it with Escape. Repeat in a platform-supported forced-colors mode. Record browser, OS and mode."
    expected: "The popup opens and closes, offers Administrator, Maya Chen and Alex Rivera in that order, and keeps the selected role when Escape cancels a tentative choice. Focus returns to the selector and remains visibly outlined."
    why_human: "The automated browser checks exercise DOM state, keyboard order and forced-colors CSS. The native popup and its platform focus treatment need visual observation."
  - test: "Screen-reader announcements. With a real screen reader, exercise the loading, initial error, retry failure, retry success and missing saved student Storybook states. Retry once with focus on the button and once after moving to Quick start. Record the browser, OS, reader and spoken sequence."
    expected: "Loading and fallback are spoken through the polite status, and failure is announced inline. Retry becomes available again after failure. Fallback selects Administrator and is announced once. Successful retry restores selector focus only if focus remained on Retry loading roles."
    why_human: "DOM roles, focus assertions and axe establish the DOM behavior. Spoken output, order and duplicates depend on the browser and reader combination."
  - test: "Actual 200% text zoom. Use a browser with text-only zoom at 200%. Inspect the app and prefixed docs at 320, 768 and 1280 CSS px, plus the narrow long-name story. Tab through the header and the feasibility report's wide table and code sample."
    expected: "Header, feedback, controls and focus rings fit without page-wide scrolling. A clipped selection has its full wrapped name below the control. Wide content scrolls within its named, keyboard-accessible region."
    why_human: "Automation exercised 200% CSS root font sizing. The browser text-zoom setting and native select rendering remain unobserved."
  - test: "Demo role boundary. Review the production selector, its storage and the BFF route before resolving the role-boundary prohibition."
    expected: "Approve the tab-local teaching selection and confirm that it grants no login session or authorization."
    why_human: "This judgment-tier prohibition requires explicit maintainer acceptance. The shipped code supports the boundary."
  - test: "Private advisory boundary. Review the docs output allowlist, workflow permissions and public guide using the public evidence."
    expected: "Approve that private inventories, feeds, credentials and scanner output remain outside the repository, site, CI and logs. B8 remains incomplete until authorized inputs and scanner are available."
    why_human: "This judgment-tier prohibition crosses publication surfaces. The generated site and leak controls provide scoped evidence."
  - test: "Phase 1 handoff. Read the rendered feasibility handoff and confirm Phase 7 owns the first hosted AMD64 DCB runtime run."
    expected: "Approve the historical ARM64 scope and the preservation of the runnable probe until the replacement criteria are met."
    why_human: "This judgment-tier prohibition includes acceptance of the scope of a public claim and retirement criteria."
  - test: "Test-tier prohibition review. Review the four test-tier prohibition projections against the linked task-level controls."
    expected: "Record the maintainer's disposition for local contract generation, the single-operation OpenAPI contract, staged-file isolation and the ordinary build graph."
    why_human: "The fallback projection has no structured enforcement descriptors. The individual controls passed, and the machine verdict stays fail-closed."
---

# Phase 02 Build and UI Foundations Verification

**Phase goal** — As a maintainer, I want to build and test the demo shell and generated BFF client through shared conventions, so that I can verify later feature slices from a clean checkout.

**Verdict** — `human_needed` · 29/31 must-haves verified · implementation checked at `d9a9614`

Initial verification. The clean-checkout outcome was demonstrated locally. Phase acceptance still needs native browser and assistive-technology observations. The matching hosted PR job is a ship checkpoint. No implementation blocker was found.

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
| 15 | 02-06 | Header and feedback wrap. Wide samples and tables scroll in their regions. The page fits at 320px and actual 200% text zoom. | Uncertain · warning | Chromium exercised 320, 768 and 1280 CSS px, scrollable regions and 200% CSS root sizing. Actual browser text zoom is pending. |
| 16 | 02-06 | Options retain complete names. A clipped selected value appears in full below the control. Long labels, links, headings and status wrap. | Verified | The production component measures clipping across font and size changes. The long-name story and Chromium responsive test check the full wrapping value. |
| 17 | 02-07 | Empty staged input is a no-op. Adjacent staged and unstaged edits remain distinct and overlaps preserve exact unstaged bytes. | Verified | Real Git fixtures assert index and worktree bytes, mode and overlap behavior. Publication affects the candidate index. |
| 18 | 02-07 | Format precedes lint on the candidate, and a rerun preserves bytes, modes and unaffected worktree content. | Verified | Candidate-config detekt and repeated-hook fixtures observe the formatting order and compare original and resulting Git and worktree state. |
| 19 | 02-07 | A competing writer, lock or formatter failure preserves staged and unstaged work. | Verified | The hook opens an exclusive lock and compares original index bytes before publishing. Independent concurrent-writer, existing-lock and failing-tool checks demonstrate preservation. |
| 20 | 02-08 | Doctor reports declared and observed versions, provenance, required tier and repair. Optional infrastructure failure allows a regular build. | Verified | Six doctor self-tests passed. The Gradle doctor report passed all required rows with refused Docker, and the same Docker setting allowed a clean build. |
| 21 | 02-08 | The public guide identifies actual selections, controls and missing records, and leaves B8 incomplete. | Verified | The public dependency runner checks selected Gradle graphs and pinned metadata. The guide cites unavailable historical paths and records the private scope and incomplete status. |
| 22 | 02-09 | An ordinary clean build regenerates the client and builds the app, Storybook and docs without infrastructure. | Verified | The post-review harness checked graph order, byte-identical client recovery, public startup, JVM cases, lock stability and failure on an injected opt-in edge. |
| 23 | 02-09 | The pushed PR has a successful read-only and SHA-pinned hosted job for the reviewed revision. | Uncertain · warning | Workflow wiring, actionlint, local style and clean build passed. The hosted job conclusion and exact reviewed head or PR merge mapping belong to the ship checkpoint. |
| 24 | 02-10 | Generation uses the contract and managed tools, restores deleted output and invalidates consumers after changes. | Verified | The retained direct runner observed generation alone, a no-change `UP-TO-DATE`, byte-identical recovery, rejected external schema reference and a changed operation export that triggers `TS2305` before bundling. |
| 25 | 02-10 | Malformed successful HTTP responses fail before persona data reaches the page. | Verified | The generated Zod schemas reject missing fields, empty labels and wrong discriminator. The adapter rejects duplicate IDs, undocumented status/media and redirects. All 19 boundary checks passed. |
| 26 | 02-11 | Storybook publishes production role states and retries. Steiger and axe reject controlled violations. | Verified | Thirteen stories run against real page and control implementations. Steiger reports `fsd/forbidden-imports` and axe reports `button-name` on deliberately broken variants. Repair restores passing results. |

### Negative Guarantees

| Plan | Guarantee | Evidence and disposition |
| --- | --- | --- |
| 02-01 | Generation needs no BFF, runtime API call or Docker. | The published variant is a local file. The standalone runner checks the generation-only task set and rejects a remote schema reference. Public package and tool provisioning uses the declared pins. Test-tier projection remains flagged. |
| 02-01 | The initial contract publishes only the implemented demo operation. | `DirectoryHttpTest` asserts exact path, method and operation ID on the served contract. Test-tier projection remains flagged. |
| 02-03 | Demo selection grants no login or authorization. | The read-only endpoint supplies catalog values. React holds the active selection in tab storage and never sends it as a credential. Judgment-tier acceptance remains open. |
| 02-04 | Keep private data outside the repository, site and CI. | The staged inputs and published outputs have exact allowlists, reject symlinks or contamination, and include a private-fixture control. The workflow runs only the public checks. Judgment-tier acceptance remains open. |
| 02-04 | Preserve the probe without claiming hosted AMD64 DCB proof. | The probe remains callable. The rendered guide retains its replacement criteria, and Phase 7 owns the first hosted runtime proof. Judgment-tier acceptance remains open. |
| 02-07 | Preserve unstaged work and competing index updates. | Real Git fixtures cover overlap, editor saves during publication, and an independent index writer. Test-tier projection remains flagged. |
| 02-09 | Keep Docker, packaging and infrastructure test tasks out of ordinary builds. | The refused-Docker build, selected-task inspection, injected forbidden edge and opt-in task presence were exercised. Test-tier projection remains flagged. |

The four test-tier projections lack structured enforcement descriptors. Their automatic disposition remains unverified. The report links the direct controls for explicit review and carries each judgment-tier item into manual acceptance.

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
| Phase 1 integration and native packaging | The Docker daemon was unavailable. The previous native ARM64 run is historical evidence. Phase 7 owns first hosted AMD64 DCB runtime proof. | Outside this rerun |

Phase 2 probes use Python and Gradle entry points. No conventional or named `probe-*.sh` was declared. Retained direct runner results were inspected where available alongside the new local checks and build artifacts.

### Test Quality Audit

The linked suites have active contract, state and failure assertions. The JUnit XML shows no skips. A separate validator checks actual HTTP bodies using the checked-in contract and separately specified expected roles. Browser tests assert focus, retry, order, routes and visible output. Git tests compare exact bytes and modes after real operations. Repeated generation checks determinism, and explicit contract mutations verify independent consumer invalidation.

## Requirements Coverage

| Requirement | Plans | Status | Evidence |
| --- | --- | --- | --- |
| FND-02 | 01, 05, 07, 08, 09 | Satisfied | Wrapper, catalog, JDK and Node pins, scoped npm metadata and locks, mise and workflow pins align with the inventory. Doctor observed the actual Temurin 25.0.5.1+2-LTS worker and required tools. |
| FND-05 | 02 | Satisfied | Gradle JVM suites run Jupiter with Kotest assertions and properties. Both BFF suites resolve the shared fixture variant and production excludes test tools. |
| FND-06 | 01, 04, 09, 10 | Satisfied | Clean Gradle build emits web, docs and Storybook. The BFF contract is explicitly consumed before frontend checks and output. |
| CQRS-04 | 01, 02, 03, 09, 10 | Satisfied at Phase 2 scope (D-04) | The implemented GET directory is contract-first, served exactly, independently validated and consumed through its generated client. Full browser command, read and live operation coverage remains pending with the later slices, starting in Phase 3. |
| UI-01 | 03, 04, 06, 09, 11 | Foundation verified, manual acceptance pending | Approved UI-SPEC, production components, Steiger and its negative control, required Storybook states and axe checks. Native and assistive observations remain below. |
| UI-03 | 01, 03, 06, 09, 11 | Implemented behavior verified | Real browser selection of all three roles, tab independence, reload, validated fallback and retry. |
| QA-07 | 02, 05, 07, 09 | Satisfied | ktfmt semantics and two-pass proof, detekt negative witness, and both Dokka warning failures and repairs. The Phase 1 specimen is preserved. |
| QA-08 | 05, 07, 09 | Local implementation verified, hosted evidence pending | Shared staged and full-tree policy, real Git controls, validated PR workflow and local clean build. The traceability row stays pending until the matching hosted job passes. |
| DOC-06 | 04, 08, 09 | Satisfied | Reconciled public B17/B8 provenance, public selected-graph reproduction, explicit incomplete B8 status and verified publication boundaries. |

All nine Phase 2 IDs occur in at least one plan. No orphaned requirements were found.

### Decision Coverage

GSD reported 15/15 trackable decisions honored. The shipped paths support the D-04 contract extension boundary and D-15 Phase 7 handoff.

### Anti-Patterns and Review Follow-Up

No unreferenced `TBD`, `FIXME` or `XXX` markers or disabled requirement-linked tests were found in the changed implementation. The fixed demo catalog and isolated story data serve their declared use cases. The reviewed corrections are present for index-only publication, path-limited commits, shell literal whitespace, partial-response deadlines, prefixed preview, malformed Node pins and comma-bearing detekt paths. The docs ship both Geist assets and licenses. Wide named docs regions support keyboard scrolling. The review accepted explicit sequential focus for those regions across widths.

## Human Verification Required

### 1. Native role selector and forced colors

**Test** — In the running shell use Tab and Shift+Tab to reach Demo role. Open the native list with the platform shortcut, move through the options with arrows, select a student, then reopen it and close it with Escape. Repeat in a platform-supported forced-colors mode. Record browser, OS and mode.

**Expected** — The popup opens and closes, offers Administrator, Maya Chen and Alex Rivera in that order, and keeps the selected role when Escape cancels a tentative choice. Focus returns to the selector and remains visibly outlined.

**Why human** — The automated browser checks exercise DOM state, keyboard order and forced-colors CSS. The native popup and its platform focus treatment need visual observation.

### 2. Screen-reader announcements

**Test** — With a real screen reader, exercise the loading, initial error, retry failure, retry success and missing saved student Storybook states. Retry once with focus on the button and once after moving to Quick start. Record the browser, OS, reader and spoken sequence.

**Expected** — Loading and fallback are spoken through the polite status, and failure is announced inline. Retry becomes available again after failure. Fallback selects Administrator and is announced once. Successful retry restores selector focus only if focus remained on Retry loading roles.

**Why human** — DOM roles, focus assertions and axe establish the DOM behavior. Spoken output, order and duplicates depend on the browser and reader combination.

### 3. Actual 200% text zoom

**Test** — Use a browser with text-only zoom at 200%. Inspect the app and prefixed docs at 320, 768 and 1280 CSS px, plus the narrow long-name story. Tab through the header and the feasibility report's wide table and code sample.

**Expected** — Header, feedback, controls and focus rings fit without page-wide scrolling. A clipped selection has its full wrapped name below the control. Wide content scrolls within its named, keyboard-accessible region.

**Why human** — Automation exercised 200% CSS root font sizing. The browser text-zoom setting and native select rendering remain unobserved.

### 4. Demo role boundary

**Test** — Review the production selector, its storage and the BFF route before resolving the role-boundary prohibition.

**Expected** — Approve the tab-local teaching selection and confirm that it grants no login session or authorization.

**Why human** — This judgment-tier prohibition requires explicit maintainer acceptance. The shipped code supports the boundary.

### 5. Private advisory boundary

**Test** — Review the docs output allowlist, workflow permissions and public guide using the public evidence.

**Expected** — Approve that private inventories, feeds, credentials and scanner output remain outside the repository, site, CI and logs. B8 remains incomplete until authorized inputs and scanner are available.

**Why human** — This judgment-tier prohibition crosses publication surfaces. The generated site and leak controls provide scoped evidence.

### 6. Phase 1 handoff

**Test** — Read the rendered feasibility handoff and confirm Phase 7 owns the first hosted AMD64 DCB runtime run.

**Expected** — Approve the historical ARM64 scope and the preservation of the runnable probe until the replacement criteria are met.

**Why human** — This judgment-tier prohibition includes acceptance of the scope of a public claim and retirement criteria.

### 7. Test-tier prohibition review

**Test** — Review the four test-tier prohibition projections against the linked task-level controls.

**Expected** — Record the maintainer's disposition for local contract generation, the single-operation OpenAPI contract, staged-file isolation and the ordinary build graph.

**Why human** — The fallback projection has no structured enforcement descriptors. The individual controls passed, and the machine verdict stays fail-closed.

## Hosted Evidence at Ship

After the authorized workflow pushes the branch and opens the PR, run `gh pr checks --watch` and inspect the matching run with `gh run view <run-id>`. Before merge, record the run link, matched head SHA or PR merge mapping, runner architecture, and successful wrapper validation, `styleCheck` and `clean build --no-build-cache`. Changes to the reviewed head require a matching new run.

## Gaps Summary

No failed implementation truths were found. Actual 200% text zoom and the matching hosted PR job account for the two uncertain truths. The remaining native-accessibility and explicit judgment checks are listed above. The private B8 scan is incomplete pending authorized inputs and the first hosted AMD64 DCB runtime proof belongs to Phase 7.

_Verified 2026-11-25T17:10:17Z by gsd-verifier._
