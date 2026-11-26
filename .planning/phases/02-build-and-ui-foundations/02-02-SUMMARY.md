---
phase: 02-build-and-ui-foundations
plan: "02"
subsystem: testing
tags: [gradle, kotlin, junit, kotest, test-fixtures, spring-boot, openapi, networknt]
requires:
  - phase: 02-01
    provides: Live BFF role directory, published OpenAPI resource, and generated browser client
provides:
  - Shared JVM convention with Eclipse Temurin toolchain and Jupiter defaults
  - Published Kotlin Java Test Fixtures variant and BFF classpath isolation checks
  - Docker-free MVC component suite that validates the live HTTP response against OpenAPI 3.1
affects: [02-05, 02-10, 03, 07]
tech-stack:
  added: [NetworkNT JSON Schema Validator 3.0.9]
  patterns: [included Gradle build, JVM Test Suites, Java Test Fixtures, loopback HTTP contract verification]
key-files:
  created:
    - build-logic/settings.gradle.kts
    - build-logic/build.gradle.kts
    - build-logic/src/main/kotlin/courses.jvm.gradle.kts
    - fixtures/build.gradle.kts
    - fixtures/src/testFixtures/kotlin/courses/fixtures/DirectoryFixtures.kt
    - bff/src/test/kotlin/courses/bff/DirectoryUnitTest.kt
    - bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt
  modified:
    - settings.gradle.kts
    - bff/build.gradle.kts
    - gradle/libs.versions.toml
key-decisions:
  - Use the root Gradle catalog and .java-version in the reusable JVM convention.
  - Restrict NetworkNT to the BFF component suite and allow schema references only within the packaged contract.
patterns-established:
  - Verify fixture consumption through resolved project capabilities and check the production runtime by selected component identities.
  - Validate the raw HTTP JSON using the method, path, status, and media type in the published OpenAPI document.
requirements-completed: [FND-05, CQRS-04, QA-07]
coverage:
  - id: D1
    description: Two Jupiter suites consume the published fixture variant and the production runtime remains isolated.
    requirement: FND-05
    verification:
      - kind: integration
        ref: "./gradlew --console=plain :bff:test :bff:componentTest :bff:verifyFixtureIsolation"
        status: pass
    human_judgment: false
  - id: D2
    description: The live BFF directory matches the published schema and serves the canonical contract byte for byte.
    requirement: CQRS-04
    verification:
      - kind: integration
        ref: "bff/src/componentTest/kotlin/courses/bff/DirectoryHttpTest.kt"
        status: pass
    human_judgment: false
  - id: D3
    description: The BFF check detects a bad fixture graph, a malformed HTTP response, and altered contract bytes.
    requirement: QA-07
    verification:
      - kind: integration
        ref: "Disposable candidate mutations of fixture selection, production runtime, HTTP response, and processed OpenAPI resource"
        status: pass
    human_judgment: false
actuals:
  tokens: 4903
  tasks: 3
  commits: 5
commits: 5
plan_head_before: 46f877f592ed8428395a68c266c2119d86c9c103
plan_head_after: f971d0a2852d77d2838d400eb833a8566a7e08b3
duration: 18m54s
completed: 2026-11-25
status: complete
---

# Phase 02 Plan 02: Run Kotlin Unit and HTTP Contract Suites With Shared Fixtures Summary

**Jupiter ran seeded Kotest properties and verified the live Spring MVC directory against the published OpenAPI contract, with fixtures and validation libraries confined to test classpaths.**

## Performance

- Started at 2026-11-25T12:40:31Z and completed the execution evidence at 2026-11-25T12:59:25Z.
- Completed 3 tasks covering 10 files.

## Accomplishments

- `courses.jvm` applies Kotlin/JVM and configures JVM Test Suites with catalog-managed Jupiter. The BFF and fixture projects use the Temurin feature version from `.java-version`.
- The default BFF test suite and `componentTest` both resolve the `:fixtures` test-fixtures capability. `verifyFixtureIsolation` checks their compile and runtime classpaths and rejects fixture, Kotest, and NetworkNT components on the BFF production runtime.
- The component suite runs Spring Boot MVC on a random loopback port. It verifies the documented status, media type, exact role IDs and ordering, required fields, and uniqueness. It compares the served and packaged OpenAPI bytes with the 1,696-byte source and checks that the document describes the one implemented operation.
- The independent validator reports the missing administrator with keyword `required` and property `administrator`. Its schema loader permits only the document IRI used for the packaged bytes. An external schema reference is rejected during the component test.

## Task Commits

| Task | Commit | Result |
| --- | --- | --- |
| 02-02-01 | `0be352a` | Shared JVM convention, Boot JAR, and seeded BFF test |
| 02-02-02 RED | `05735d2` | Required fixture samples for zero, one, and two students |
| 02-02-02 GREEN | `4c725c1` | Shared fixture publication, suite consumption, and runtime isolation |
| 02-02-03 RED | `621938a` | Required schema rejection for a parseable payload missing the administrator |
| 02-02-03 GREEN | `f971d0a` | Live HTTP verification and test-scoped NetworkNT pin |

## Verification

Gradle ran on Temurin 25.0.5.1+2-LTS with wrapper 9.9.2 and KGP 2.4.21. Both classpath graphs selected Jupiter engine 6.1.3. The Gradle and KGP pairing passed these checks. The publisher lists Gradle 9.7.0 as the upper bound of the fully supported range for this KGP version. [Kotlin Gradle plugin compatibility](https://kotlinlang.org/docs/gradle-configure-project.html)

| Command | Observation |
| --- | --- |
| `./gradlew --console=plain :bff:bootJar :bff:test --tests 'courses.bff.DirectoryUnitTest'` | Exit 0. The Boot JAR assembled, and the filter ran one Jupiter test at seed `20261125` for 32 checks. The tracer feedback rerun took 10 seconds. |
| `./gradlew --console=plain :bff:test :bff:verifyFixtureIsolation` | Exit 0 in 17 seconds. Both unit tests passed. Seed `20261126` checked 32 samples and reported sizes `[0, 1, 2]`. |
| `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :bff:test :bff:componentTest :bff:verifyFixtureIsolation` | Exit 0 in 24 seconds after the catalog pin. |
| `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :bff:clean :bff:build --no-build-cache` | Exit 0 in 14 seconds. The clean BFF build executed 2 unit and 4 component tests with 0 failures, errors, or skips. The lifecycle also ran `verifyFixtureIsolation`. |
| `./gradlew --console=plain :bff:dependencies --configuration runtimeClasspath` | Exit 0. The graph excluded `:fixtures`, `io.kotest`, and `com.networknt`. |
| `./gradlew --console=plain :web:generateClient --dry-run` | The client generation task graph had no BFF tasks. |
| `env DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain :web:provisionBrowser :web:roleTracer` | Exit 0 in 35 seconds. Chromium 159.0.8154.6 passed the original tracer and selected Alex Rivera from the live BFF reply. |

### Negative controls and TDD evidence

- Task 1 failed in the same filtered Jupiter class when the label expectation was reversed. The XML showed the property assertion and seed `20261125`. An unmatched class filter failed with `No tests found`.
- Task 2 produced `RED_EVIDENCE_OK` using fresh JUnit XML. The named property shrank to a zero-student sample and failed with expected 0 versus actual 2. Removing the fixture dependency produced unresolved fixture imports, selecting the plain project variant failed `testCompileClasspath`, and injecting the fixture and Kotest into production fired the runtime leak check.
- Task 3 produced `RED_EVIDENCE_OK` on the missing-administrator assertion. The parse-only check returned no violations for the valid JSON object. The four GREEN cases include exact NetworkNT diagnostic matching and same-document reference enforcement.
- A disposable BFF controller return value missing `administrator` failed the live HTTP assertion with `required property 'administrator' not found`. Appending one newline to the processed OpenAPI resource failed the served comparison with expected length 1696 and actual length 1697. Injecting NetworkNT into the production runtime failed the classpath check and named the selected artifact.
- The unit and component reports and both classified RED records were retained under the ignored GSD evidence directory.

## Dependency Qualification

Maven Central publication metadata and the upstream release identify `com.networknt:json-schema-validator:3.0.9` as the current stable release. The publisher targets Java 17+ and Jackson 3. The isolated exact-coordinate run passed the four component cases with Boot 4.2.0, Temurin 25, and selected Jackson Databind 3.1.8 before the catalog pin. The catalog-backed configuration then passed the clean BFF build. [NetworkNT release](https://github.com/networknt/json-schema-validator/releases/tag/3.0.9), [Publisher POM](https://repo.maven.apache.org/maven2/com/networknt/json-schema-validator/3.0.9/json-schema-validator-3.0.9.pom)

## Issues Encountered

- Jackson 3's `JsonNode.map` supplies the whole node to its callback. The component test uses `values()` to assert the ordered contents of the student array. The corrected RED run had exactly one failing test.
- The pre-existing duplicate KGP loader warning now lists `:bff`, `:fixtures`, and `:probe`. The 02-10 executor owns the root build-script change. A disposable root `build.gradle.kts` with the following plugin declarations removed the warning and passed `:bff:verifyFixtureIsolation :bff:test :bff:componentTest :probe:test` in 57 seconds. The trial kept the probe script and catalog versions intact.

  ```kotlin
  plugins {
      alias(libs.plugins.kotlin.jvm) apply false
      alias(libs.plugins.kotlin.spring) apply false
      id("courses.jvm") apply false
  }
  ```

## Deviations from Plan

None. The KGP root-scope trial was confined to a disposable candidate.

## Next Phase Readiness

The shared convention and fixture publication are available to later JVM suites. The independent HTTP check covers the server side of the contract while the original browser tracer continues to consume the same Gradle artifact. Plans 02-03, 02-05, 02-07, 02-09, and 02-10 carry remaining checks for shared CQRS-04 and QA-07 evidence.

## Self-Check: PASSED
