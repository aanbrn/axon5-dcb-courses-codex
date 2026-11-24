import java.time.Duration

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

                val evidenceDirectory = providers.environmentVariable("PROBE_EVIDENCE_DIR")
                    .map { rootProject.file(it) }
                    .orElse(buildDirectory.dir("reports/feasibility").map { it.asFile })
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
}

configurations.configureEach {
    if (name == "integrationTestImplementation") extendsFrom(configurations.implementation.get())
}

tasks.register<Exec>("frontendAssets") {
    group = "verification"
    description = "Build and verify the probe's static assets with the isolated npm build."
    val marker = providers.gradleProperty("probeMarker")
    val repository = rootProject.layout.projectDirectory
    workingDir(repository.asFile)
    commandLine(repository.file("gradlew").asFile, "--console=plain", "-p", "probe/web", "frontendAssets")
    if (gradle.startParameter.isRerunTasks) args("--rerun-tasks")
    marker.orNull?.let { args("-PprobeMarker=$it") }
}
