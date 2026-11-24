import java.time.Duration

plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.spring)
    id("jvm-test-suite")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(libs.versions.jdk.get().toInt())
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
}

val roleClasspath = sourceSets.main.map { it.runtimeClasspath }
val roleLauncher = javaToolchains.launcherFor(java.toolchain)
val buildDirectory = layout.buildDirectory

testing.suites {
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
                javaLauncher = roleLauncher
                filter.isFailOnNoMatchingTests = true
                timeout = Duration.ofMinutes(5)
                testLogging.showStandardStreams = true

                val evidenceDirectory = providers.environmentVariable("PROBE_EVIDENCE_DIR")
                    .map { rootProject.file(it) }
                    .orElse(buildDirectory.dir("reports/feasibility").map { it.asFile })
                val workerHome = buildDirectory.dir("tmp/integrationTest/worker-home")
                val workerDirectory = buildDirectory.dir("tmp/integrationTest/worker-work")
                val dockerEnvironment = listOf(
                    "DOCKER_HOST", "TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE", "TESTCONTAINERS_HOST_OVERRIDE",
                    "PATH", "LANG", "LC_ALL", "TMPDIR", "SystemRoot",
                ).mapNotNull { key -> providers.environmentVariable(key).orNull?.let { key to it } }.toMap()

                setEnvironment(dockerEnvironment + ("HOME" to workerHome.get().asFile.absolutePath))
                workingDir(workerDirectory)
                systemProperty("user.home", workerHome.get().asFile.absolutePath)
                systemProperty("probe.evidenceDirectory", evidenceDirectory.get().absolutePath)
                systemProperty("probe.serverImage", libs.versions.axon.server.image.get())
                systemProperty("probe.runId", providers.environmentVariable("PROBE_RUN_ID").orElse("").get())

                doFirst {
                    for (directory in listOf(workerHome.get().asFile, workerDirectory.get().asFile)) {
                        check(directory.deleteRecursively() && directory.mkdirs()) { "Cannot initialize $directory" }
                    }
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
