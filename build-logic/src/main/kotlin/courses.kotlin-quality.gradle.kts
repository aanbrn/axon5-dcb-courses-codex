import groovy.json.JsonOutput
import org.gradle.api.artifacts.VersionCatalogsExtension
import org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension

plugins {
    id("courses.jvm")
    id("org.jetbrains.dokka")
}

val catalog = extensions.getByType<VersionCatalogsExtension>().named("libs")
val ktfmtDependencies = configurations.dependencyScope("ktfmtDependencies")
val ktfmtTool = configurations.resolvable("ktfmtTool") { extendsFrom(ktfmtDependencies.get()) }
val detektDependencies = configurations.dependencyScope("detektDependencies")
val detektCommentsTool =
    configurations.resolvable("detektCommentsTool") { extendsFrom(detektDependencies.get()) }

dependencies {
    add(ktfmtDependencies.name, catalog.findLibrary("ktfmt").get())
    constraints {
        add(ktfmtDependencies.name, catalog.findLibrary("guava-jre").get()) {
            because(
                "The formatter graph must select a Guava release with the GHSA-xxph-c9ww-hj94 fix",
            )
        }
    }
    add(detektDependencies.name, catalog.findLibrary("detekt-cli").get())
}

val toolLauncher = javaToolchains.launcherFor(java.toolchain)
val ktfmtMain = "org.jetbrains.kotlinx.ktfmt.cli.Main"
val ktfmtStyle = "--kotlinlang-style"
val detektMain = "io.gitlab.arturbosch.detekt.cli.Main"
val commentsConfig = rootProject.layout.projectDirectory.file("config/detekt/comments.yml")
val detektOptions = listOf("--config", commentsConfig.asFile.absolutePath)

val kotlinSources = objects.fileCollection()

extensions.getByType<KotlinJvmProjectExtension>().sourceSets.configureEach {
    kotlinSources.from(kotlin)
}

kotlinSources.from(fileTree(layout.projectDirectory) { include("*.gradle.kts") })

val kotlinFiles = kotlinSources.asFileTree.matching { include("**/*.kt", "**/*.kts") }

val ktfmtCheck =
    tasks.register<JavaExec>("ktfmtCheck") {
        group = "verification"
        description = "Check Kotlin and KDoc formatting with ktfmt."
        javaLauncher = toolLauncher
        classpath(ktfmtTool)
        mainClass = ktfmtMain
        args(ktfmtStyle, "--dry-run", "--set-exit-if-changed")
        inputs.files(kotlinFiles).withPathSensitivity(PathSensitivity.RELATIVE)
        argumentProviders.add(
            CommandLineArgumentProvider {
                kotlinFiles.files.map(File::getAbsolutePath).sorted()
            },
        )
        onlyIf { !kotlinFiles.isEmpty }
    }

val detektComments =
    tasks.register<JavaExec>("detektComments") {
        group = "verification"
        description = "Check KDoc with the repository's detekt comments rules."
        javaLauncher = toolLauncher
        classpath(detektCommentsTool)
        mainClass = detektMain
        args(detektOptions)
        inputs.file(commentsConfig).withPathSensitivity(PathSensitivity.RELATIVE)
        inputs.files(kotlinFiles).withPathSensitivity(PathSensitivity.RELATIVE)
        argumentProviders.add(
            CommandLineArgumentProvider {
                listOf(
                    "--input",
                    kotlinFiles.files.map(File::getAbsolutePath).sorted().joinToString(","),
                )
            },
        )
        onlyIf { !kotlinFiles.isEmpty }
    }

tasks.register("kotlinQualityRuntime") {
    group = "build setup"
    description = "Write the shared formatter and analyzer command prefixes for repository tooling."
    val formatter = files(ktfmtTool)
    val analyzer = files(detektCommentsTool)
    val javaExecutable = toolLauncher.map { it.executablePath.asFile.absolutePath }
    val commandsFile = layout.buildDirectory.file("kotlin-quality/commands.json")
    inputs.files(formatter, analyzer)
    inputs.property("javaExecutable", javaExecutable)
    inputs.property("ktfmtMain", ktfmtMain)
    inputs.property("ktfmtStyle", ktfmtStyle)
    inputs.property("detektMain", detektMain)
    inputs.property("detektOptions", detektOptions)
    outputs.file(commandsFile)
    doLast {
        val commands =
            mapOf(
                "ktfmt" to
                    listOf(javaExecutable.get(), "-cp", formatter.asPath, ktfmtMain, ktfmtStyle),
                "detekt" to
                    listOf(javaExecutable.get(), "-cp", analyzer.asPath, detektMain) +
                        detektOptions,
            )
        commandsFile.get().asFile.writeText(JsonOutput.toJson(commands) + "\n")
    }
}

val publicationSourceSet = objects.property<String>().convention("main")

pluginManager.withPlugin("java-test-fixtures") { publicationSourceSet.set("testFixtures") }

dokka {
    dokkaPublications.named("html") {
        failOnWarning.set(true)
        offlineMode.set(true)
    }
    dokkaSourceSets.configureEach {
        val sourceSetName = name
        suppress.set(publicationSourceSet.map { it != sourceSetName })
        reportUndocumented.set(true)
    }
}

tasks.check {
    dependsOn(ktfmtCheck, detektComments, tasks.named("dokkaGeneratePublicationHtml"))
}
