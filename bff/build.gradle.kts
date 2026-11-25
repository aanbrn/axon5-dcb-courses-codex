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
        implementation(libs.kotest.assertions)
        implementation(libs.kotest.property)
    }
}

val openApiElements = configurations.consumable("openApiElements")
val bootExecutableElements = configurations.consumable("bootExecutableElements")

artifacts {
    add(openApiElements.name, layout.projectDirectory.file("src/main/resources/static/openapi.json"))
    add(bootExecutableElements.name, tasks.named<BootJar>("bootJar"))
}
