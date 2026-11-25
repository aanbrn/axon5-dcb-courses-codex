# Phase 01 feasibility record

On 2026-11-25 the native ARM64 probe passed a multi-tag write, an overlapping append refusal and a remote subscription update in a fresh Axon Server DCB context. The ordinary build passed with Docker unreachable. The four independent toolchain checks passed in the same acceptance run.

| Evidence field | Observed value |
| --- | --- |
| Acceptance run | `acceptance-5zjznvdt` |
| Tested revision | `3b5f0ef405e699b7ff6b212366880f846b650d00` |
| Input tree SHA-256 | `0880d41be1a2441daf2e5ee8ff195207a66817629095d0fb0936094b6f21bd78` |
| Manifest SHA-256 | `d99a8403e073c21d6b7edd876923ceb339912e6855ec23594aabd169a56f2b0b` |
| Gradle | `9.9.2` |
| Kotlin | `2.4.21` |
| Spring Boot | `4.2.0` |
| Axon Framework | `5.4.2` |
| Axoniq Framework | `5.4.2` |
| JUnit | `6.1.3` |
| Temurin | `25.0.5.1+2-LTS` |
| JVM architecture | `aarch64` |
| Docker platform | `linux/arm64` |
| Docker server | `29.10.0` |
| Axon Server index | `axoniq/axonserver:2026.1.8@sha256:57b6ad30353cc0df1612d6a30be03a1df85b4b49b5f2feee218a70d1cb7794c2` |
| ARM64 manifest | `sha256:463d3a60cecbe0301860924ea3eaef5b0d6e3b8a4fd26e8b9cc82e9df7ab7bf4` |
| ARM64 config | `sha256:ff706e6d5bdf856240d1167404ab509558ed1a433ff4e0c55f7c02ae1b837130` |
| AMD64 manifest | `sha256:6c7646628da238d3e2ac5ff58e271e0ebbeab924f8027858eda711804d200a42` |
| AMD64 config | `sha256:d340e53869f149bfd5db58187786d435b5e29e530a4c047241d5525b8822cca6` |
| Axon Server Java transport | `2026.1.1` |
| Reactor Core | `3.9.0` |
| Testcontainers | `2.0.5` |
| Runtime Guava | `33.8.0-android` |
| Formatter Guava | `33.8.0-jre` |
| frontend | `Pass` |
| typeid | `Pass` |
| kotest | `Pass` |
| kdoc | `Pass` |

## Reproduce the proof

Start from a clean checkout of the tested revision. The revision includes the full harness and remains the entry point after the module is retired. Use a native ARM64 host, Eclipse Temurin 25 for the Gradle launcher and toolchain, Python 3.9 or newer, and a reachable Linux/ARM64 Docker daemon for the opt-in checks. Put the Pack version declared in `mise.toml` on `PATH` for the optional image check. Gradle provisions the selected Node and npm.

```sh
./gradlew --console=plain --version
DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain build --dry-run
DOCKER_HOST=tcp://127.0.0.1:1 ./gradlew --console=plain build --no-build-cache --rerun-tasks --info
./gradlew --console=plain :probe:integrationTest :probe:frontendImageProbe --dry-run
./gradlew --console=plain :probe:integrationTest --rerun-tasks
python3 probe/verify_evidence.py --capture --evidence probe/build/reports/feasibility
```

The capture creates a unique ignored run directory, sets aside existing probe build products, and runs the ordinary build twice with Docker unreachable. The first build starts without project output. The second reuses the warmed tool and dependency caches. The capture then runs all three integration cases and collects the resolver output and seven secondary stages. It retains the original JUnit XML, command exits, tool identities, raw OCI metadata and SHA-256 fingerprints. Public downloads may populate the Gradle, npm, or Docker caches. The server data, role homes and configuration start empty for the native proof.

To verify this publication against the retained local run, keep its `runs/acceptance-5zjznvdt` directory and use the following command. A repeat capture has a new run ID and its own evidence.

```sh
python3 probe/verify_evidence.py --evidence probe/build/reports/feasibility --report docs/feasibility/phase-01.md
```

## Selected versions

The stable and applicable LTS starting candidates were checked against publisher release metadata on 2026-11-24 and 2026-11-25. The native result selected the candidate tuple without a downgrade.

| Starting candidate | Selection rationale and publication evidence |
| --- | --- |
| Axon Framework and Axoniq Framework 5.4.2 | The OSS framework supplies the DCB APIs. The Axoniq distribution supplies Axon Server persistence and distributed messaging for this flow. The 5.4.2 Maven coordinates were published on 2026-11-16. [OSS release](https://github.com/AxonIQ/AxonFramework/releases/tag/axon-5.4.2), [Axoniq parent POM](https://repo.maven.apache.org/maven2/io/axoniq/framework/axoniq-framework/5.4.2/axoniq-framework-5.4.2.pom), [Framework comparison](https://docs.axoniq.io/axon-framework-reference/5.4/framework-comparison/) |
| Axon Server 2026.1.8 | The publisher's 2026.1 patch available on 2026-11-23 includes DCB fixes. The fixture resolved the exact immutable index and ran its ARM64 child. [2026.1 patch notes](https://docs.axoniq.io/axon-server-reference/v2026.1/rn-as-minor-releases/#release-202618), [Docker Hub image](https://hub.docker.com/r/axoniq/axonserver) |
| Spring Boot 4.2.0 | GA on 2026-11-19. The build resolved the published 4.2 BOM and the real Spring applications exercised the selected Axon wiring. [Spring Boot release](https://github.com/spring-projects/spring-boot/releases/tag/v4.2.0), [Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html), [Axon Spring Boot integration](https://docs.axoniq.io/axon-framework-reference/5.4/spring-boot-integration/) |
| Kotlin 2.4.21 and Gradle 9.9.2 | The stable Kotlin release and current Gradle release passed together. JetBrains gives 9.7.0 as the upper end of its fully supported Gradle range for KGP 2.4.20–2.4.21. Keep the measured 9.9.2 combination and repeat compatibility checks on KGP or Gradle updates. [Kotlin releases](https://kotlinlang.org/docs/releases.html), [KGP compatibility table](https://kotlinlang.org/docs/gradle-configure-project.html), [Gradle release service](https://services.gradle.org/versions/current), [Gradle checksums](https://gradle.org/release-checksums/) |
| Eclipse Temurin 25 | The applicable LTS feature and 25.0.5.1+2 patch were selected. The launcher, daemon, Kotlin compiler toolchain, smoke worker and all three probe JVMs reported Eclipse Adoptium build 25.0.5.1+2-LTS on ARM64. [Adoptium patch release](https://github.com/adoptium/temurin25-binaries/releases/tag/jdk-25.0.5.1%2B2) |
| JUnit 6.1.3 and Testcontainers 2.0.5 | The selected Jupiter engine and Platform launcher are 6.1.3. Boot manages Testcontainers 2.0.5 in the integration graph. The running auxiliary image was `testcontainers/ryuk:0.14.0`. [JUnit release](https://github.com/junit-team/junit-framework/releases/tag/r6.1.3), [Testcontainers release](https://github.com/testcontainers/testcontainers-java/releases/tag/2.0.5) |
| Node 26.13.1 LTS and npm 12.2.3 | The Lithium LTS release and the separately pinned npm passed the Gradle Node 7.1.0 static asset and TypeID checks. [Node release](https://nodejs.org/en/blog/release/v26.13.1), [npm release](https://github.com/npm/cli/releases/tag/v12.2.3), [Gradle Node release](https://github.com/node-gradle/gradle-node-plugin/releases/tag/7.1.0) |

The tested `probe/build.gradle.kts` declares `org.springframework.boot:spring-boot-dependencies:4.2.0`, `org.axonframework:axon-framework-bom:5.4.2`, then `io.axoniq.framework:axoniq-framework-bom:5.4.2` as Gradle platforms. The resolved Axon distribution combines the OSS Spring starter and autoconfigure modules, messaging, modelling, and event sourcing with the Axoniq Spring starter, autoconfigure, distributed messaging, and `io.axoniq.framework:axon-server-connector:5.4.2`. The connector brings `io.axoniq:axonserver-connector-java:2026.1.1`. The role runtime resolved Kotlin stdlib and reflection 2.4.21 and Boot-managed Reactor Core 3.9.0, gRPC 1.84.1 and Protobuf 4.36.2. The starter's Testcontainers convenience module is excluded at that dependency. The integration suite supplies Testcontainers in its own configuration. [Boot BOM](https://repo.maven.apache.org/maven2/org/springframework/boot/spring-boot-dependencies/4.2.0/spring-boot-dependencies-4.2.0.pom)

Version ownership stays with the checked-in [Gradle wrapper](../../gradle/wrapper/gradle-wrapper.properties), [Gradle catalog](../../gradle/libs.versions.toml), [JDK feature file](../../.java-version), [Node version file](../../.nvmrc), [CLI pins](../../mise.toml), and the sample npm manifests and lockfiles. The full JDK patch is a measured value. Hosted Actions SHA pins belong to the later hosted delivery work.

## Applicable terms

**Server image.** The publisher's Docker Hub entry links its Legacy Software Subscription Agreement Terms. Its license summary and the agreement's single-node clause describe designated non-production deployment for up to 14 days, with a commercial license required for production or longer deployment. Axoniq's current Terms of Service, dated 2026-04-22, separately describe the designated Unregistered License as evaluation only for 14 days starting on first download, with registration and an appropriate plan for continued use. The exact OCI configuration included no separate license label. The vendor documents that Axon Server 2026.0 and later shuts down after 12 hours when it has neither a Platform configuration nor a license file. The probe observed the unregistered startup and its scheduled shutdown message. [Docker Hub license summary](https://hub.docker.com/r/axoniq/axonserver), [Legacy subscription terms](https://www.axoniq.io/legal/legacy-software-subscription-agreement-terms), [Current terms, sections 1.4 and 3](https://www.axoniq.io/legal/terms-of-service), [Runtime expiry documentation](https://docs.axoniq.io/axoniq-platform-reference/licensing/rotation-and-expiry/)

**Application artifacts.** The OSS Axon parent POM declares Apache 2.0. The Axoniq Framework parent POM applies the current Axoniq Terms of Service to its 5.4.2 starter, autoconfigure, distributed messaging and server connector. The Java transport POM declares the same terms. The licensing reference lists product-key checks for commercial add-ons such as PostgreSQL event storage, workflow and data protection. Those add-ons were outside the selected graph. In the missing-license path for an application using licensed modules, the reference says that the application can run for 24 hours while it obtains a license. For Axoniq Framework 5.3.2 and later with no license source or Platform configuration it documents a machine-bound temporary development permission requested from Platform and renewed hourly. The three fixture roles registered with the server using empty homes and without vendor registration, a supplied license file, or a Platform token. Their logs had no development-permission message during this run. Public Docker Registry requests used the anonymous pull path. Vendor-offline execution, renewal and multi-hour behavior remain unverified. [OSS POM](https://repo.maven.apache.org/maven2/org/axonframework/axon/5.4.2/axon-5.4.2.pom), [Axoniq parent POM](https://repo.maven.apache.org/maven2/io/axoniq/framework/axoniq-framework/5.4.2/axoniq-framework-5.4.2.pom), [Java transport POM](https://repo.maven.apache.org/maven2/io/axoniq/axonserver-connector-java/2026.1.1/axonserver-connector-java-2026.1.1.pom), [License coverage](https://docs.axoniq.io/axoniq-platform-reference/licensing/), [License sources](https://docs.axoniq.io/axoniq-platform-reference/licensing/license-sources/)

**Optional Platform access.** The Individual plan provides Development access subject to the publisher's plan terms. Account-based Platform connection and any production entitlement have their own scope. The short local acceptance run used the registration-free evaluation path. [Axoniq billing](https://docs.axoniq.io/axoniq-platform-reference/billing/)

## Native ARM64 proof

The capture ran from 2026-11-24 23:58:49 UTC through 2026-11-25 00:03:52 UTC. The host reported macOS 27.2.1 on ARM64, with a Linux/ARM64 Docker 29.10.0 daemon. The fixture explicitly pulled the ARM64 child by manifest digest. Docker reported the running image ID as the ARM64 config digest. The container config declared Java `jdk-21.0.13+9`, and the server startup reported Java 21.0.13. The capture hashed the OCI index bytes and both child manifests and configs. The AMD64 rows record registry metadata.

Each integration case started a disposable container with `AXONIQ_AXONSERVER_STANDALONE_DCB=true`, mapped the management and gRPC ports to loopback, and waited for `/v1/public/me` and the DCB context's elected primary. The clients used `axon.axonserver.servers` for the mapped gRPC address and selected `axon.axonserver.context=default`. The three JVMs used `AxonServerEventStorageEngine` and distributed command and query buses. [Axon Server local installation](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/installation/local-installation/), [Versioned context documentation](https://docs.axoniq.io/axon-server-reference/v2026.1/axon-server/administration/multi-context/)

| Role | Observed PID | Client ID |
| --- | --- | --- |
| Test worker / driver | 95453 | `probe-driver-acceptance-5zjznvdt` |
| Command | 96085 | `probe-command-acceptance-5zjznvdt` |
| Projection | 96367 | `probe-projection-acceptance-5zjznvdt` |

```text
context default, empty history, terminal marker 0
course 43cc43ca-b8fc-449b-ac65-b403c4d45460
direct query before write = 0; open subscription initial result = 0
command JVM commit = 89e5a621-9f04-4bb3-8ea2-82a1b862d720
stale append 2aa94012-3466-4c67-beb1-1f584d6e432c
  AppendEventsTransactionRejectedException / CANCELLED / ConsistencyConditionException
courseId read = [89e5a621-9f04-4bb3-8ea2-82a1b862d720]
studentId read for a475d1ac-94c4-4e56-a99e-26a14ccfbcf6 = [89e5a621-9f04-4bb3-8ea2-82a1b862d720]
joint tag read and complete history = [89e5a621-9f04-4bb3-8ea2-82a1b862d720]
studentId read for 2ef20dc3-1e1c-4192-bcc0-45920ba7c59a = []
open subscription update = 1, event 89e5a621-9f04-4bb3-8ea2-82a1b862d720
fresh query = 1, event 89e5a621-9f04-4bb3-8ea2-82a1b862d720
```

JUnit executed the remote tagged write tracer, overlapping append and subscription case, and controlled cleanup failure case with zero skips, errors or failures. Both cleanup paths closed the opened subscription, exited the two child processes, and removed the owned container. The forced failure left an unrelated Docker network intact.

The cold and warm ordinary wrapper invocations took 8.19 and 4.25 seconds. Each executed one Jupiter contract smoke case. The exact dry-run tasks included `:probe:test` and left the Docker integration and image tasks explicit. The full integration wrapper invocation took 95.47 seconds with cached tool and image inputs and freshly initialized scenario containers. The harness budgets 90 seconds for server readiness, 45 seconds per child, 20 seconds per message operation, and five minutes for the integration task. A first-time download adds network-dependent time.

## Secondary checks

All seven diagnostic stages returned zero. Each result was collected independently of the DCB behavior and bound to this native acceptance run. Run the commands from the repository root.

| Check | Reproducer | Observed result and receiving work |
| --- | --- | --- |
| Kotlin / Jupiter / Kotest | `./gradlew --console=plain :probe:kotestProbe --rerun-tasks` | Kotlin 2.4.21 and Jupiter 6.1.3 executed the named Kotest 6.2.7 property case in the Temurin worker. Seed `20261124` ran 32 checks. Use the combination for shared test conventions in Phase 2. [Kotest 6.2.7](https://github.com/kotest/kotest/releases/tag/v6.2.7) |
| ktfmt / KDoc | `./gradlew --console=plain :probe:kdocProbe --rerun-tasks` | `org.jetbrains.kotlinx:ktfmt:0.65` wrapped the long paragraph in the `kotlinlang` style and preserved the link, list, fenced example, and tags. Both formatted outputs shared SHA-256 `539206da981249e09a0f9d4aa9bea0dadcd3571d57e38c7127a6908bb4df8106`. Phase 2 owns shared formatting, detekt comments and Dokka enforcement. [ktfmt 0.65](https://github.com/Kotlin/ktfmt/releases/tag/v0.65) |
| TypeID interoperability | `./gradlew --console=plain :probe:typeIdJvmVectors --rerun-tasks`, then `./gradlew --console=plain :probe:typeIdProbe --rerun-tasks` | JVM `de.fxlae:typeid-java:0.3.1` and `typeid-js@1.2.0` with the native TypeScript 7.0.2 compiler each checked 9 valid and 21 invalid vectors. The two exchanges checked two independently produced IDs per direction, including their prefixes and 16 UUID bytes. Phase 3 owns application storage round trips and TypeScript dependency selection. [TypeID vectors](https://github.com/jetify-com/typeid/tree/cb20c6eeb4bc6e5a115fceffcbb22f331d4033f8/spec), [JVM library release](https://github.com/fxlae/typeid-java/tree/v0.3.1), [TypeScript release](https://github.com/microsoft/typescript-go/releases/tag/typescript%2Fv7.0.2) |
| Gradle/npm and Paketo | `./gradlew --console=plain :probe:frontendAssets --rerun-tasks`, then `./gradlew --console=plain :probe:frontendImageProbe --rerun-tasks` | Gradle drove `npm ci`, preserved the lock, and staged static assets. Pack 0.40.11 and lifecycle 0.21.29 used the catalog-pinned Jammy buildpackless builder 0.0.363, Jammy run image, and Web Servers 4.16.3 on ARM64. Two marker builds served HTTP 200 with bodies matching their own staged bytes. Phase 2 owns the project asset build, and Phase 5 owns application image packaging. [Pack release](https://github.com/buildpacks/pack/releases/tag/v0.40.11), [Paketo Web Servers 4.16.3](https://github.com/paketo-buildpacks/web-servers/releases/tag/v4.16.3) |

The separate TypeID npm advisory check on 2026-11-25 ran `npm audit --ignore-scripts --json` against the official advisory API. It exited `1` with two Moderate entries for one underlying advisory, GHSA-w5hq-g745-h8pq / CVE-2026-41907, and zero High or Critical entries. The Jetify dependency's `^10.0.0` range selects `uuid@10.0.0` and does not admit the upstream fixes. The installed Jetify bundle imports only `uuid.stringify` and `uuid.v7`, and the fixture uses fixed UUID bytes and parsed TypeID suffixes. The advisory concerns `v3`, `v5`, and `v6` with supplied output buffers. The build maintainer owns the temporary `probe/typeid` hold through 2026-12-02. Reassess immediately if its input or API surface changes. When a verified Jetify release selects a patched `uuid`, refresh the lock and repeat the exact audit and TypeID check. Application dependency selection stays open. [Upstream uuid advisory](https://github.com/uuidjs/uuid/security/advisories/GHSA-w5hq-g745-h8pq), [Plan 01-04 advisory assessment](../../.planning/phases/01-axon-server-and-toolchain-feasibility/01-04-SUMMARY.md#npm-advisory-assessment)

## Dependency and image review

The capture retained `:probe:dependencies` for runtime, test, integration, compile, formatter, Kotest and TypeID configurations and `:probe:dependencyInsight` for the selected paths. To reproduce individual queries, substitute the appropriate compile or runtime configuration.

```sh
./gradlew --console=plain :probe:dependencies --configuration integrationTestRuntimeClasspath
./gradlew --console=plain :probe:dependencyInsight --configuration runtimeClasspath --dependency com.google.guava:guava
./gradlew --console=plain :probe:dependencyInsight --configuration kdocFormatter --dependency com.google.guava:guava
./gradlew --console=plain :probe:dependencyInsight --configuration testRuntimeClasspath --dependency org.postgresql:postgresql
```

| Prior record | Disposition in this checkout |
| --- | --- |
| Guava GHSA-xxph-c9ww-hj94 / CVE-2026-102554 | **Reproduced and corrected.** The selected Axon Java transport and Boot-managed gRPC graph previously chose 33.6.0-android. The isolated ktfmt and google-java-format graph previously chose 33.5.0-jre. The advisory covers both variants and the patched release starts at 33.7.2. The existing BOMs did not select a fixed version. Two ordinary catalog-backed lower bounds now select 33.8.0-android in the consuming role/test graphs and 33.8.0-jre in the formatter alone. Before/after comparisons checked the affected compile and runtime graphs and the independent controls. The role-side selection also raised Error Prone annotations to 2.52.0. The formatter-only selection also raised JSpecify to 1.0.1 and Error Prone annotations to 2.52.0. The applicable builds, integration tests and formatter checks passed. The build maintainer reviews by 2026-12-01 or sooner on a relevant upstream/BOM change. Remove a bound after upstream selects a fixed release in the affected graphs and the graph comparisons, applicable tests and available private checks pass without it. [Reviewed advisory](https://github.com/advisories/GHSA-xxph-c9ww-hj94), [Guava 33.8.0 publisher release](https://github.com/google/guava/releases/tag/v33.8.0) |
| pgJDBC 42.7.15 | **Outside the examined graphs.** Upstream published the 42.7.15 security release on 2026-11-23. The selected Boot 4.2.0 BOM declares 42.7.14. Dependency insight found no selected pgJDBC in the probe compile or runtime configurations. Recheck the first consuming application role, its workers and tests, and after Boot updates. Prefer a fixed BOM selection and use a scoped explicit version if needed. [pgJDBC 42.7.15](https://github.com/pgjdbc/pgjdbc/releases/tag/REL42.7.15) |
| Axon Server image | **Reproduced for the selected index and native child.** Both runnable child manifests and configs were checked. ARM64 ran the DCB proof. The vendor lists its own Guava 33.8.0 update for CVE-2026-102554 and CVE-2026-118042 in this patch. The build maintainer reviews by 2026-12-01 or sooner on a relevant security or terms change. Re-evaluate the exact replacement index, children, terms and runtime before changing the pin. [Axon Server 2026.1.8 release notes](https://docs.axoniq.io/axon-server-reference/v2026.1/rn-as-minor-releases/#release-202618) |
| PostgreSQL image | **Outside the examined scope.** This checkout has no selected PostgreSQL image or running PostgreSQL case. The first consuming phase must verify the exact candidate index and children, terms, and a fresh runtime test. The earlier review date is 2026-12-01, with earlier review on a relevant security or terms change. |
| B8 private JVM advisory check / B17 historical review | **Private check incomplete.** The referenced procedure and earlier output were unavailable here. The current public graph comparison reproduces the applicable Guava selection evidence. Application `:command`, `:query`, and `:bff` runtime graphs are pending those modules. When the procedure and authorized feed are available, run it for those role graphs and the probe's two selected test runtimes. Recheck at least weekly and after dependency or relevant advisory changes. Results apply only to the examined Maven selections, transitives and BOM metadata. Gradle plugins, the JDK, npm, images and OS packages are outside the private JVM scope. The maintainer has been notified of the incomplete check. Hosted dependency update automation and hosted dependency and image scans are pending. [Project dependency maintenance policy](../../.planning/PROJECT.md#dependency-maintenance) |

## Hosted AMD64 verification and retirement

The first actual AMD64 run belongs on a hosted GitHub Actions AMD64 runner when hosted CI is enabled. Use the application integration and E2E suites if they already demonstrate the required behavior. Otherwise run an AMD64-capable `:probe` there. Phase 01 records AMD64 image metadata and a successful native ARM64 run.

Retire `:probe` only after a successful hosted AMD64 run has Testcontainers coverage of a committed multi-tag write, rejection of an overlapping append, and a cross-process subscription update correlated with the persisted event. Require a passing representative browser workflow in Playwright. Keep this report and add the link to the successful replacement run before removing the module.
