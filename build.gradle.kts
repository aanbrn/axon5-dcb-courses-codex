plugins {
    base
    alias(libs.plugins.kotlin.jvm) apply false
    alias(libs.plugins.kotlin.spring) apply false
    id("courses.jvm") apply false
}

val applicationProjects = listOf(project(":bff"), project(":web"))

listOf(tasks.clean, tasks.assemble, tasks.check).forEach { lifecycle ->
    lifecycle.configure {
        val taskName = name
        dependsOn(
            applicationProjects.map { application ->
                providers.provider { application.tasks.named(taskName) }
            },
        )
    }
}
