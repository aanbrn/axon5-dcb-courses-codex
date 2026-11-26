---
phase: quick-261126-fhh
plan: "01"
subsystem: build
tags: [mise, java, node, gradle, documentation]
requires: []
provides: [Mise developer commands using the canonical Java and Node.js version files]
affects: [local development, maintainer guide]
tech-stack:
  added: []
  patterns: [Checkout-scoped idiomatic version discovery]
key-files:
  created: []
  modified: [mise.toml, docs/maintainer-guide.md]
key-decisions:
  - Use `.java-version` for the Temurin feature version and `.nvmrc` for the Node.js version.
requirements-completed: [FND-02]
commits: 1
plan_head_before: bb454a021f0148cd61575015896fb3aa1b6267b2
plan_head_after: d92322eb78efcb6559327c6ddee9fe426ec77806
duration: 5min
completed: 2026-11-26
status: complete
---

# Quick Task 261126-fhh Summary

Mise selects Eclipse Temurin from `.java-version` and Node.js from `.nvmrc` for local commands. The maintainer guide explains how to install, invoke and inspect both runtimes. Gradle continues to provision Node.js and npm for its consumers, and `mise.toml` owns the Pack, Ruff and Taplo pins.

## Verification

| Check | Result |
| --- | --- |
| `mise install java node` and `mise ls --current` on mise 2026.11.14 | Both runtimes were already installed. The listing selected Java feature `25` from `.java-version` and Node.js `26.13.1` from `.nvmrc`. |
| `mise exec java node -- java -XshowSettings:properties -version` | The mise executable reported Eclipse Adoptium, Java feature `25` and Temurin build `25.0.5.1+2-LTS`. |
| `mise exec java node -- node -p 'process.versions.node'` | The mise executable reported `26.13.1`. |
| `mise exec java node -- ./gradlew --no-daemon --console=plain --version` | Gradle `9.9.2` used the mise Temurin for the launcher and daemon. |
| Scratch config with conflicting `.sdkmanrc`, `.node-version` and `package.json` | Mise continued to select the two canonical files. |
| `mise exec ruff taplo -- ./gradlew --no-daemon --console=plain styleCheck doctor` | The full tracked style check passed. Doctor passed all checks, including Ruff `0.17.4`, Taplo `0.10.0` and Gradle-managed Node.js `26.13.1` and npm `12.2.3`. |
| `./gradlew --no-daemon --console=plain :docs-site:docsCheck` | All 14 tests passed, and the rendered guide contains the mise commands. |
| Temporary mise data directory containing only Ruff and Taplo | The scoped style command preserved the incoming `JAVA_HOME`. The mise environment export supplied no `JAVA_HOME`, and no Java, Node.js or Pack installations appeared. This models the existing style setup on a fresh CI runner. |

## Compatibility and rollback

When the mise JDK is installed, `mise exec ruff taplo` also sets `JAVA_HOME` to that JDK. To use the shell's existing JDK for one style or diagnostic command, prefix `mise exec ruff taplo` with `MISE_DISABLE_TOOLS=java,node`. The prefix preserved the incoming `JAVA_HOME` in the local check. Explicit installation of Java feature `25` required online Temurin version resolution even with the selected build already installed. The runtime and build verification used checkout-scoped trust and temporary mise state.

## Task commit

`d92322e` enables the canonical runtime files and updates the maintainer guide. The checkout's optional Git hook was unconfigured, and the equivalent full tracked style check passed before the commit.

## Self-Check: PASSED

Both changed files are present in the task commit, and the measured range contains one commit.
