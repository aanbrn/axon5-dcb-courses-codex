import org.springframework.boot.gradle.tasks.bundling.BootJar

plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.spring)
    alias(libs.plugins.spring.boot)
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
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation(kotlin("reflect"))
}

val openApiElements = configurations.consumable("openApiElements")
val bootExecutableElements = configurations.consumable("bootExecutableElements")

artifacts {
    add(openApiElements.name, layout.projectDirectory.file("src/main/resources/static/openapi.json"))
    add(bootExecutableElements.name, tasks.named<BootJar>("bootJar"))
}
