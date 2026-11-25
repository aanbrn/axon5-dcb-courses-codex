---
title: Maintainer guide
layout: page.11ty.js
---

# Maintainer guide

## Version owners

| Tool or dependency | Source |
| --- | --- |
| Gradle distribution and checksum | [Wrapper properties](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/gradle/wrapper/gradle-wrapper.properties) |
| Gradle plugins, dependencies and images | [Version catalog](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/gradle/libs.versions.toml) |
| Eclipse Temurin feature version | [JDK version file](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/.java-version) |
| Node.js | [Node version file](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/.nvmrc) |
| npm version and dependency resolutions | [Web manifest](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/web/package.json), [web lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/web/package-lock.json), [docs manifest](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/docs-site/package.json), [docs lockfile](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/docs-site/package-lock.json) |
| Independent CLIs | [mise configuration](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/mise.toml) |

## Documentation build

```sh
./gradlew :docs-site:docsBuild
./gradlew :docs-site:serve -PdocsBase=/courses/
```

Gradle stages the public sources and renders the static site into `docs-site/build/site`. The optional `docsBase` is a deployment path with a leading and trailing slash. With `/courses/`, mount the output there. The local preview prints `http://127.0.0.1:8081/courses/` when it is ready.

For hosted deployments, provide an HTTPS `docsAppUrl` and include its origin in the comma-separated `docsTrustedAppOrigins` build setting. The local Vite origin `http://127.0.0.1:5173` is already allowed. Invalid values fail the build.

## Feasibility probe

The [probe build](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/build.gradle.kts) provides the opt-in DCB integration suite. Follow the [probe runbook](https://github.com/aanbrn/axon5-dcb-courses-codex/blob/main/probe/README.md) to reproduce the native proof. The [feasibility report](/feasibility/phase-01/#hosted-amd64-verification-and-retirement) records the evidence and conditions for retiring the probe.
