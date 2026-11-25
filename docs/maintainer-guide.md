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
| Independent CLIs                        | [mise configuration](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/mise.toml)                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| GitHub Actions                          | Each external action uses a full commit SHA in its [workflow](https://github.com/aanbrn/axon5-dcb-courses-codex/tree/main/.github/workflows). Doctor reports the pins it can read from the checkout.                                                                                                                                                                                                                                                                                                                                                                |

## Setup and diagnostics

Use an ARM64 or AMD64 host running macOS or Linux with Git, a POSIX shell, Python 3.11 or newer and mise. Install Eclipse Temurin at the feature release in `.java-version` and point `JAVA_HOME` at that JDK. Gradle uses an Eclipse Adoptium toolchain for the BFF JVM suites. The complete vendor, patch and build strings in doctor are observations. The version file stays feature-only.

```sh
mise install ruff taplo
mise exec ruff taplo -- ./gradlew --console=plain doctor
```

Doctor reports required checks for the regular build and repository style, plus additional checks for Docker, Compose, Pack and the retained probe. A failing required row sets a nonzero exit status. A failing additional row identifies which optional workflow needs attention. The observed managed Node and npm versions come from starting the executables at the reported paths. On a fresh checkout, the regular build provisions them, or run the setup tasks for the consumer you need.

```sh
./gradlew npmSetup :web:npmSetup :docs-site:npmSetup
# For the independent Phase 1 probe only
./gradlew -p probe/web npmSetup
```

When `./gradlew` cannot start, run the same diagnostic in bootstrap mode. Resolve each required failure using its repair column, then rerun `doctor`. Bootstrap checks local inputs and the launcher, and marks Gradle, the BFF worker and managed Node/npm observations as deferred.

```sh
mise exec ruff taplo -- python3 tools/doctor.py
```

Run `./gradlew installGitHooks` to opt in to the staged-content hook. Run the full tracked-file check with `mise exec ruff taplo -- ./gradlew styleCheck`. Both entry points use the checked-in [style policy](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/tools/style/policy.json).

## Documentation build

```sh
./gradlew :docs-site:docsBuild
./gradlew :docs-site:serve -PdocsBase=/courses/
```

Gradle stages the public sources and renders the static site into `docs-site/build/site`. The optional `docsBase` is a deployment path with a leading and trailing slash. With `/courses/`, mount the output there. The local preview prints `http://127.0.0.1:8081/courses/` when it is ready.

For hosted deployments, provide an HTTPS `docsAppUrl` and include its origin in the comma-separated `docsTrustedAppOrigins` build setting. The local Vite origin `http://127.0.0.1:5173` is already allowed. Invalid values fail the build.

## Feasibility probe

The [probe build](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/build.gradle.kts) provides the opt-in DCB integration suite. Follow the [probe runbook](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/README.md) to reproduce the native proof. The [feasibility report](/feasibility/phase-01/#hosted-amd64-verification-and-retirement) records the evidence and conditions for retiring the probe.
