<!-- GSD:project-start source:PROJECT.md -->

## Project

**Axon 5 DCB Courses**

A reference implementation of students subscribing to courses, built on Axon Framework 5 using Dynamic Consistency Boundaries (DCB) instead of aggregates and inspired by “Killing the Aggregate.” It is a learning example held to production-grade standards in architecture, code, tests, documentation, CI/CD, and observability. It serves developers moving from Axon 4, the author’s own deep learning, and a public portfolio or article.

**Core Value:** Show, with working code, tests, and documentation, how DCB enforces cross-entity business invariants without aggregates and what trade-offs it offers versus an aggregate-based approach.

### Constraints

- Use Kotlin, Spring Boot, and Axon Framework 5 on the backend. Prefer idiomatic Kotlin to Java-style translations.
- Run Axon Server with DCB support in Docker.
- Separate command, query/projection, automation, and REST BFF services by responsibility.
- Use React and TypeScript with Feature-Sliced Design (FSD), checked by Steiger.
- Use Gradle JVM Test Suites and Java Test Fixtures to organize test levels and reuse test helpers.
- Name Kotlin test methods with short English phrases in backticks that describe the expected behavior.
- Auto-format and style-check all repository artifacts through a local pre-commit hook and in CI.
- Use one Docker Compose setup for the full local system.
- Hold code, tests, documentation, CI, and observability to reference-quality standards.
- Write code, docs, and repository artifacts in English.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Backend and Event Store

## Build, Tests, and Frontend

| Area                 | Direction                                                                                                                                                                                                                  | Verification evidence                                                                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gradle and tools     | Wrapper, catalog, Temurin feature version, mise, Node version file, package metadata and lockfile, and SHA-pinned Actions each own their inputs.                                                                           | Record the observed JDK patch/build in the Phase 1 probe. Verify the clean build and inventory in Phase 2.                                                                 |
| JVM tests            | JUnit 6 runner with Kotest assertions and property checks. Organize Gradle JVM Test Suites and share Kotlin helpers through Java Test Fixtures. Run Testcontainers against the selected Axon Server and PostgreSQL images. | Run a small Kotlin and Kotest check in Phase 1 and exercise shared fixtures in Phase 2. Verify application behavior with the integration suites as the services are built. |
| TypeID               | Use type-prefixed UUIDv7 IDs in contracts and native UUID storage.                                                                                                                                                         | Compare Kotlin and TypeScript test vectors in Phase 1. Prove the application UUID round trip in Phase 3.                                                                   |
| Web build            | Use the Gradle Node plugin for React/TypeScript and the docs site. Make OpenAPI generation, client generation, and frontend build explicit task inputs and outputs.                                                        | Regenerate the client from a clean build in Phase 2.                                                                                                                       |
| JVM images           | Use Spring Boot `bootBuildImage` with a Paketo builder.                                                                                                                                                                    | Build and run the application role images in Phase 5.                                                                                                                      |
| Frontend image       | Use Gradle and `npm ci` to build static assets. Package those assets with Paketo Web Servers.                                                                                                                              | Probe the packaging and serving path in Phase 1 and use it for the application image in Phase 5.                                                                           |
| Documentation checks | Use ktfmt for Kotlin/KDoc, detekt `comments` rules, and Dokka warnings as errors.                                                                                                                                          | Check ktfmt against a representative KDoc sample in Phase 1. Exercise the shared style and documentation checks in Phase 2.                                                |

## Tooling for Delivery

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `$gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `$gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `$gsd-debug` for investigation and bug fixing
- `$gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `$gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.

<!-- GSD:profile-end -->
