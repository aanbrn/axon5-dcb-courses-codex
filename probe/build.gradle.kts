import groovy.json.JsonOutput
import java.security.MessageDigest
import java.time.Duration
import java.util.HexFormat
import java.util.UUID
import javax.xml.parsers.DocumentBuilderFactory

plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.spring)
    id("jvm-test-suite")
}

val javaFeature = providers.fileContents(rootProject.layout.projectDirectory.file(".java-version"))
    .asText.map { it.trim().toInt() }

java {
    toolchain {
        languageVersion = javaFeature.map(JavaLanguageVersion::of)
        vendor = JvmVendorSpec.ADOPTIUM
    }
}

dependencies {
    implementation(platform(libs.spring.boot.bom))
    implementation(platform(libs.axon.bom))
    implementation(platform(libs.axoniq.bom))
    implementation(libs.spring.boot.starter)
    implementation(libs.axoniq.starter) {
        // The probe supplies its Docker server from the isolated integration suite.
        exclude(group = "io.axoniq.framework", module = "axoniq-testcontainer")
    }
    implementation(kotlin("reflect"))
    // The Axon connector uses Reactor at runtime for subscription queries.
    runtimeOnly(libs.reactor.core)
}

val roleClasspath = sourceSets.main.map { it.runtimeClasspath }
val roleLauncher = javaToolchains.launcherFor(java.toolchain)
val buildDirectory = layout.buildDirectory
val evidenceDirectory = providers.environmentVariable("PROBE_EVIDENCE_DIR")
    .map { rootProject.file(it) }
    .orElse(buildDirectory.dir("reports/feasibility").map { it.asFile })
val typeIdFixture = layout.projectDirectory.file("typeid/vectors.json")
val typeIdRunId = providers.environmentVariable("PROBE_RUN_ID").orElse("local")
val typeIdExchangeId = UUID.randomUUID().toString()
val kotlinExchange = buildDirectory.file("typeid/kotlin-origin.json")

fun sha256(bytes: ByteArray): String = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes))

fun observation(stage: String, fields: Map<String, Any>) {
    println("PROBE_SECONDARY ${JsonOutput.toJson(mapOf("stage" to stage) + fields)}")
}

fun publishArtifact(name: String, bytes: ByteArray): String {
    val directory = evidenceDirectory.get()
    directory.mkdirs()
    directory.resolve(name).writeBytes(bytes)
    return name
}

fun Configuration.moduleVersions() = incoming.resolutionResult.allComponents
    .mapNotNull { it.moduleVersion }
    .associate { "${it.group}:${it.name}" to it.version }

fun verifySecondaryIsolation() {
    for (name in listOf("runtimeClasspath", "integrationTestRuntimeClasspath")) {
        val helpers = configurations.getByName(name).moduleVersions().keys.filter { coordinate ->
            coordinate.startsWith("io.kotest:") || coordinate.startsWith("de.fxlae:") ||
                coordinate == "org.jetbrains.kotlinx:ktfmt"
        }
        check(helpers.isEmpty()) { "Secondary helpers leaked into $name: $helpers" }
    }
}

tasks.withType<Test>().configureEach {
    javaLauncher = roleLauncher
    systemProperty("probe.javaFeature", javaFeature.get())
}

testing.suites {
    named<JvmTestSuite>("test") {
        useJUnitJupiter(libs.versions.junit.get())
        dependencies {
            implementation(libs.jackson.databind)
        }
        targets.configureEach {
            testTask.configure {
                val workerHome = buildDirectory.dir("tmp/test/worker-home")
                val workerDirectory = buildDirectory.dir("tmp/test/worker-work")
                setEnvironment(mapOf("HOME" to workerHome.get().asFile.absolutePath))
                workingDir(workerDirectory)
                systemProperty("user.home", workerHome.get().asFile.absolutePath)
                doFirst {
                    for (directory in listOf(workerHome.get().asFile, workerDirectory.get().asFile)) {
                        check(directory.deleteRecursively() && directory.mkdirs()) { "Cannot initialize $directory" }
                    }
                }
            }
        }
    }

    register<JvmTestSuite>("integrationTest") {
        useJUnitJupiter(libs.versions.junit.get())

        dependencies {
            implementation(project())
            implementation(libs.jackson.databind)
            implementation(libs.testcontainers)
        }

        targets.configureEach {
            testTask.configure {
                dependsOn(roleClasspath)
                filter.isFailOnNoMatchingTests = true
                timeout = Duration.ofMinutes(5)
                testLogging.showStandardStreams = true

                val workerHome = buildDirectory.dir("tmp/integrationTest/worker-home")
                val workerDirectory = buildDirectory.dir("tmp/integrationTest/worker-work")
                workingDir(workerDirectory)
                systemProperty("user.home", workerHome.get().asFile.absolutePath)
                systemProperty("probe.evidenceDirectory", evidenceDirectory.get().absolutePath)
                inputs.property("probe.serverImage", libs.versions.axon.server.image)

                doFirst {
                    for (directory in listOf(workerHome.get().asFile, workerDirectory.get().asFile)) {
                        check(directory.deleteRecursively() && directory.mkdirs()) { "Cannot initialize $directory" }
                    }
                    val dockerEnvironment = listOf(
                        "DOCKER_HOST", "TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "TESTCONTAINERS_HOST_OVERRIDE",
                        "PATH", "LANG", "LC_ALL", "TMPDIR", "SystemRoot",
                    ).mapNotNull { key -> providers.environmentVariable(key).orNull?.let { key to it } }.toMap()
                    setEnvironment(dockerEnvironment + ("HOME" to workerHome.get().asFile.absolutePath))
                    systemProperty("probe.serverImage", libs.versions.axon.server.image.get())
                    systemProperty("probe.runId", providers.environmentVariable("PROBE_RUN_ID").orElse("").get())
                    systemProperty("probe.roleClasspath", roleClasspath.get().asPath)
                    systemProperty("probe.roleJava", roleLauncher.get().executablePath.asFile.absolutePath)
                }
            }
        }
    }

    register<JvmTestSuite>("kotestProbe") {
        useJUnitJupiter(libs.versions.junit.get())
        dependencies {
            implementation(libs.coroutines.core)
            implementation(libs.kotest.assertions)
            implementation(libs.kotest.property)
        }
        targets.configureEach {
            testTask.configure {
                val testClass = "probe.KotestInteropTest"
                val testCase = "Jupiter runs a seeded Kotest property"
                useJUnitPlatform { includeEngines("junit-jupiter") }
                filter.includeTestsMatching("$testClass.$testCase")
                filter.isFailOnNoMatchingTests = true
                systemProperty("probe.kotlinVersion", libs.versions.kotlin.get())
                timeout = Duration.ofMinutes(2)
                outputs.upToDateWhen { false }
                doLast {
                    verifySecondaryIsolation()
                    val report = reports.junitXml.outputLocation.get().asFile.resolve("TEST-$testClass.xml")
                    val xml = DocumentBuilderFactory.newDefaultInstance().apply {
                        setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)
                    }.newDocumentBuilder().parse(report)
                    val cases = xml.getElementsByTagName("testcase")
                    check(cases.length == 1 && cases.item(0).attributes.getNamedItem("name").nodeValue == "$testCase()" &&
                        xml.getElementsByTagName("failure").length == 0 && xml.getElementsByTagName("error").length == 0 &&
                        xml.getElementsByTagName("skipped").length == 0) { "Expected one passing Jupiter case: $testCase" }
                    val worker = xml.getElementsByTagName("system-out").item(0).textContent.lineSequence()
                        .single { it.startsWith("PROBE_KOTEST_WORKER ") }
                        .removePrefix("PROBE_KOTEST_WORKER ").split(' ', limit = 3)
                    val (vendor, build, architecture) = worker[2].split('|')
                    check(vendor == "Eclipse Adoptium" && Runtime.Version.parse(build).feature() == javaFeature.get()) {
                        "Unexpected Kotlin test worker: ${worker[2]}"
                    }
                    val expectedModules = mapOf(
                        "org.jetbrains.kotlin:kotlin-stdlib" to libs.versions.kotlin.get(),
                        "org.junit.platform:junit-platform-launcher" to libs.versions.junit.get(),
                        "org.junit.jupiter:junit-jupiter-engine" to libs.versions.junit.get(),
                        "io.kotest:kotest-assertions-core-jvm" to libs.versions.kotest.get(),
                        "io.kotest:kotest-property-jvm" to libs.versions.kotest.get(),
                    )
                    val selected = configurations.getByName("kotestProbeRuntimeClasspath").moduleVersions()
                    val resolved = selected.filterKeys { it in expectedModules }
                    check(resolved == expectedModules) { "Unexpected Jupiter/Kotest runtime modules: $resolved" }
                    val artifact = publishArtifact("kotest-junit.xml", report.readBytes())
                    observation("kotest", mapOf(
                        "artifacts" to listOf(artifact), "junitCase" to testCase, "testCount" to cases.length,
                        "propertySeed" to worker[0].toLong(), "propertyChecks" to worker[1].toInt(),
                        "resolvedModules" to resolved, "workerVendor" to vendor, "workerBuild" to build,
                        "workerArchitecture" to architecture, "coreDependenciesIsolated" to true,
                    ))
                }
            }
        }
    }

    register<JvmTestSuite>("typeIdJvmVectors") {
        useJUnitJupiter(libs.versions.junit.get())
        dependencies {
            implementation(platform(libs.spring.boot.bom))
            implementation(libs.jackson.databind)
            implementation(libs.typeid.java)
        }
        targets.configureEach {
            testTask.configure {
                val output = kotlinExchange.get().asFile
                inputs.file(typeIdFixture).withPathSensitivity(PathSensitivity.RELATIVE)
                outputs.file(kotlinExchange)
                outputs.upToDateWhen { false }
                useJUnitPlatform { includeEngines("junit-jupiter") }
                filter.includeTestsMatching("probe.TypeIdVectorsTest.*")
                filter.isFailOnNoMatchingTests = true
                systemProperty("probe.typeIdFixture", typeIdFixture.asFile.absolutePath)
                systemProperty("probe.typeIdKotlinExchange", output.absolutePath)
                systemProperty("probe.typeIdRunId", typeIdRunId.get())
                systemProperty("probe.typeIdExchangeId", typeIdExchangeId)
                timeout = Duration.ofMinutes(2)
                doFirst { check(!output.exists() || output.delete()) { "Could not clear old Kotlin exchange" } }
            }
        }
    }
}

kotlin.sourceSets.named("typeIdJvmVectors") {
    kotlin.setSrcDirs(listOf("src/typeIdProbe/kotlin"))
}

configurations.configureEach {
    if (name == "integrationTestImplementation") extendsFrom(configurations.implementation.get())
}

val kdocFormatter = configurations.resolvable("kdocFormatter")
dependencies { add(kdocFormatter.name, libs.ktfmt) }

val kdocFixture = layout.projectDirectory.file("kdoc/Specimen.kt")
val firstKdocPass = buildDirectory.file("kdoc/first/Specimen.kt")
val secondKdocPass = buildDirectory.file("kdoc/second/Specimen.kt")

fun JavaExec.formatKdoc(input: RegularFile, output: Provider<RegularFile>) {
    javaLauncher = roleLauncher
    classpath(kdocFormatter)
    mainClass = "org.jetbrains.kotlinx.ktfmt.cli.Main"
    inputs.file(input).withPathSensitivity(PathSensitivity.RELATIVE)
    outputs.file(output)
    timeout = Duration.ofMinutes(1)
    args("--kotlinlang-style", output.get().asFile.absolutePath)
    doFirst { input.asFile.copyTo(output.get().asFile, overwrite = true) }
}

val formatKdoc = tasks.register<JavaExec>("formatKdocSpecimen") {
    formatKdoc(kdocFixture, firstKdocPass)
}

tasks.register<JavaExec>("kdocProbe") {
    group = "verification"
    description = "Verify ktfmt KDoc reflow, content retention and idempotence."
    dependsOn(formatKdoc)
    formatKdoc(firstKdocPass.get(), secondKdocPass)
    outputs.upToDateWhen { false }
    doLast {
        verifySecondaryIsolation()
        val original = kdocFixture.asFile.readBytes()
        val first = firstKdocPass.get().asFile.readBytes()
        val second = secondKdocPass.get().asFile.readBytes()
        val lines = first.toString(Charsets.UTF_8).lineSequence()
            .dropWhile { it != "/**" }.drop(1).takeWhile { it != " */" }
            .map { it.removePrefix(" *").removePrefix(" ") }.toList()
        val paragraph = lines.takeWhile(String::isNotBlank)
        val expectedParagraph = "Normalizes a label with [String.trim] and preserves intentional whitespace in this example " +
            "so the formatter must reflow this paragraph without changing its words."
        check(!original.contentEquals(first) && paragraph.size > 1 && paragraph.joinToString(" ") == expectedParagraph) {
            "Expected ktfmt to wrap the long KDoc paragraph and retain its words and symbol link"
        }
        check(lines.drop(paragraph.size) == listOf(
            "", "- Trim leading whitespace.", "- Trim trailing whitespace.", "", "```kotlin",
            "val source = \"  example  \"", "val label = normalizeLabel(source)", "```", "",
            "@param source the untrimmed label", "@return the trimmed label",
        )) { "ktfmt changed the KDoc list, fenced example, or parameter/return tags: $lines" }
        check(first.contentEquals(second)) { "The second ktfmt pass changed the first pass bytes" }
        val version = kdocFormatter.get().moduleVersions().getValue("org.jetbrains.kotlinx:ktfmt")
        check(version == libs.versions.ktfmt.get()) { "Unexpected ktfmt version: $version" }
        val artifact = publishArtifact("kdoc-formatted.kt", first)
        observation("kdoc", mapOf(
            "artifacts" to listOf(artifact), "formatterVersion" to version, "style" to "kotlinlang",
            "beforeSha256" to sha256(original), "afterSha256" to sha256(first), "secondSha256" to sha256(second),
            "contentPreserved" to true, "coreDependenciesIsolated" to true,
        ))
    }
}

fun Exec.runFrontendTask(name: String) {
    val repository = rootProject.layout.projectDirectory
    workingDir(repository.asFile)
    commandLine(repository.file("gradlew").asFile, "--console=plain", "-p", "probe/web", name)
    if (gradle.startParameter.isRerunTasks) args("--rerun-tasks")
}

val frontendAssets = tasks.register<Exec>("frontendAssets") {
    group = "verification"
    description = "Build and verify the probe's static assets with the isolated npm build."
    runFrontendTask("frontendAssets")
    providers.gradleProperty("probeMarker").orNull?.let { args("-PprobeMarker=$it") }
}

tasks.register<Exec>("frontendImageProbe") {
    group = "verification"
    description = "Package and serve two static builds on a native ARM64 Docker daemon."
    mustRunAfter(frontendAssets)
    runFrontendTask("frontendImageProbe")
}
