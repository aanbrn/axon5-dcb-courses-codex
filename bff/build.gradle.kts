import org.gradle.api.artifacts.component.ModuleComponentIdentifier
import org.gradle.api.artifacts.component.ProjectComponentIdentifier
import org.springframework.boot.gradle.tasks.bundling.BootJar

plugins {
    id("courses.jvm")
    alias(libs.plugins.kotlin.spring)
    alias(libs.plugins.spring.boot)
}

dependencies {
    implementation(platform(libs.spring.boot.bom))
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation(kotlin("reflect"))
}

testing.suites.named<JvmTestSuite>("test") {
    dependencies {
        implementation(testFixtures(project(":fixtures")))
        implementation(libs.coroutines.core)
        implementation(libs.kotest.assertions)
        implementation(libs.kotest.property)
    }
}

val openApiSource = layout.projectDirectory.file("src/main/resources/static/openapi.json")

val componentTest = testing.suites.register<JvmTestSuite>("componentTest") {
    dependencies {
        implementation(project())
        implementation(testFixtures(project(":fixtures")))
        implementation(platform(libs.spring.boot.bom))
        implementation(libs.jackson.databind)
        implementation(libs.networknt.validator)
        implementation("org.springframework.boot:spring-boot-test")
        implementation("org.springframework:spring-test")
    }

    targets.configureEach {
        testTask.configure {
            inputs.file(openApiSource).withPathSensitivity(PathSensitivity.RELATIVE)
            systemProperty("courses.openapi.source", openApiSource.asFile.absolutePath)
        }
    }
}

val fixtureConsumerClasspaths = listOf(
    "testCompileClasspath",
    "testRuntimeClasspath",
    "componentTestCompileClasspath",
    "componentTestRuntimeClasspath",
)

val verifyFixtureIsolation = tasks.register("verifyFixtureIsolation") {
    group = "verification"
    description = "Verify JVM suite fixture variants and an isolated BFF production runtime."

    fixtureConsumerClasspaths.forEach { name ->
        inputs.property(name, configurations.named(name).map { configuration ->
            configuration.incoming.resolutionResult.allComponents.any { component ->
                val id = component.id
                id is ProjectComponentIdentifier && id.buildTreePath == ":fixtures" &&
                    component.variants.any { variant ->
                        variant.capabilities.any { it.name == "fixtures-test-fixtures" }
                    }
            }
        })
    }
    inputs.property("runtimeLeaks", configurations.runtimeClasspath.map { configuration ->
        configuration.incoming.resolutionResult.allComponents.mapNotNull { component ->
            when (val id = component.id) {
                is ProjectComponentIdentifier -> id.buildTreePath.takeIf { it == ":fixtures" }
                is ModuleComponentIdentifier -> id.displayName.takeIf {
                    id.group == "io.kotest" ||
                        (id.group == "com.networknt" && id.module == "json-schema-validator")
                }
                else -> null
            }
        }.sorted()
    })

    doLast {
        val properties = inputs.properties
        fixtureConsumerClasspaths.forEach { name ->
            check(properties.getValue(name) == true) {
                "$name did not resolve the :fixtures test-fixtures variant"
            }
        }
        val leaks = properties.getValue("runtimeLeaks") as List<*>
        check(leaks.isEmpty()) { "Test dependencies leaked into :bff:runtimeClasspath: $leaks" }
    }
}

tasks.check {
    dependsOn(componentTest, verifyFixtureIsolation)
}

val openApiElements = configurations.consumable("openApiElements")
val bootExecutableElements = configurations.consumable("bootExecutableElements")

artifacts {
    add(openApiElements.name, openApiSource)
    add(bootExecutableElements.name, tasks.named<BootJar>("bootJar"))
}
