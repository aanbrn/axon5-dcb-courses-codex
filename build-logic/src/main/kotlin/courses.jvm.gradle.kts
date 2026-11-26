import org.gradle.api.artifacts.VersionCatalogsExtension

plugins {
    id("org.jetbrains.kotlin.jvm")
    id("jvm-test-suite")
}

val javaFeature =
    providers.fileContents(rootProject.layout.projectDirectory.file(".java-version")).asText.map {
        it.trim().toInt()
    }
val catalog = extensions.getByType<VersionCatalogsExtension>().named("libs")

java {
    toolchain {
        languageVersion = javaFeature.map(JavaLanguageVersion::of)
        vendor = JvmVendorSpec.ADOPTIUM
    }
}

val testLauncher: Provider<JavaLauncher> = javaToolchains.launcherFor(java.toolchain)
val jupiterVersion = catalog.findVersion("junit").get().requiredVersion

testing.suites.withType<JvmTestSuite>().configureEach {
    useJUnitJupiter(jupiterVersion)

    targets.configureEach {
        testTask.configure {
            javaLauncher = testLauncher
            filter.isFailOnNoMatchingTests = true
        }
    }
}
