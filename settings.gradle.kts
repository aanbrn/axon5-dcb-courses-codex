pluginManagement {
    includeBuild("build-logic")

    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
}

rootProject.name = "axon5-dcb-courses"

include(":probe", ":bff", ":web", ":docs-site")

if (file("fixtures").isDirectory) {
    include(":fixtures")
}
