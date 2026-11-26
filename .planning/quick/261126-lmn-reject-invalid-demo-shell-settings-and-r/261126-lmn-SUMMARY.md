---
phase: quick-261126-lmn
plan: "01"
subsystem: demo shell and role directory
tags: [vite, gradle, openapi, kotlin, zod, playwright]
requires:
  - phase: "02"
    provides: The Gradle-managed shell, contract generation, BFF and browser smoke suites
provides:
  - Documentation URL validation during Vite configuration
  - Aligned role string checks in the BFF, independent schema validator and generated client
  - Immutable ordered server directory with exact, case-sensitive IDs
affects: [FND-06, CQRS-04, UI-03]
tech-stack:
  added: []
  patterns:
    - Vite define replacement for the normalized documentation base
    - Explicit ECMAScript whitespace set across JVM and browser validation
key-files:
  created: []
  modified:
    - web/build.gradle.kts
    - web/vite.config.ts
    - web/src/app/main.tsx
    - web/test/client-graph.py
    - bff/src/main/resources/static/openapi.json
    - bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt
    - web/test/generated-client.test.ts
    - bff/src/main/kotlin/courses/bff/BffApplication.kt
    - bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt
    - web/test/role-states.test.tsx
key-decisions:
  - Resolve the effective documentation URL with Vite mode and environment precedence.
  - Apply case-sensitive identifier uniqueness to the immutable directory snapshot.
requirements-completed: [FND-06, CQRS-04, UI-03]
actuals:
  tokens: 5892
  tasks: 3
  commits: 5
commits: 5
plan_head_before: 781355d1ed6b1f230be3f4e56787bf04446743c2
plan_head_after: cca11b1248b4f1c6b64aab557c98afa1173fc46b
duration: 18m29s
completed: 2026-11-26
status: complete
---

# Demo Shell Validation and Role Directory Summary

Vite now validates and normalizes the documentation base before startup. The BFF and generated client reject malformed role fields and enforce case-sensitive directory identity at their respective boundaries.

## Accomplishments

- The disposable Gradle test proved the default loopback URL, the process override of an invalid production env file, and the exact normalized deployment prefix shipped in the bundle. An invalid port stopped both the build and the Vite dev command with a fixed diagnostic. The failure output excluded the synthetic input sentinel and the failed builds produced no bundle files.
- The published and served OpenAPI match byte for byte. NetworkNT and the regenerated Orval client reject space-and-tab, non-breaking space and zero-width no-break space in every role identifier and label. The tests preserve input with content, student order and the empty student list.
- The BFF rejects duplicate student IDs and administrator/student collisions. It preserves case-distinct IDs and takes an unmodifiable copy of the student list in display order.
- Chromium exercises blank-label and duplicate-ID HTTP 200 replies. The alert, disabled selector, saved role and documentation links remain available during failure. A valid retry restores the saved selection and enables the selector.

## Regression Evidence

- The pre-fix Gradle run reported `:web:webBuild UP-TO-DATE` after an explicitly empty process override of an existing default bundle. This exposed the collision between absent and empty task inputs.
- The contract RED run reported an empty NetworkNT violation list where the test expected `pattern` at `/administrator/id`. The managed Node TAP run reported 12 missing expected Zod rejections. Both reports passed the GSD RED evidence check.
- The model RED run reported five expected assertion failures. Four construction checks observed missing exceptions for blank strings and duplicate identities. Clearing the caller's list also removed the directory's students. The JUnit report passed the GSD RED evidence check.

## Verification

- `./gradlew --console=plain :web:verifyClientGraph` passed twice, including the post-commit tracer gate.
- `./gradlew --console=plain :bff:componentTest :web:generateClient :web:webCheck` passed. The generated schemas applied regex checks to all four fields. All 6 HTTP component and 32 generated-client cases passed.
- `./gradlew --console=plain :bff:test :bff:componentTest :web:webCheck :web:shellSmoke styleCheck` passed with the managed tools. The run covered 9 unit, 6 HTTP, 32 client and 19 Chromium cases, plus typecheck, Steiger and the repository style check.
- `git diff --check` passed over the complete source commit range.

## Deviations from Plan

- **Rule 1** added a Gradle input change in `web/build.gradle.kts`. The absent value and the explicit empty value now produce distinct task input fingerprints. Commit `552c2cf`.
- **Rule 1** used an explicit character class equivalent to ECMAScript `\S` for the OpenAPI and Kotlin patterns. The independent HTTP validator uses Java's default regex engine, whose shorthand has a different whitespace set. Managed Node verified equivalence across all Unicode code points. Cross-runtime tests include U+00A0 and U+FEFF rejection and U+0085 acceptance. Commits `b826f5b` and `cca11b1`.

## Source Commits

| Commit    | Change                                          |
| --------- | ----------------------------------------------- |
| `552c2cf` | Validate the demo documentation base at startup |
| `32ff545` | Reproduce whitespace-only role fields           |
| `b826f5b` | Reject blank strings in the role contract       |
| `39e478b` | Cover directory construction and shell recovery |
| `cca11b1` | Enforce immutable unique demo role identities   |

## Self-Check: PASSED
