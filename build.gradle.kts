plugins {
    base
    alias(libs.plugins.kotlin.jvm) apply false
    alias(libs.plugins.kotlin.spring) apply false
    id("courses.jvm") apply false
}

val productionProjects = listOf(project(":bff"), project(":web"), project(":docs-site"))

listOf(tasks.clean, tasks.assemble, tasks.check).forEach { lifecycle ->
    lifecycle.configure {
        val taskName = name
        dependsOn(
            productionProjects.map { project ->
                providers.provider { project.tasks.named(taskName) }
            },
        )
    }
}
