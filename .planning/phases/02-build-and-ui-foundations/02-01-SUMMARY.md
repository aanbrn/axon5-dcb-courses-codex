---
phase: 02-build-and-ui-foundations
plan: "01"
subsystem: web
tags: [gradle, spring-boot, openapi, orval, zod, react, vite, playwright]
requires:
  - phase: 01-axon-server-and-toolchain-feasibility
    provides: Gradle wrapper, Java and Node version files, and the managed npm pattern
provides:
  - Live BFF role directory and its published OpenAPI file
  - Gradle-generated Fetch client with Zod validation and a runnable React selector
  - Opt-in Chromium tracer with a Boot JAR and production Vite bundle on loopback
affects: [02-02, 02-03, 02-04, 02-10]
tech-stack:
  added: [Spring Boot MVC, React, Vite, Orval Fetch, Zod, Playwright]
  patterns: [contract-first Gradle artifacts, managed npm ci, same-origin API proxy, supervised Chromium tracer]
key-files:
  created:
    - bff/build.gradle.kts
    - bff/src/main/kotlin/courses/bff/BffApplication.kt
    - bff/src/main/resources/static/openapi.json
    - web/build.gradle.kts
    - web/index.html
    - web/orval.config.ts
    - web/package-lock.json
    - web/package.json
    - web/src/app/main.tsx
    - web/src/shared/api/demoRoles.ts
    - web/test/role-tracer.mjs
    - web/tsconfig.json
    - web/vite.config.ts
  modified:
    - settings.gradle.kts
    - gradle/libs.versions.toml
key-decisions:
  - Keep the canonical OpenAPI file as the published Gradle artifact and Spring static resource.
  - Disable implicit npm lifecycle scripts and provision the pinned Chromium through an explicit task.
patterns-established:
  - Client generation uses the BFF contract artifact without building or starting the application.
  - The browser assertion compares the first proxied response with the direct BFF reply and the rendered selector.
requirements-completed: [FND-06, CQRS-04, UI-03, FND-02]
coverage:
  - id: D1
    description: The exact frontend package tuple resolves and installs with an unchanged lockfile.
    requirement: FND-02
    verification:
      - kind: other
        ref: "Official npm registry evidence, GSD package classifier, managed npm ci, and npm ls --depth=0"
        status: pass
    human_judgment: false
  - id: D2
    description: Gradle generates and builds the browser client from the canonical BFF artifact while the BFF is stopped.
    requirement: FND-06
    verification:
      - kind: integration
        ref: "env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :web:clean :web:webBuild"
        status: pass
    human_judgment: false
  - id: D3
    description: Chromium receives the live BFF reply and selects Alex Rivera from the generated-client-backed selector.
    requirement: UI-03
    verification:
      - kind: e2e
        ref: "web/test/role-tracer.mjs#selects a role from the first live BFF response"
        status: pass
    human_judgment: false
actuals:
  tokens: 35832
  tasks: 2
  commits: 2
commits: 2
plan_head_before: 1f7f8dcad359250da3718361a7baabba44704ff5
plan_head_after: 6aed3de5b169df7c260933e337ded6aeb6a65119
duration: 12m20s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 01: Serve a BFF Role Directory Through the Generated Browser Client Summary

**Chromium selected Alex Rivera in a React build populated by the live Spring BFF through a Gradle-generated Fetch client with Zod validation.**

## Performance

- Started 2026-11-25T12:23:56Z and completed implementation verification at 2026-11-25T12:36:16Z.
- Completed two tasks across 15 implementation files. The registry checkpoint had collected its read-only evidence by 2026-11-25T12:20:23Z.

## Accomplishments

- The BFF serves `GET /api/demo-roles` and its exact source contract at `/openapi.json`. The published OpenAPI operation requires an administrator and an ordered array of students. The live fixture returns Administrator, Maya Chen, and Alex Rivera.
- Gradle resolves the BFF contract as a file input to Orval. The generated client validates JSON at runtime, and the shared API rejects unsuccessful responses, unexpected media types, and duplicate role IDs.
- The React shell selects Administrator on first load, shows the BFF's returned names, and resolves its documentation links against `VITE_DOCS_BASE`. The separate default docs origin is `http://127.0.0.1:8081/`.
- `:bff:bootRun` and `:web:dev` are the development entry points. `VITE_BFF_ORIGIN` defaults to `http://127.0.0.1:8080`. `:web:roleTracer` provisions Chromium and uses an independently built Boot JAR and Vite bundle.

## Package Legitimacy and Measured Versions

The npm classifier assessed 33 names with 12 OK, 21 SUS, and zero SLOP. All ten installed direct candidates had exact official registry manifests with integrity hashes and publisher or repository evidence. The exact manifests declared no preinstall, install, or postinstall scripts. npmjs.com package pages returned HTTP 403, and the official npm registry and upstream publisher evidence resolved identity. The user explicitly approved the five active flags, each caused only by the classifier's age threshold. Later-wave candidates are outside this approval.

| Direct package | Exact version | Published UTC | Disposition |
| --- | --- | --- | --- |
| `orval` | 8.49.0 | 2026-11-22 | SUS, explicitly approved |
| `zod` | 4.6.7 | 2026-10-12 | OK |
| `react` | 19.3.1 | 2026-10-14 | OK |
| `react-dom` | 19.3.1 | 2026-10-14 | OK |
| `typescript` | 7.0.2 | 2026-07-08 | OK |
| `vite` | 8.3.8 | 2026-11-11 | SUS, explicitly approved |
| `@vitejs/plugin-react` | 6.3.0 | 2026-11-09 | SUS, explicitly approved |
| `@types/react` | 19.3.2 | 2026-11-25 | SUS, explicitly approved |
| `@types/react-dom` | 19.3.0 | 2026-09-09 | OK |
| `playwright` | 1.65.1 | 2026-11-13 | SUS, explicitly approved |

Gradle 9.9.2 ran on Temurin 25.0.5.1+2. The managed runner reported Node 26.13.1 and npm 12.2.3. In a disposable directory, normal peer resolution, `npm ci --ignore-scripts --no-audit --no-fund`, `npm ls --depth=0`, Orval 8.49.0 generation, native TypeScript 7.0.2 compilation, and Vite 8.3.8 bundling all passed. These are observed versions. Publisher engine and peer ranges informed the selection.

The lockfile SHA-256 remained `265a68b1127838d40126679373f6b2004a97e6e8c6284234d4faa98215689b12` across disposable and repository installs. The lock marked `esbuild` and `fsevents` as having install scripts. The qualified app build uses the locked platform packages with lifecycle scripts disabled. Playwright installs Chromium explicitly.

## Browser Results and TDD Gate Compliance

| Check | Observed result |
| --- | --- |
| RED, managed Node with the TAP reporter on `web/test/role-tracer.mjs` | Exit 1, one named test failed. Chromium opened a listening baseline shell and reached the assertion that the first directory GET must succeed. GSD classified the complete TAP record as `RED_EVIDENCE_OK`. |
| GREEN and feedback gate, `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :web:provisionBrowser :web:roleTracer` | Exit 0 before and after the GREEN commit. Chromium 159.0.8154.6 received the actual BFF reply, displayed the returned roles in order, and selected Alex Rivera. The run used an isolated `PLAYWRIGHT_BROWSERS_PATH` and npm cache. |
| Controlled negative, same tracer with `ROLE_TRACER_STOP_BFF=1` | Exit 1 on the first live GET assertion after the real BFF had started and exited. |
| Controlled negative, same tracer with a disposable Vite bundle | Exit 1 on DOM versus BFF directory equality. The served bundle rendered Alex R. while the real BFF still returned Alex Rivera. |
| `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :web:clean :web:webBuild` | Exit 0 with the BFF stopped. Gradle regenerated the client, typechecked it, and rebuilt the production bundle. The log contained only web tasks and the lock bytes matched. |
| Packaged OpenAPI and Kotlin formatting | The contract inside `bff.jar` matched its source file byte for byte. The existing ktfmt 0.65 configuration formatted the new Kotlin source before the final browser checks. |

## Task Commits

1. **Registry review** completed as a read-only task.
2. **Live role tracer** RED in `8adb4bc`, followed by GREEN in `6aed3de`.

## Deviations from Plan

- **[Rule 3 - Build configuration]** Added the Spring Boot plugin alias in `gradle/libs.versions.toml` so the plugin and BOM share the existing Boot 4.2.0 version. Gradle 9.9.2 rejected declaring dependencies directly on a resolvable configuration. The web graph now declares dependencies in dedicated dependency scopes and resolves the contract and Boot JAR lazily. Committed in `6aed3de`.
- **[Rule 3 - Disposable lock resolution]** The initial npm `--prefix` trial generated paths relative to the repository. Regenerating from the physical disposable working directory produced portable `node_modules/` paths with the same exact direct versions and normal peers.
- **[Rule 1 - Smoke readiness]** The first real Gradle smoke exposed a Fetch readiness check that called `Response.ok` as a function. Correcting it to the Fetch property let the query reach the real Chromium assertions. Committed in `6aed3de`.
- **[Rule 3 - State bookkeeping]** GSD could not advance the legacy `Plan: Not started` field. Restoring the current plan and total fields let its standard command advance the position to 2 of 11.

## Outstanding Evidence

The Kotlin plugin emits a duplicate-load warning for `:probe` and `:bff` during configuration. The shared JVM convention work in 02-02 can consolidate plugin application. Integration of the root build and failure injection against the generated client continue in 02-10. The broader requirement evidence also includes later documentation, UI state, and tool inventory plans.

## Self-Check: PASSED
