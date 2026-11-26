import groovy.json.JsonOutput
import java.io.ByteArrayOutputStream
import java.nio.file.Files
import javax.inject.Inject
import org.gradle.api.artifacts.VersionCatalogsExtension
import org.gradle.process.ExecOperations
import org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension

plugins {
    id("courses.jvm")
    id("org.jetbrains.dokka")
}

abstract class DetektCommentsTask : DefaultTask() {
    @get:InputFiles
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val sources: ConfigurableFileCollection

    @get:InputFile
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val rules: RegularFileProperty

    @get:Classpath abstract val toolClasspath: ConfigurableFileCollection

    @get:Input abstract val analyzerMain: Property<String>

    @get:Nested abstract val launcher: Property<JavaLauncher>

    @get:Inject protected abstract val execOperations: ExecOperations

    @TaskAction
    fun checkComments() {
        val scratch = Files.createTempDirectory(temporaryDir.toPath(), "detekt-").toFile()
        try {
            val copies =
                sources.files.sorted().mapIndexed { index, source ->
                    val copy = scratch.resolve("$index/${source.name.replace(',', '_')}")
                    source.copyTo(copy)
                    copy.canonicalPath to source.absolutePath
                }
            val output = ByteArrayOutputStream()
            val result = execOperations.javaexec {
                executable = launcher.get().executablePath.asFile.absolutePath
                classpath(toolClasspath)
                mainClass.set(analyzerMain)
                workingDir(scratch)
                // detekt splits --input on commas, including commas in absolute checkout paths.
                args("--config", rules.get().asFile.absolutePath, "--input", ".")
                standardOutput = output
                errorOutput = output
                isIgnoreExitValue = true
            }
            val diagnostics =
                copies.fold(output.toString(Charsets.UTF_8)) { message, (copy, source) ->
                    message.replace(copy, source)
                }
            if (diagnostics.isNotBlank()) logger.lifecycle(diagnostics.trimEnd())
            result.assertNormalExitValue()
        } finally {
            scratch.deleteRecursively()
        }
    }
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

val toolLauncher: Provider<JavaLauncher> = javaToolchains.launcherFor(java.toolchain)
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
    tasks.register<DetektCommentsTask>("detektComments") {
        group = "verification"
        description = "Check KDoc with the repository's detekt comments rules."
        launcher = toolLauncher
        toolClasspath.from(detektCommentsTool)
        analyzerMain = detektMain
        rules = commentsConfig
        sources.from(kotlinFiles)
        onlyIf { !sources.isEmpty }
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
