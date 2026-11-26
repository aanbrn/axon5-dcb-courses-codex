---
phase: quick-261126-lmh
verified: 2026-11-26T08:57:34Z
status: passed
score: 3/3 must-haves verified
covered_files:
  - .planning/quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-PLAN.md
  - .planning/quick/261126-lmh-isolate-historical-qodana-scans-from-ide/261126-lmh-SUMMARY.md
  - docs/maintainer-guide.md
  - tools/qodana-scan.sh
covered_digest: "v4:sha256:48795065d94c44935bc4040a331d17a546b0515cdeb8bf8dcc03443732938c61"
behavior_unverified: 0
overrides_applied: 0
---

# Quick Task 261126-lmh Verification

Close Phase 02 CR-04 by isolating historical Qodana snapshots and analysis caches from the IntelliJ editor profile while preserving Gradle diagnostics, Spring entry points and the Axon plugin.

## Observable Truths

| # | Plan must-have | Status | Independent evidence |
| --- | --- | --- | --- |
| 1 | The ordinary launcher recovers genuine Gradle diagnostics on the historical revision, the exact delivery commit and a second historical scan using one analysis cache. | VERIFIED | The three retained scans recovered all 51 reference findings with successful invocations and the same 20-module model. The original scan of the historical SHA returned zero. Code, Git blob keys, cache identity and Gradle import or model reuse logs establish the shared path. |
| 2 | Each archived revision omits the editor profile before the synthetic Git snapshot. Both analysis paths bypass old cached editor settings. | VERIFIED | Archive comparisons on five revisions removed only the tracked historical profile where present. All three new synthetic Git trees match their filtered archive by tracked blob ID. All three working snapshots and the current fresh cache omit the editor profile. Evaluating the launcher’s unconfigured cache selection against a retained archive without the Spring XML returned the new `no-entry-points` path before cache creation. |
| 3 | Configured revisions retain Spring Bean entry points, Axon, warm Gradle dependencies and the recommended profile. The working checkout retains its IDEA settings. | VERIFIED | The common Spring component survives in each run’s final `misc.xml`, Axon 0.10.1 loads from the existing plugin cache, and every SARIF uses the recommended profile. All three runs preserve the three Spring factory and four Axon handler results. The working editor profile checksum matches the pre-run checksum. |

## Artifacts and Wiring

| Artifact | Status | Evidence |
| --- | --- | --- |
| [Qodana launcher](../../../tools/qodana-scan.sh#L35) | VERIFIED | The literal Git exclusion runs before extraction and synthetic commit. The inspected Spring blob supplies `misc.xml` and the configured analysis-cache key. The default key is `no-entry-points`. The revision’s `qodana.yaml` blob still supplies the plugin-cache key, with `no-config` as the fallback. The Docker volume arguments use the resulting analysis and plugin paths alongside the existing Gradle mount. |
| [Maintainer guide](../../../docs/maintainer-guide.md#local-kotlin-inspections) | VERIFIED | The documented launcher commands, revision archive exclusion, qualified Spring and Axon behavior, and both analysis-cache keys match the implementation. The delivery commit changes only the launcher and the two Qodana guide paragraphs. |

The GSD artifact and key-link checks returned 2/2 and 3/3. Both owning files match delivery commit `3df371b931bb5ba908c69b94f25059e90c2254d5` in the working checkout.

## Scan Evidence

The retained directories below are relative to the ignored `.gradle/qodana/runs/` path. Each revision marker matches the requested commit, and each of the three new console logs names the corresponding report directory.

| Run | Directory | Findings | SARIF SHA-256 |
| --- | --- | ---: | --- |
| Historical control | `e434f250f5e3d729f789de1cb4dae2a5871080df.aLTXc4` | 0 | `1bee011768e1b3df63e0c5b35670b9f6556cb0f62fd8f2852ccefb59bdda4fe2` |
| Clean reference | `fff0b35755676ab15867460b8e0bb73449f9b2c8.mBmOjq` | 51 | `a1904e1df11912d0324c715ac313208813a0b4d721195c399a20b54fb2ff7e4e` |
| First historical scan | `e434f250f5e3d729f789de1cb4dae2a5871080df.KaymLA` | 52 | `9bb3bc2661913f68009f0e71d2654833d864a0a80258632e1ada0f05d156b969` |
| Exact delivery scan | `3df371b931bb5ba908c69b94f25059e90c2254d5.zF3TEP` | 51 | `5397e5e7a2739ebc8a832c9263550756029579a02319b3c8394fab91ebea2c98` |
| Historical repeat | `e434f250f5e3d729f789de1cb4dae2a5871080df.aCxHM7` | 51 | `5abb2d2798ffff4c2ac004258860eac9ae86ea6abf0f951a33e7557bb9c789a4` |

- Each new SARIF has a successful invocation and `configProfile: recommended`. The findings match the clean reference as a multiset keyed by rule, source path, line, column, snippet and message. Every result is `UnstableApiUsage`, including BFF Gradle incubation diagnostics. The first scan alone adds `TestingExtension.getSuites()` at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:24:9`, highlighting `suites`.
- The first scan completed Gradle resolution and import. The delivery and repeat scans loaded external project data and applied it successfully. Full module records match after keying modules by name and sorting their `contentEntries` by path. The first import reordered three entries in `build-logic.main`. The other two module reports are byte-identical to the reference.
- All three new SARIF files carry the reference’s `sanityFailure` for the unresolved generated `build-logic/build/pluginUnderTestMetadata` root in `build-logic.test`. The scanner logs also reproduce the reference’s JetBrains internal plugin repository HTTP 401 and configuration-script service override warnings.
- The inspected Spring XML blob is `3c9deeb0d85d54bdd7d3a968093dc2545359c330` in all three revisions. The final `misc.xml` preserves the blob’s complete `EntryPointsManager` component for `org.springframework.context.annotation.Bean` alongside generated Gradle and JDK settings. The three factories `enrollmentHandler`, `tokenStore` and `courseProjection` are reported by the older no-Spring control, then absent from the three new SARIF files.
- The common configuration blob `35d11a506cae623f5450221d5c11035cdd1d588f` selects the installed Axon Framework plugin `io.axoniq.ide.intellij` 0.10.1. All three logs confirm it loaded. Its JAR SHA-256 is `924cb8f1ba3c30e0d3970191d2adbbf2b2ab7e9d2012f355f100bdfa44181fef`. The four annotated handlers `ready`, `enroll`, `course` and `enrolled` are reported by the older no-plugin control, then absent from the three new SARIF files.
- The current Gradle cache, plugin cache and both legacy analysis cache directories match the recorded pre-run device and inode pairs. The new Spring-keyed cache matches its device and inode recorded before the delivery and repeat scans. The checkout profile is tracked and clean with SHA-256 `599ec2ecaf83fef1a888d3ec25bcac89316ce281cd7fdd5eac692081b290f1aa`, matching the pre-run copy. The historical control’s profile independently matches the `e434f25` Git blob.

## Verification Checks

| Check | Result |
| --- | --- |
| Shell syntax, managed ShellCheck and `git diff --check` for the delivery commit | PASS |
| Literal Git archive exclusion on `e434f25`, `fff0b35`, `3df371b`, `b838a25` and `9bac742` | PASS |
| Cache selection on the retained snapshot of `01045e6e975293484d77a12c893ecd1cef41f35c`, which lacks Spring XML | PASS. The read-only shell check evaluated the launcher’s selection before its directory creation. The three retained full scans exercised the Spring-configured path. |
| Gradle `styleCheck` and `:docs-site:check` | The retained delivery log shows `styleCheck` completed and two inherited article-region tests failed. The retained integrated log at `a702e28515011b1124fc9c17d34c1aa5dd35a1bb` shows both tasks completed and all 28 documentation tests passed. The adjacent fix changed separate documentation-site and smoke-test files. |

The three real scans are the behavioral test for the shared-cache transition. Verification read the retained artifacts directly. The report fingerprints the tracked implementation and its plan and summary. The ignored evidence remains machine-local and is identified by run path and checksum. The launcher and guide contained no unresolved debt markers or placeholder behavior. The retained logs and snapshots cover the automated criteria without a human check.

## Requirements Coverage

| Requirement | Status | Evidence |
| --- | --- | --- |
| Phase 02 CR-04 | SATISFIED | The three-run regression reproduces the 51 reference findings and confirms editor profile isolation across the shared cache. |
| QA-07 | Phase 02 requirement previously satisfied | The quick plan draws on QA-07 for related tooling. Its KDoc, ktfmt, detekt and Dokka evidence remains in the [Phase 02 verification](../../phases/02-build-and-ui-foundations/02-VERIFICATION.md#requirements-coverage). |
