---
phase: 02-build-and-ui-foundations
plan: "10"
subsystem: build
tags: [gradle, openapi, orval, zod, typescript, node-test]
requires:
  - phase: 02-01
    provides: Canonical BFF OpenAPI artifact, generated Fetch client, and approved frontend lockfile
  - phase: 02-02
    provides: BFF HTTP contract suite and verified root Kotlin plugin declarations
provides:
  - Provider-backed root BFF and web lifecycle
  - Isolated clean, deleted-output, and changed-contract build checks
  - Managed Node tests for the production role directory adapter
affects: [02-03, 02-04, 02-09, 03]
tech-stack:
  added: []
  patterns: [Gradle task providers, disposable build controls, managed Node TAP with Vite module loading]
key-files:
  created: [build.gradle.kts, web/test/client-graph.py, web/test/generated-client.test.ts]
  modified: [web/build.gradle.kts, web/src/shared/api/demoRoles.ts]
key-decisions:
  - Load the Kotlin plugins in the root classpath and aggregate the BFF and web lifecycles using task providers.
  - Use the managed Node test runner with the existing Vite module loader and preserve the approved npm inputs.
  - Reject Fetch redirects so the documented status is checked at the original operation URL.
patterns-established:
  - Verify both the producing task outcome and the generated file bytes before and after a disposable contract mutation.
  - Exercise generated response validation through the production adapter and retain actual TAP failures for fault injection.
requirements-completed: [FND-06, CQRS-04]
coverage:
  - id: D1
    description: A clean root build produces the executable BFF JAR and Vite assets and executes the BFF and web checks.
    requirement: FND-06
    verification:
      - kind: integration
        ref: "python3 web/test/client-graph.py --clean"
        status: pass
    human_judgment: false
  - id: D2
    description: Contract-only generation rejects remote references, restores deleted files, and invalidates consumers when the operation changes.
    requirement: FND-06
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :web:verifyClientGraph"
        status: pass
    human_judgment: false
  - id: D3
    description: The production adapter enforces the role directory contract through the generated Fetch operation.
    requirement: CQRS-04
    verification:
      - kind: unit
        ref: "./gradlew --console=plain :web:webCheck"
        status: pass
      - kind: integration
        ref: "web/test/generated-client.test.ts#rejects a redirect to a valid role directory"
        status: pass
    human_judgment: false
actuals:
  tokens: 7172
  tasks: 2
  commits: 3
commits: 3
plan_head_before: 83b7008c34059b8730c1c8994de7e4898e682a64
plan_head_after: 11ad528b8895bedb57bf9c3b3d868cb284edf82c
duration: 12m14s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 10: Qualify the Root Build and Generated Client Contract Summary

**A clean root Gradle build assembles the BFF and web from the checked-in contract, and the generated Fetch path rejects corrupt or redirected role directories.**

## Performance

- Started at 2026-11-25T13:02:15Z and finished the implementation commits at 2026-11-25T13:14:29Z.
- Completed two tasks across five implementation files.

## Accomplishments

- Root `clean`, `assemble`, and `check` resolve the BFF and web lifecycle task providers. `:web:check` runs native TypeScript and the managed Node HTTP contract tests. Docker-dependent probes and browser provisioning are opt-in.
- The build proof copies the sources into a disposable directory with private build and npm outputs. It checks actual task outcomes, generated client and schema files, Vite's referenced JavaScript asset, and exact OpenAPI bytes in the executable BFF JAR.
- `:web:webCheck` runs the generated Fetch operation through the production adapter. Tests cover ordered directories with zero, one, or two students, required fields, nonempty fields, role discriminators, duplicate IDs, malformed JSON, exact media type and success status, and a real HTTP redirect to a valid replacement response.
- The approved `web/package.json` and `web/package-lock.json` are byte-identical to 02-01. Managed npm uses `ci` with package lifecycle scripts disabled. The observed lockfile SHA-256 was `265a68b1127838d40126679373f6b2004a97e6e8c6284234d4faa98215689b12` throughout the disposable runs.

## Task Commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-10-01 | `0cafdcf` | Root lifecycle and isolated clean build proof |
| 02-10-02 RED | `ade53d3` | Managed Node witnesses for the generated role directory client |
| 02-10-02 GREEN | `11ad528` | Graph invalidation and recovery, root HTTP checks, and redirect rejection |

## Verification

Tests ran with Gradle 9.9.2, Temurin 25.0.5.1+2-LTS, Node 26.13.1, npm 12.2.3, Orval 8.49.0, and native TypeScript 7.0.2. The disposable runs set `DOCKER_HOST=tcp://127.0.0.1:1` and used a fresh browser cache path. No step provisioned a browser. The generation-only task list contained just the included build and managed Node/npm/generation tasks. The BFF’s own component tests use a loopback Spring server during root `check`.

| Verification | Observation |
| --- | --- |
| `python3 web/test/client-graph.py --clean` | Exit 0, including the tracer feedback run and the final run with `:web:webCheck`. Gradle ran generation, native typecheck, and production bundling in order. The final clean build ran BFF unit and component checks and all 19 web tests. |
| Disposable disconnection in `--clean` | `:web:typecheck` exited nonzero with `TS2307` for `../../../build/generated/client`. The generated directory stayed absent. |
| `./gradlew --console=plain :web:verifyClientGraph :web:webCheck` | Exit 0 in 33 seconds. The unchanged generator was `UP-TO-DATE`. Deleting only its output made it execute and restore the original generated bytes. The Vite bundle remained available. |
| Disposable external reference in `:web:verifyClientGraph` | Orval rejected the loopback `$ref` with `External $ref targets are not allowed by default.` before fetching. In-document references generated successfully. [Orval input configuration](https://orval.dev/docs/reference/configuration/input/) |
| Disposable operation rename in `:web:verifyClientGraph` | Generation emitted `listRenamedDemoRoles`. Native TypeScript reported `TS2305` for the old `listDemoRoles` export, and bundling did not run. Restoring the original contract bytes rebuilt the client and the bundle. |
| `./gradlew --console=plain :probe:test :web:generateClient` and `./gradlew --console=plain build --dry-run` | The unchanged Phase 1 unit suite passed one test, and the duplicate Kotlin plugin-load warning disappeared. The ordinary `build` selected the BFF and web lifecycle checks and the Phase 1 unit test. It selected no probe integration or browser provisioning tasks. |

## TDD Gate Compliance

- **RED.** Managed Node `--test --test-reporter=tap test/generated-client.test.ts` exited 1 with 18 passes and one failure. The named redirect test executed a loopback HTTP 302 and failed at `Missing expected rejection (TypeError)` because Fetch returned the valid replacement directory. GSD accepted the unmodified TAP report as `RED_EVIDENCE_OK`.
- **GREEN.** The same assertions passed through `:web:webCheck` with 19 passed and zero failed or skipped. The real redirect fixture observed zero requests to the replacement endpoint.
- **Generated-validator bypass.** In the disposable client, replacing the Zod call with the raw parsed body caused all three filtered TAP cases to fail. The missing administrator produced a `TypeError` instead of the expected `ZodError`. The empty label and wrong discriminator returned malformed payloads and failed their rejection assertions. The original generated bytes were restored after the control.
- The raw TAP records and Gradle logs are retained locally under the ignored `.gsd/tdd-evidence/02-10/` directory.

## Deviations from Plan

- **[Rule 3 - Build configuration]** Task 1 applied the three root plugin declarations already qualified in 02-02. The original `:probe:test` passed and the Kotlin duplicate-loader warning was absent. The Phase 1 sources and version owners remained untouched. Committed in `0cafdcf`.
- **[Rule 1 - HTTP boundary]** Task 2 found that the generated Fetch call followed redirects by default and could accept a 200 from a different endpoint. The production adapter now passes `redirect: "error"`. The loopback RED and GREEN records show both outcomes. Committed in `11ad528`.

## Outstanding Evidence

Plan 02-04 adds the documentation build to the root lifecycle. The later UI, tool inventory, and hosted CI plans carry the remaining phase-level evidence. The 02-10 build and HTTP acceptance checks are complete.

## Self-Check: PASSED
