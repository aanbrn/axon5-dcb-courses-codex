---
phase: quick-261126-lmh
plan: "01"
subsystem: build-tooling
tags: [qodana, gradle, intellij, docker]
requires:
  - phase: quick-261126-jp0
    provides: Spring entry-point settings and qualified Axon plugin behavior
  - phase: quick-261126-jsl
    provides: Shared IntelliJ profile and historical and clean SARIF controls
provides:
  - Revision-independent editor profile exclusion in the ordinary Qodana launcher
  - Fresh Qodana analysis caches for configured and unconfigured revisions
affects: [local-quality-checks, maintainer-guide]
tech-stack:
  added: []
  patterns: [literal Git archive pathspec exclusion, configuration-keyed analysis cache]
key-files:
  modified: [tools/qodana-scan.sh, docs/maintainer-guide.md]
key-decisions:
  - Exclude the editor profile in the archive tree walk before extraction.
  - Use a new analysis namespace keyed by the Spring XML blob or no-entry-points.
requirements-completed: [QA-07]
commits: 1
plan_head_before: 86ec0fc011bd98abf18115d366c8b5c534c6c62d
plan_head_after: 3df371b931bb5ba908c69b94f25059e90c2254d5
actuals:
  tokens: 1734
  tasks: 2
  commits: 1
duration: 8m
completed: "2026-11-26"
status: complete
---

# Isolate historical Qodana scans from the IntelliJ editor profile

The ordinary Qodana launcher recovered all 51 known Gradle incubation diagnostics on the historical revision, the delivery commit and a second scan of the historical revision. The original historical report had zero findings. This closes Phase 02 review finding CR-04.

## Snapshot and cache isolation

The launcher excludes `.idea/inspectionProfiles/Project_Default.xml` via a literal Git pathspec before extracting any revision. A plain `git archive` of `e434f25` included the file. The explicit exclusion omitted it on `e434f25`, `fff0b35`, `b838a25` and the checkout's committed tree at the time of verification. The synthetic Git tree and the extracted project omitted the profile after every scan. The analysis cache contained no copy after each scan. The working checkout's profile retained SHA-256 `599ec2ecaf83fef1a888d3ec25bcac89316ce281cd7fdd5eac692081b290f1aa`.

All three scans selected `.gradle/qodana/analysis-cache/without-editor-profile/3c9deeb0d85d54bdd7d3a968093dc2545359c330` using the same Spring XML blob. The directory identity stayed stable after its initial creation. Each generated `.idea/misc.xml` contained `org.springframework.context.annotation.Bean`. The launcher selects `analysis-cache/without-editor-profile/no-entry-points/` for revisions without the XML. The existing shared Gradle cache, `qodana.yaml`-keyed plugin cache (`35d11a506cae623f5450221d5c11035cdd1d588f`) and legacy analysis directories retained their directory identities. Qodana logged the already-installed Axon Framework plugin `io.axoniq.ide.intellij` 0.10.1 in every scan. The installed JAR retained SHA-256 `924cb8f1ba3c30e0d3970191d2adbbf2b2ab7e9d2012f355f100bdfa44181fef`.

## Colima verification

The ordinary launcher ran Qodana Community for JVM 2026.3 (`QDJVM-263.8362`) with Temurin 25 and Gradle 9.9.2. Each run directory below is relative to `.gradle/qodana/runs/` and contains the requested commit marker, the archived project, SARIF, HTML, `log/idea.log` and `projectStructure/Modules.json`. Console logs and check output remain in `.gradle/qodana/261126-lmh/`.

| Role | Run directory | `UnstableApiUsage` | Other findings |
| --- | --- | ---: | ---: |
| Original historical control | `e434f250f5e3d729f789de1cb4dae2a5871080df.aLTXc4` | 0 | 0 |
| Clean reference | `fff0b35755676ab15867460b8e0bb73449f9b2c8.mBmOjq` | 51 | 0 |
| First historical scan | `e434f250f5e3d729f789de1cb4dae2a5871080df.KaymLA` | 52 | 0 |
| Exact delivery scan | `3df371b931bb5ba908c69b94f25059e90c2254d5.zF3TEP` | 51 | 0 |
| Historical repeat | `e434f250f5e3d729f789de1cb4dae2a5871080df.aCxHM7` | 51 | 0 |

All three new reports used `qodana.recommended` and recorded successful invocations. The first scan completed a full Gradle import. The second and third loaded the cached external Gradle data and applied it successfully. All 51 reference findings matched by rule, path, line, column, highlighted text and message. The only extra finding was the previously observed fresh-cache `TestingExtension.getSuites()` at `build-logic/src/main/kotlin/courses.jvm.gradle.kts:24:9`. The Spring factories `enrollmentHandler`, `tokenStore` and `courseProjection` and Axon handlers `ready`, `enroll`, `course` and `enrolled` produced no `UnusedSymbol` findings in any of the new reports.

All runs reported the same 20 modules. The first fresh import reordered three otherwise identical `contentEntries` in `build-logic.main`. The module comparison sorted modules by name and each module's `contentEntries` by path, preserving all properties and entries. The delivery and repeat reports already matched the reference after sorting modules alone. The first raw ordering difference remains in `first-module-order.diff` alongside the console logs.

Each new SARIF carried the same separate `sanityFailure` notification as the clean reference for the unresolved generated `build-logic/build/pluginUnderTestMetadata` root in `build-logic.test`. The scanner log also repeated the reference run's JetBrains internal plugin-repository HTTP 401 messages and the configuration script service override warning. Gradle model import or reuse and the cached Axon plugin load succeeded in all three runs.

## Local checks

Shell syntax, managed ShellCheck, `git diff --check` and the checked-in pre-commit hook passed for `3df371b`. The exact delivery commit also passed Gradle `styleCheck` in a temporary detached worktree using the existing local dependency cache. It inherited two documentation landmark regression tests from parent `86ec0fc`, so `:docs-site:check` failed there with duplicate accessible region names. The adjacent fix `a702e28` resolved both failures. The combined `mise exec python ruff taplo -- ./gradlew --console=plain styleCheck :docs-site:check` passed in the primary checkout with that fix, including all 28 documentation tests. `style-delivery.log` and `style-integrated.log` preserve both outcomes. The temporary worktree was removed after the check.

## Task commits

- `3df371b931bb5ba908c69b94f25059e90c2254d5` delivers the launcher and maintainer guide.
- The three scan reports and local validation logs remain in ignored directories.

## Deviations from Plan

- The fresh module comparison additionally sorted `contentEntries` to account for the ordering difference described above.
- The combined style and documentation command passed after the adjacent documentation fix. The exact delivery revision retained its independent style result.

## Self-Check: PASSED
