---
title: Maintainer guide
layout: page.11ty.js
---

# Maintainer guide

## Version owners

| Tool or dependency                      | Source                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gradle distribution and checksum        | [Wrapper properties](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/gradle/wrapper/gradle-wrapper.properties)                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Gradle plugins, dependencies and images | [Version catalog](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/gradle/libs.versions.toml)                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Eclipse Temurin feature version         | [JDK version file](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/.java-version)                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Node.js                                 | [Node version file](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/.nvmrc)                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| npm executables                         | The `packageManager` pins in [web](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/web/package.json), [docs-site](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/docs-site/package.json), [tools/style](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/tools/style/package.json) and [probe/web](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/web/package.json). The standalone probe build also supplies that npm version to `probe/typeid`.                                                            |
| npm package selections                  | [Web lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/web/package-lock.json), [docs lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/docs-site/package-lock.json), [style lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/tools/style/package-lock.json), [static probe lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/web/package-lock.json) and [TypeID probe lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/typeid/package-lock.json). |
| Python and independent CLIs             | [mise configuration](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/mise.toml)                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| GitHub Actions                          | Each external action uses a full commit SHA in its [workflow](https://github.com/aanbrn/axon5-dcb-courses-codex/tree/main/.github/workflows). Doctor reports the pins it can read from the checkout.                                                                                                                                                                                                                                                                                                                                                                |

## Setup and diagnostics

Use an ARM64 or AMD64 host running macOS or Linux with Git, a POSIX shell and mise. If mise requests trust, review `mise.toml` and run `mise trust` from the repository root.

Install Eclipse Temurin at the feature release in `.java-version` and point `JAVA_HOME` at that JDK, or use mise to supply Eclipse Temurin and Node.js to individual commands. Gradle uses an Eclipse Adoptium toolchain for the BFF JVM suites. The complete vendor, patch and build strings in doctor are observations. The version file stays feature-only.

```sh
mise install java node
mise ls --current
mise exec java node -- java -version
mise exec java node -- node --version
mise exec java node -- ./gradlew --version
```

The `Source` column shows `.java-version` for Java and `.nvmrc` for Node.js. Edit those files when changing the JDK feature or Node version. The project config excludes `.sdkmanrc`, `.node-version` and `package.json` from runtime discovery so these versions come from the same files used by CI and Gradle. Gradle installs its own Node.js and uses each consumer's `packageManager` pin for npm. The `mise.toml` pins control Python, actionlint, ShellCheck, Ruff, Taplo and Pack. Install the required tools for diagnostics and style.

```sh
mise install python aqua:rhysd/actionlint shellcheck ruff taplo
mise exec java python aqua:rhysd/actionlint shellcheck ruff taplo -- ./gradlew --console=plain doctor
```

Doctor compares the running Python interpreter to the exact patch version in `mise.toml` and reads the versions of the workflow lint and style tools from their executables. A failing required row sets a nonzero exit status. Additional checks cover Docker, Compose, Pack and the retained probe. A failing additional row identifies which optional workflow needs attention. For GSD for Codex, doctor reports whether it finds the CLI file under the checkout's `.codex` or the configured `CODEX_HOME` (default `~/.codex`). This is an informational observation based on file presence. The observed managed Node and npm versions come from starting the executables at the reported paths. On a fresh checkout, the regular build provisions them, or run the setup tasks for the consumer you need.

```sh
./gradlew npmSetup :web:npmSetup :docs-site:npmSetup
# For the independent Phase 1 probe only
./gradlew -p probe/web npmSetup
```

When `./gradlew` cannot start, run the same diagnostic in bootstrap mode. Resolve each required failure using its repair column, then rerun `doctor`. Bootstrap checks local inputs and the launcher, and marks Gradle, the BFF worker and managed Node/npm observations as deferred.

```sh
mise exec java python aqua:rhysd/actionlint shellcheck ruff taplo -- python3 tools/doctor.py
```

Run `./gradlew installGitHooks` to opt in to the staged-content hook. Commit from a shell with mise activated so the hook inherits Python, Ruff and Taplo. For a single commit, use `mise exec python ruff taplo -- git commit`. Run the full tracked-file check with `mise exec python ruff taplo -- ./gradlew styleCheck`. Both entry points use the checked-in [style policy](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/tools/style/policy.json).

The hook formats staged content and leaves your working files untouched. After a commit that applies formatting, use `git diff -- <path>` to review the unstaged changes. To copy the committed formatting back, use `git restore --patch --worktree -- <path>` and select only hunks that contain formatting you want to keep. If a hunk also contains local edits, carry the formatting over in your editor.

## Pull request build

The `build-and-style` job runs on GitHub's Ubuntu 24.04 x64 runner with read access to repository contents. It validates the Gradle wrapper before running it. The workflow pins each action to the publisher's full commit SHA. [Build workflow](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/.github/workflows/build.yml)

| Action                    | Release                                                             | Purpose                                                                                                    |
| ------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Checkout                  | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)   | Check out the PR merge revision without retaining checkout credentials                                     |
| Gradle Wrapper Validation | [v6.4.1](https://github.com/gradle/actions/releases/tag/v6.4.1)     | Compare the wrapper JAR with published Gradle checksums                                                    |
| Setup Java                | [v6.3.0](https://github.com/actions/setup-java/releases/tag/v6.3.0) | Select Eclipse Temurin from `.java-version`                                                                |
| Mise Action               | [v5.3.0](https://github.com/jdx/mise-action/releases/tag/v5.3.0)    | Run mise 2026.11.14 and install the Python, actionlint, ShellCheck, Ruff and Taplo versions in `mise.toml` |

The job logs the runner architecture and effective Java, Gradle, mise, Python, actionlint, ShellCheck, Ruff and Taplo versions. It runs actionlint with ShellCheck on the GitHub Actions workflows before the tracked formatting and style check. Gradle provisions Node from `.nvmrc` and npm from each consumer's `packageManager` field. Run `doctor` after provisioning to see their resolved versions and the BFF test worker's JDK build.

Run the same checks from the repository root. The style command also provisions the locked YAML parser used by the local workflow checker.

```sh
mise exec aqua:rhysd/actionlint shellcheck -- actionlint -shellcheck=shellcheck -pyflakes=
mise exec python ruff taplo -- ./gradlew --console=plain styleCheck
DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain clean build --no-build-cache
mise exec python -- python3 tools/check_pr_workflow.py
```

The ordinary build generates and checks the web client, builds the app, Storybook and docs, and runs the JVM suites that use local files or loopback HTTP. The browser journey is a separate check with explicit Chromium provisioning. Keep ports 5173, 8080 and 8081 free when running these local checks.

```sh
mise exec python -- python3 tools/test_phase2_build.py
./gradlew --console=plain :web:provisionBrowser :web:siteSmoke
```

## Documentation build

```sh
./gradlew :docs-site:docsBuild
```

Gradle stages the public sources and renders the static site into `docs-site/build/site`. The optional `docsBase` is a deployment path with a leading and trailing slash. With `/courses/`, mount the output there. The local preview prints `http://127.0.0.1:8081/courses/` when it is ready.

Use document-relative links such as `../feasibility/phase-01/` from the Maintainer guide. Write the published path as it appears, with literal `/` separators. The build rejects an active `<base href>` so links resolve from the published page URL. Link fragments to element IDs or named anchors in the active page. An ID on a `<template>` element can be targeted. Its contents are inert.

To try the prefixed site with the live demo, run these commands in separate terminals. Both the app's documentation links and the site's **Open demo** action use the URLs below.

```sh
./gradlew :bff:bootRun --args='--server.address=127.0.0.1'
VITE_DOCS_BASE=http://127.0.0.1:8081/courses/ ./gradlew :web:dev
./gradlew :docs-site:serve -PdocsBase=/courses/ -PdocsAppUrl=http://127.0.0.1:5173/
```

For hosted deployments, provide an HTTPS `docsAppUrl` and include its origin in the comma-separated `docsTrustedAppOrigins` build setting. The local Vite origin `http://127.0.0.1:5173` is already allowed. Invalid values fail the build.

Set `VITE_DOCS_BASE` when building the hosted web app with `./gradlew :web:webBuild`. Use the published documentation URL with its full deployment prefix, for example `https://docs.example.com/courses/`.

## Local Kotlin inspections

Run Qodana Community for JVM with Docker and the Python version in `mise.toml`. The command inspects a committed revision, using `HEAD` by default.

```sh
mise exec python -- sh tools/qodana-scan.sh
mise exec python -- sh tools/qodana-scan.sh HEAD~1
```

The script uses the Qodana image pinned in the Gradle catalog and provides the Temurin feature version from the inspected revision's `.java-version`. It imports a separate source snapshot and runs `qodana.recommended`. Open the HTML or SARIF report in the printed directory under `.gradle/qodana/runs/`. Scans share the Gradle cache in `.gradle/qodana/cache/gradle/`. Installed plugins use `.gradle/qodana/plugin-cache/`, keyed by the inspected revision's `qodana.yaml` Git blob. Revisions without that file use their own plugin cache.

The local Community scan works without credentials. It loads the Axon Framework plugin declared in `qodana.yaml`. With Qodana 2026.3 and Axon Framework plugin 0.10.1, the Kotlin `UnusedSymbol` inspection recognized the probe's `@CommandHandler`, `@QueryHandler` and `@EventHandler` methods as used. [Axon Framework plugin](https://plugins.jetbrains.com/plugin/18628-axon-framework)

Qodana resolves the plugin by ID from Marketplace and caches the installed files. The image digest pins the linter, while Marketplace may offer a newer compatible plugin release. When the linter or plugin changes, compare two disposable Git snapshots of the same revision. Give each snapshot a fresh plugin cache and add the same unannotated, unused Kotlin method next to `EnrollmentHandler.ready`. Keep the plugin declaration only in the candidate snapshot and commit both snapshots before running the launcher. Check the candidate's loaded plugin version in `results/log/idea.log` and confirm that both Gradle imports and analyses succeeded. In the two SARIF reports, check that only the four annotated Axon handlers lose their `UnusedSymbol` results and that the unused method still appears. [Qodana plugin installation](https://www.jetbrains.com/help/qodana/extending-qodana-plugins.html)

The launcher installs `.qodana/profiles/spring-beans.xml` as `.idea/misc.xml` inside the archived snapshot. Qodana's Kotlin `UnusedSymbol` inspection recognizes methods annotated with `org.springframework.context.annotation.Bean` as entry points. Qodana Community 2026.3 cleared the probe's three bean factories and a newly added test factory. An unannotated method and a method marked with a different annotation named `Bean` remained reportable. Qodana can restore project settings from its cache, so the launcher uses `.gradle/qodana/analysis-cache/without-editor-profile/` for analysis state. Within that directory, revisions use the XML's Git blob ID as the cache key or `no-entry-points` if the XML is absent. [Qodana entry-point configuration request](https://youtrack.jetbrains.com/issue/QD-14001), [cache behavior](https://youtrack.jetbrains.com/issue/QD-13987)

To repeat the Spring check, commit the same three controls in two disposable Git snapshots of the same revision. Add a public unused method with Spring's `@Bean`, one with a different `Bean` annotation, and one with no annotation. Remove `.qodana/profiles/spring-beans.xml` only from the control snapshot. Run the launcher on both. In `qodana.sarif.json`, confirm that only the four Spring factories lose their `UnusedSymbol` findings in the candidate, and check that the `projectStructure/Modules.json` files list the same Gradle modules. Full Spring inspections require Qodana for JVM with an Ultimate or Ultimate Plus license and an authorized project `QODANA_TOKEN`. [JVM feature matrix](https://www.jetbrains.com/help/qodana/jvm.html#Supported+technologies+and+features), [project token requirements](https://www.jetbrains.com/help/qodana/docker-image-configuration.html)

## IntelliJ IDEA inspection profile

Open the repository as a Gradle project. In **Settings → Editor → Inspections**, select **Project Default** from the project profiles. The shared profile keeps **Unstable API Usage** (`UnstableApiUsage`) enabled at **Warning** and removes only `org.gradle.api.Incubating` from its annotation list. The exclusion applies across the whole project, including future Gradle call sites. Current intentional uses include the JVM Test Suite DSL and the `dependencyScope`, `resolvable` and `consumable` configuration roles. [Inspection profiles](https://www.jetbrains.com/help/idea/customizing-profiles.html)

If IDEA was already open when the shared profile was added and reports a duplicate `Project Default` scheme, close and reopen the project to load the profile from disk.

If you use a custom project profile, keep it selected and remove the same annotation under **JVM languages → Unstable API Usage → Unstable API annotations**. For an IDE-level profile, first use **Copy to Project** to keep the change local to this project. After an IDE upgrade, compare the shared list with the bundled defaults and carry forward any new annotations. [Unstable API Usage defaults](https://www.jetbrains.com/help/inspectopedia/UnstableApiUsage.html)

When upgrading the Gradle wrapper, run the build and the ordinary Qodana command above on the committed revision. Review new or changed `UnstableApiUsage` findings for Gradle APIs. The launcher excludes `.idea/inspectionProfiles/Project_Default.xml` when archiving any revision for inspection with `qodana.recommended`.

## Feasibility probe

The [probe build](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/build.gradle.kts) provides the opt-in DCB integration suite. Follow the [probe runbook](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/README.md) to reproduce the native proof. The [feasibility report](/feasibility/phase-01/#hosted-amd64-verification-and-retirement) records the evidence and conditions for retiring the probe.

## Extending the API contract

The [OpenAPI contract](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/bff/src/main/resources/static/openapi.json) currently publishes the demo role directory. Add operations for browser commands, reads and live subscriptions as the corresponding behavior ships. Define the operation, schema, success and error responses in the contract, keep existing operation IDs stable, and add BFF component coverage against the checked-in contract. Run `./gradlew :bff:componentTest :web:generateClient :web:webCheck` to verify the implementation, regenerate the client and exercise consumers. Extend the shell through the generated client.

The selected demo role is local tab state. If a future version adds login, use a signed cookie for the login session and verify session behavior with that feature.

## Dependency maintenance

Start with the latest stable release in the applicable major or LTS line. Verify compatibility before changing an owner. Record the scope, owner, concrete blocker and evidence for any hold. Review it within seven days unless the record specifies a date, and earlier after an upstream release, relevant advisory or terms change. Record any renewal with its evidence and removal trigger.

Prefer a BOM or parent update that fixes the consuming graph within scope. Where the BOM cannot deliver the fix, use a catalog-backed ordinary lower-bound constraint with a reason on the affected declarable configuration. Use a strict bound only when reproduced selection behavior requires it, and record the case. Keep application and formatter scopes independent. Capture the full affected and control graphs, incoming paths and selection reasons, and run their applicable tests. Repeat those checks before removing a bound.

The source brief cites the 2026-11-24 historical records in `phases/01-axon-server-feasibility-and-build-foundation/01-13-PLAN.md#b17-reference-scoped-transitive-review` (B17) and `phases/01-axon-server-feasibility-and-build-foundation/01-09-PLAN.md#b8-reference-private-jvm-advisory-check` (B8). Those original paths and their output are unavailable in this checkout. The [2026-11-25 Phase 1 public record](/feasibility/phase-01/#dependency-and-image-review) and the Phase 2 checks below document the observations that can be reproduced here.

### Public JVM selection evidence

```sh
mise exec python -- python3 tools/verify_dependency_evidence.py
# With the public artifacts already cached
mise exec python -- python3 tools/verify_dependency_evidence.py --offline
```

The verifier uses disposable build sources to record Gradle `dependencies`, `dependencyInsight` and selected graph edges. It compares the checked-in graph, a baseline with only the ordinary Guava bounds removed, and the restored graph. The BFF unit and component tests, fixture isolation, ktfmt, probe unit tests and KDoc fixture run across those states. Probe integration compile and runtime graphs are included. The Docker-backed integration suite is opt-in and its runtime needs separate evidence.

| Scope                                                | Selection and incoming paths                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Probe main, unit and integration compile and runtime | Boot manages gRPC at `1.84.1`. The Axon Java transport `2026.1.1` leads to the gRPC graph. The compile classpaths expose `grpc-stub` as the incoming Guava edge. Runtime also exposes `grpc-api` and other gRPC modules. They request `33.6.0-android`, and the ordinary probe implementation constraint selects component `33.8.0-android` by conflict resolution. Gradle reports `jreApiElements` for compile and `jreRuntimeElements` for runtime. |
| `:bff:ktfmtTool` and `:probe:kdocFormatter`          | ktfmt `0.65` brings Guava `33.5.0-jre`, and its google-java-format `1.23.0` path brings `32.1.3-jre`. The ordinary formatter constraint selects `33.8.0-jre` by conflict resolution.                                                                                                                                                                                                                                                                  |
| BFF main, unit and component compile and runtime     | The full graphs stayed equal across the removal and restoration controls, with no selected Guava in these classpaths.                                                                                                                                                                                                                                                                                                                                 |
| BFF detekt, probe Kotest and probe JVM TypeID        | The graph checks cover these independent tool and suite configurations as additional controls.                                                                                                                                                                                                                                                                                                                                                        |

The build maintainer owns both Guava bounds and reviews them by **2026-12-01** or sooner after a relevant upstream or BOM change. The unconstrained gRPC and formatter graphs select versions affected by GHSA-xxph-c9ww-hj94 / CVE-2026-102554. Remove each bound when the upstream graph independently selects a compatible fixed release, the affected and control comparisons and applicable tests pass, and the applicable private review has run. [Guava advisory](https://github.com/advisories/GHSA-xxph-c9ww-hj94)

The selected Spring Boot `4.2.0` BOM POM declares pgJDBC `42.7.14`. The observed BFF and probe application and test graphs select no `org.postgresql:postgresql` artifact. The build maintainer rechecks by **2026-12-01**, at first consumption and after each Boot change. Confirm the driver selected in real consuming role, worker and test graphs. Prefer the BOM when it supplies `42.7.15` or a verified newer fix. If the BOM still selects an affected version for a real consumer, add a scoped explicit version and remove it when the BOM independently selects a fixed version and the consuming checks pass. [pgJDBC 42.7.15 release](https://github.com/pgjdbc/pgjdbc/releases/tag/REL42.7.15)

### Image and npm review

The build maintainer reviews the pinned Axon Server `2026.1.8` catalog entry by **2026-12-01** or sooner after an advisory or terms change. The Phase 1 report records the immutable index and both ARM64 and AMD64 child manifests and configs, the native ARM64 proof, and the terms governing the image and application artifacts. Before changing the pin, verify the replacement index, both children, current applicable terms and a fresh local runtime result. Phase 7 owns the first hosted AMD64 DCB runtime proof. PostgreSQL currently has no selected image. The build maintainer reviews this record by **2026-12-01** and verifies the selected index, both child manifests and configs, applicable terms and a fresh runtime test at first consumption. [Phase 1 versions and terms](/feasibility/phase-01/#applicable-terms)

Review each npm consumer's own manifest and lockfile. To change a package, verify its registry origin, version, integrity and support, regenerate the affected lock with the Gradle-managed npm, then run strict-peer `npm ci`, `npm ls --all` and the consuming checks. Review the resulting lock diff and audit coverage for that consumer. Keep this work within the public npm graph and registry advisory boundary.

On 2026-11-25, managed npm `12.2.3` ran `npm ls --all --json --offline` successfully against the installed public trees. It reported 28 direct web packages, Eleventy `3.1.8` for docs, Prettier `3.10.1` and git-format-staged `4.0.2` for style, no direct packages in the static probe, and two in the TypeID probe. This command checks the installed dependency tree and peer relationships. The dated npm advisory assessment below has its own scope.

The isolated TypeID probe selects `typeid-js@1.2.0` and its transitive `uuid@10.0.0`. The 2026-11-25 public npm audit reported two Moderate entries for the same underlying advisory. The fixture exercises the bundle's stringify and v7 paths, while GHSA-w5hq-g745-h8pq concerns v3, v5 and v6 supplied output buffers. Jetify's `^10.0.0` range cannot select the fix. The build maintainer reviews by **2026-12-02** and immediately if probe inputs or API use change. Retire the hold when a verified Jetify release resolves a fixed uuid, then repeat the audit and TypeID vector check. The application TypeID package decision is pending. [Phase 1 npm evidence](/feasibility/phase-01/#secondary-checks)

The web lock selects app and Storybook TypeScript `7.0.2`. Its package extension gives `@feature-sliced/steiger-plugin@0.8.2` tooling-only TypeScript `5.9.3` for `tsconfck@3.1.6` and its optional `^5.0.0` peer. The control without the extension passed strict install and failed `npm ls --all` with `ELSPROBLEMS` for `typescript@7.0.2`. The web tooling maintainer reviews by **2026-12-02** and whenever the Steiger plugin or config reader is upgraded. Remove the extension only after a disposable lock regenerated without it passes strict managed npm install, `npm ls --all`, native TypeScript compilation, and Steiger and Chromium checks.

### Private JVM advisory procedure (B8)

**B8 status: incomplete.** The authorized feed, scanner and private inputs were unavailable for this review. Keep the result open and escalate incomplete coverage immediately to the build maintainer.

1. Opt in only with an authorized scanner, current authorized feed and an authorized external local directory. From Gradle's selected resolution results, produce inventories of Maven coordinates for `:bff:runtimeClasspath`, `:probe:testRuntimeClasspath` and `:probe:integrationTestRuntimeClasspath`. Include selected transitives and selected platform/BOM metadata. Exclude project components. Add `:command:runtimeClasspath` and `:query:runtimeClasspath` when those modules exist.
2. Run the authorized scanner with the scoped inventories and feed. Record the checked revision, configurations, scan time, feed identity and time, scanner version, result and limitations in the authorized external local directory. Keep the full inventories, feed and results out of the repository, published site, CI and logs.
3. Repeat at least weekly and after dependency changes or relevant advisories. Escalate incomplete results and High or Critical findings immediately. Assess unrated findings individually against their evidence and exposure.

A complete no-match applies only to the examined inventories and feed. Scope excludes Gradle plugins, JDK and other toolchain inputs, npm and other non-Maven inputs, container images, operating-system packages and advisories absent from the feed. A public Gradle graph reproduction, an npm audit and a hosted dependency or image scan have their own evidence and coverage.
