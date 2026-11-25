# Phase 02 — Build and UI Foundations Pattern Map

**Mapped:** 2026-11-25

**Coverage:** 15 file groups, 10 with tracked analogs. Proposed paths and grouped globs describe planning scope. The planner can choose exact filenames within each group.

## File Classification

| New or modified file group | Role | Data flow | Closest tracked analog | Match |
| --- | --- | --- | --- | --- |
| `settings.gradle.kts`, root `build.gradle.kts` | config | batch | `settings.gradle.kts:1-15` | role |
| `gradle/libs.versions.toml`, `mise.toml` | config | batch | Same files, catalog `1-12,25-45`, mise `1-2` | exact |
| `build-logic/**` and BFF JVM build configuration | config | batch | `probe/build.gradle.kts:9-22,84-118,152-158,262-287` | role |
| Fixture producer build and `src/testFixtures/kotlin/**` | test | transform | `probe/src/integrationTest/kotlin/probe/ProbeFixture.kt:47-66,198-220` | partial |
| `bff/src/main/resources/openapi.json`, Boot entry point, controller and wire models | controller, config, model | request-response, file-I/O | — | none |
| `bff/src/test/kotlin/**`, `bff/src/componentTest/kotlin/**` | test | request-response, transform | `probe/src/test/kotlin/probe/ProbeContractsTest.kt:3-26`, `probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt:3-26` | role |
| `web/build.gradle.kts`, `docs-site/build.gradle.kts`, both `package.json` and `package-lock.json` pairs | config | batch | `probe/web/build.gradle.kts:49-120`, `probe/web/package.json:2-7` | role |
| `web/orval.config.*`, Vite, TypeScript, Steiger and shadcn configuration | config | transform, batch | — | none |
| `web/src/app/**`, `pages/home/**`, `shared/api/**`, `shared/ui/**` | component, hook, service | event-driven, request-response | — | none |
| `web/.storybook/**`, browser unit, story and smoke tests | config, test | event-driven, request-response | — | none |
| `docs-site` Eleventy config, templates, assets and output checks | config, component, test | file-I/O, transform | — | none |
| `docs/feasibility/phase-01.md`, quick start, maintainer guide and inventory | documentation | file-I/O | `docs/feasibility/phase-01.md:37-74,128-151`, `probe/README.md:1-36` | role |
| Shared style Gradle tasks, rules, formatter driver, `.githooks/pre-commit` and Git acceptance fixture | config, utility, test | file-I/O, transform | `probe/build.gradle.kts:262-328` for Kotlin formatter only | partial |
| `doctor` task and diagnostic implementation | utility | batch | `probe/web/build.gradle.kts:71-99`, `probe/src/test/kotlin/probe/ProbeContractsTest.kt:24-28` | partial |
| `.github/workflows/*.yml` PR build | config | event-driven | `probe/README.md:27-42` for command separation only | partial |

## Pattern Assignments

### Root build, JVM conventions, suites and fixture producer

`settings.gradle.kts:1-15` owns repository resolution and module registration. Keep application modules in the root build. Use one catalog across the convention build and consumers. `gradle/libs.versions.toml:25-45` puts BOM-managed coordinates next to aliases that use `version.ref` for explicitly owned versions. `mise.toml:1-2` gives independent CLIs their own owner.

`probe/build.gradle.kts:15-22,152-158` shows the toolchain owner and the suite dependency pattern.

```kotlin
val javaFeature = providers.fileContents(rootProject.layout.projectDirectory.file(".java-version"))
    .asText.map { it.trim().toInt() }

java {
    toolchain {
        languageVersion = javaFeature.map(JavaLanguageVersion::of)
        vendor = JvmVendorSpec.ADOPTIUM
    }
}
```

```kotlin
register<JvmTestSuite>("kotestProbe") {
    useJUnitJupiter(libs.versions.junit.get())
    dependencies {
        implementation(libs.coroutines.core)
        implementation(libs.kotest.assertions)
        implementation(libs.kotest.property)
    }
```

Reuse the Jupiter runner and suite-scoped Kotest dependencies. `probe/src/kotestProbe/kotlin/probe/KotestInteropTest.kt:13-26` uses a backtick behavior name and `checkAll(PropTestConfig(seed = seed, iterations = iterations), ...)`. `probe/src/test/kotlin/probe/ProbeContractsTest.kt:3-23` exercises actual serialized bytes with Jackson 3 and checks that case-sensitive IDs survive. Use that assertion discipline for BFF wire tests, with actual loopback HTTP and the published OpenAPI schema per research. `probe/src/integrationTest/kotlin/probe/ProbeFixture.kt:198-220` owns cleanup through `AutoCloseable`, preserves secondary errors and bounds process exit. Use the lifecycle idea where a fixture owns a process. Its Docker, Axon, environment isolation and evidence capture are specific to Phase 01. Cross-project `java-test-fixtures` publication, random-port Boot MVC testing and independent schema validation begin in Phase 02. The BFF component suite participates in `check`.

### Managed npm, generated client and static sites

`probe/web/build.gradle.kts:55-69,93-109` derives Node from `.nvmrc` and npm from `packageManager`. Preserve checked-in manifests and lockfiles and use the plugin-managed runner.

```kotlin
node {
    version = selectedNode
    npmVersion = selectedNpm
    download = true
    npmInstallCommand = "ci"
    nodeProjectDir = layout.dir(provider { npmDirectory })
}
```

`probe/web/build.gradle.kts:93-120` asserts lockfile bytes before and after install and declares manifests, lockfile, owners and versions as task inputs. Apply those edges with task-specific inputs and output directories. Add the BFF source contract as a provider-backed outgoing artifact for Orval, connect generation to web tasks that import the client, and stage only public content for Eleventy. The Phase 01 nested Gradle invocation (`probe/build.gradle.kts:331-350`) and probe markers are proof isolation. The Phase 02 web and docs builds are ordinary root subprojects.

### Kotlin documentation, verification and `doctor`

`probe/build.gradle.kts:262-287` provides an isolated formatter classpath. Preserve `libs.guava.jre` as a constraint in the formatter graph and use `org.jetbrains.kotlinx.ktfmt.cli.Main` with `--kotlinlang-style`.

```kotlin
val kdocFormatterImplementation = configurations.dependencyScope("kdocFormatterImplementation")
val kdocFormatter = configurations.resolvable("kdocFormatter") {
    extendsFrom(kdocFormatterImplementation.get())
}.get()
```

`probe/build.gradle.kts:300-321` compares actual formatted text and checks that the second pass is byte-identical. Use that proof for KDoc checks. The detekt comments config and Dokka warning gate are new. `probe/web/build.gradle.kts:71-90` compares actual output from managed Node and npm against declared versions. Apply that distinction in `doctor`, along with the Java worker checks in `probe/src/test/kotlin/probe/ProbeContractsTest.kt:24-28` and the optional tool split in `probe/README.md:27-42`.

### Published content and maintainer evidence

Use `probe/README.md:1-36` as a runbook pattern for prerequisites, root-relative wrapper commands, expected output and optional checks. Use `docs/feasibility/phase-01.md:58-74,128-145` for version and dependency evidence. Its `dependencyInsight` examples name the actual classpath, distinguish observed selections from BOM metadata, and record the limited scope of private checks. Keep the feasibility Markdown as the report's source. Reconcile the handoff in `docs/feasibility/phase-01.md:147-151` with Context D-15, which places hosted AMD64 DCB runtime proof in Phase 07 and retains the existing retirement criteria.

## Shared Patterns

- **Scope dependencies to actual consumers.** `gradle/libs.versions.toml:7-8,26-37` separates constraint aliases from BOMs. `probe/build.gradle.kts:262-273` confines the formatter constraint to its own resolvable graph. Apply the same scope discipline to build tools and test fixtures.
- **Keep ordinary and infrastructure verification separately runnable.** `probe/build.gradle.kts:89-118,345-350` defines separate tasks and `probe/README.md:27-42` documents the Docker prerequisite for the packaging proof. Phase 02's clean PR build includes the BFF HTTP suite and static artifacts. Hosted DCB runtime proof follows in Phase 07.
- **Verify bytes at the boundary.** The lockfile check in `probe/web/build.gradle.kts:93-99` and serialization test in `probe/src/test/kotlin/probe/ProbeContractsTest.kt:15-23` exercise observed bytes. Apply the principle to the served OpenAPI file, same-source staged Markdown and staged Git blobs.

## No Analog Found

- **BFF and contract.** The tracked Axon probe fixtures have no MVC endpoint or authored OpenAPI contract. Use Research architecture §§1–2 for the HTTP and code generation patterns. Demo selection is tab-local persona state and needs no auth or guard pattern.
- **React and Storybook.** The tracked static probe builds a standalone asset. Use the approved UI-SPEC and Research §3 for FSD placement, states, keyboard and retry focus behavior, and story tests. The generated Fetch adapter owns transport and schema failures. The page reconciles storage after a successful directory response.
- **Docs-site templates and checks.** Markdown content and Gradle npm tasks have analogs. Eleventy layouts, URL bases, input allowlisting and link checks start here. Use Research §4 and the UI-SPEC navigation contract.
- **Hook and CI implementation.** There are no tracked Git hooks or Actions workflows. Use Research §§6–7 for a shared staged/full rule policy, partially staged files, read-only PR permissions, pinned Actions and wrapper validation. Keep shell and package lockfile policies owned by the selected tools.

## Metadata

Search scope comprised tracked root and Gradle launch, version and build files, Phase 01 JVM and web probe sources, and the runtime documentation under `probe/` and `docs/feasibility/`. The tracked path inventory showed no existing `bff/`, `web/`, `docs-site/`, `.githooks/`, or `.github/` source. Pattern evidence is from source inspection.
