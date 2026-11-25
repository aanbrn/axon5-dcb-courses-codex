# Phase 01: Axon Server and Toolchain Feasibility - Pattern Map

- **Mapped:** 2026-11-24
- **Scope:** FND-01
- **Path groups classified:** 12
- **Tracked implementation analogs:** 0

`git ls-files` showed only planning documents, `AGENTS.md`, and `.gitignore`. There are no tracked Gradle, JVM, Node, container, or test implementations to copy. The paths below describe the proposed Phase 1 footprint. The planner can choose the filenames and package structure for the probe code.

## File Classification

| New path or path group | Role | Data flow | Closest analog |
| --- | --- | --- | --- |
| `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.{jar,properties}` | config | file-I/O | None |
| `settings.gradle.kts`, `build.gradle.kts` if needed, `gradle/libs.versions.toml`, `probe/build.gradle.kts` | config | batch | None |
| `.java-version`, `.nvmrc`, `mise.toml` | config | file-I/O | None |
| Probe-local Kotlin contracts and fixtures | model | transform | None |
| Probe-local Spring Boot role entry points and Axon client configuration | config | request-response | None |
| Probe-local command logic and query/projection logic | service | request-response, event-driven | None |
| `probe/src/integrationTest/` driver, container/JVM lifecycle support, and DCB assertions | test | request-response, streaming | None |
| `probe/src/test/` ordinary smoke test | test | batch | None |
| Probe-local secondary Kotlin/TypeScript TypeID samples, shared vectors, Kotest sample, and ktfmt/KDoc specimen | test | transform, batch | None |
| Probe-local web samples including `package.json`, `package-lock.json`, static inputs, and packaging verification | test, config | file-I/O, request-response | None |
| `probe/README.md` run guide | documentation | file-I/O | None |
| Permanent Phase 1 report outside `probe/` | documentation | file-I/O | None |

## Pattern Assignments

- **Bootstrap and tasks.** Use `01-RESEARCH.md:117-122` for wrapper and catalog setup, and `01-RESEARCH.md:218` for task isolation. Use the wrapper distribution checksum and an explicit Docker-backed integration entry point. Keep the Docker and image packaging tasks outside the ordinary build graph.
- **DCB and transport.** Use `01-RESEARCH.md:168-172` for clean server startup and role wiring. Follow `01-RESEARCH.md:196-201` for the ordered proof. Await the initial remote subscription value, source the stale writer's marker, await the winning two-tag write, and verify the overlapping append rejection at the actual commit boundary. Confirm both tags resolve the same persisted event and verify the correlated update on the remote subscription. Bound waits and release the subscription, child JVMs, and container on exit.
- **Secondary checks.** Use the separate samples and assertion targets in `01-RESEARCH.md:298-315`. Use shared TypeID vectors, a Jupiter test with Kotest helpers, and an isolated KDoc specimen. Gradle runs `npm ci` and produces static assets. Pack consumes the staged assets and the verification compares them with the HTTP response.
- **Run guide and report.** Use D-03, D-04, and D-07 through D-13 in `01-CONTEXT.md:23-44`. Capture repeatable commands in the module guide. Preserve the selected tuple, terms, ARM64 runtime results, ARM64 and AMD64 image metadata, and secondary outcomes in the permanent report. Treat published versions in research as candidates until execution validates them.

## Shared Patterns

- **Version ownership** (`.planning/PROJECT.md:132-140`, `01-RESEARCH.md:117-122`). The wrapper owns Gradle. The catalog owns Gradle inputs, including images. `.java-version` owns the Temurin feature version and the report records the observed patch/build. `mise.toml` owns selected independent CLIs. `.nvmrc` owns Node, `packageManager` owns npm, and `package-lock.json` owns npm dependency resolution. Workflow SHA pins apply in the hosted CI phase.
- **Local artifacts** (`.gitignore:10-37`). Keep generated output in the existing ignored directories and keep credentials and diagnostic logs local. The tracked entries include:

  ```gitignore
  .gradle/
  .kotlin/
  build/
  out/
  *.class
  ```

- **Project conventions** (`AGENTS.md:11-21,31-40`). Use idiomatic Kotlin, preserve role boundaries within the temporary proof, organize JVM tests with Gradle JVM Test Suites, and write repository artifacts in English. Shared build conventions, the real application, and hosted workflows belong to later phases.

## No Analog Found

All 12 path groups require new files. The tracked planning documents supply decisions and research references for the implementation.
