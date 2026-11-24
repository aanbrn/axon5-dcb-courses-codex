# Stack Research

**Project:** Axon 5 DCB Courses

**Date:** 2026-11-24

**Confidence:** High for the documented entry points and medium for the combined runtime until Phase 1 executes the probe.

## Backend and Event Store

Use Kotlin and the Spring Boot 4 line from the brief. Axoniq documents Spring Boot integration in Framework 5, with distinct open-source and commercial distributions. For a candidate release, inspect the actual starter, BOM, connector coordinates, and license terms together. Verify the application wires the intended event store, command and query buses, and processor configuration. [Spring Boot integration](https://docs.axoniq.io/axon-framework-reference/5.4/spring-boot-integration/) · [Framework comparison](https://docs.axoniq.io/axon-framework-reference/5.4/framework-comparison/)

Axon Server supports DCB contexts. Its versioned documentation describes context creation and clustering configuration, and the available options vary by release. Match bootstrap configuration to the selected server image documentation. Check DCB context creation and startup without a Platform account or token on a clean volume, review image and connector terms for the target use, and record the immutable index and selected ARM64 and AMD64 child digests. [Axon Server contexts](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/administration/multi-context/) · [Axon Server cluster initialization](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/clustering/cluster-basics/) · [Axoniq licensing](https://docs.axoniq.io/axoniq-platform-reference/licensing/)

Keep the optional AxonIQ Platform connector behind explicit configuration. Use the vendor’s connector scope and externally injected credentials when performing account verification. [Axon Framework Client](https://docs.axoniq.io/axoniq-platform-reference/connectors/axon-framework/)

## Build, Tests, and Frontend

| Area | Direction | Evidence to collect in Phase 1 |
| --- | --- | --- |
| Gradle and tools | Wrapper, catalog, Temurin feature version, mise, Node version file, package metadata and lockfile, and SHA-pinned Actions each own their inputs. | Clean build and tool inventory. Record observed JDK patch/build separately. |
| JVM tests | JUnit 6 runner with Kotest assertions and property checks. Organize Gradle JVM Test Suites and share Kotlin helpers through Java Test Fixtures. Run Testcontainers against the selected Axon Server and PostgreSQL images. | A Kotlin test and property test in the chosen runner, shared fixtures used in a separate suite, and live server and database smoke tests. |
| TypeID | Use type-prefixed UUIDv7 IDs in contracts and native UUID storage. | Compare Kotlin and TypeScript encoding and decoding with common vectors, and prove a PostgreSQL UUID round trip. |
| Web build | Use the Gradle Node plugin for React/TypeScript and the docs site. Make OpenAPI generation, client generation, and frontend build explicit task inputs and outputs. | Regenerate the client from a clean build without relying on an already generated client. |
| JVM images | Use Spring Boot `bootBuildImage` with a Paketo builder. | Build and start a JVM image and inspect the selected builder and run image. |
| Frontend image | Use Paketo Web Servers. Its docs describe serving already built assets and building from frontend sources. | Test the selected pnpm workflow. If the source build path is unavailable, verify that Gradle can build the assets and Paketo can package them within the chosen build graph. |
| Documentation checks | Use ktfmt for Kotlin/KDoc, detekt `comments` rules, and Dokka warnings as errors. | Format representative KDoc and show which tool reports malformed documentation. |

Sources for these entry points. [Gradle version catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html) · [Gradle JVM Test Suites](https://docs.gradle.org/current/dsl/org.gradle.api.plugins.jvm.JvmTestSuite.html) · [Gradle Java Test Fixtures](https://docs.gradle.org/current/userguide/java_test_fixtures_plugin.html) · [TypeID specification repository](https://github.com/jetify-com/typeid) · [Gradle Node plugin](https://github.com/node-gradle/gradle-node-plugin) · [Spring Boot OCI packaging](https://docs.spring.io/spring-boot/gradle-plugin/packaging-oci-image.html) · [Paketo Web Servers](https://paketo.io/docs/howto/web-servers/)

## Tooling for Delivery

Use Steiger for frontend architecture rules and Storybook with axe for component checks. Pair Playwright workflow checks with a manual review of keyboard access, focus, and meaningful live updates against the WCAG 2.2 AA target. Use an OpenTelemetry Collector in the local Compose setup and keep the hosted Platform integration optional. [Steiger](https://github.com/feature-sliced/steiger) · [Storybook accessibility testing](https://storybook.js.org/docs/9/writing-tests/accessibility-testing) · [WCAG 2.2](https://www.w3.org/TR/WCAG22/) · [OpenTelemetry Collector with Docker](https://opentelemetry.io/docs/collector/install/docker/)

The Phase 1 version matrix is pending. Select one verified compatible tuple across Framework, Spring Boot, Axon Server, Kotlin, the toolchain, test dependencies, and buildpacks. Reconcile the dependency review records in [PROJECT.md](../PROJECT.md) with the actual selected graphs. Gradle documents why catalog declarations alone cannot establish the selected version and how to inspect selection. [Gradle dependency reports](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html)
