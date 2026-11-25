import com.github.gradle.node.NodeExtension
import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.variant.VariantComputer
import com.github.gradle.node.variant.computeNodeExec
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

plugins {
    base
    alias(libs.plugins.kotlin.jvm) apply false
    alias(libs.plugins.kotlin.spring) apply false
    alias(libs.plugins.gradle.node)
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

val nodeOwner = layout.projectDirectory.file(".nvmrc")
val styleManifest = layout.projectDirectory.file("tools/style/package.json")
val styleLock = layout.projectDirectory.file("tools/style/package-lock.json")
val selectedNode = providers.fileContents(nodeOwner).asText.get().trim()
val packageManager =
    (JsonSlurper().parse(styleManifest.asFile) as Map<*, *>)["packageManager"] as String
val selectedNpm = packageManager.removePrefix("npm@")
val exactVersion = Regex("[0-9]+\\.[0-9]+\\.[0-9]+")

require(exactVersion.matches(selectedNode)) { ".nvmrc must pin an exact Node release" }

require(packageManager == "npm@$selectedNpm" && exactVersion.matches(selectedNpm)) {
    "tools/style/package.json must pin an exact npm release"
}

node {
    version = selectedNode
    npmVersion = selectedNpm
    download = true
    npmInstallCommand = "ci"
    nodeProjectDir = layout.projectDirectory.dir("tools/style")
}

val npmInstall =
    tasks.named<NpmInstallTask>("npmInstall") {
        args = listOf("--strict-peer-deps", "--ignore-scripts", "--no-audit", "--no-fund")
        inputs
            .files(nodeOwner, styleManifest, styleLock)
            .withPathSensitivity(PathSensitivity.RELATIVE)
        inputs.property("npmVersion", selectedNpm)
        lateinit var lockBefore: ByteArray
        doFirst { lockBefore = styleLock.asFile.readBytes() }
        doLast {
            check(styleLock.asFile.readBytes().contentEquals(lockBefore)) {
                "npm ci changed tools/style/package-lock.json"
            }
        }
    }

val styleCommands = layout.buildDirectory.file("style/commands.json")
val kotlinCommands = project(":bff").layout.buildDirectory.file("kotlin-quality/commands.json")
val prettier = layout.projectDirectory.file("tools/style/node_modules/prettier/bin/prettier.cjs")
val webModules = layout.projectDirectory.dir("web/node_modules")
val steiger = webModules.file("steiger/dist/cli.mjs")
val styleDriver = layout.projectDirectory.file("tools/style/run.py").asFile

val nodeExtension = extensions.getByType<NodeExtension>()
val variants = VariantComputer()
val nodeBinDir =
    variants.computeNodeBinDir(nodeExtension.resolvedNodeDir, nodeExtension.resolvedPlatform)
val nodeExecutable = computeNodeExec(nodeExtension, nodeBinDir)

val styleRuntime =
    tasks.register("styleRuntime") {
        group = "build setup"
        description =
            "Provision the locked formatter and linter commands used by repository style checks."
        dependsOn(npmInstall, ":bff:kotlinQualityRuntime", ":web:npmInstall")
        inputs.files(kotlinCommands, prettier, steiger)
        inputs.property("nodeExecutable", nodeExecutable)
        outputs.file(styleCommands)
        doLast {
            val kotlin = JsonSlurper().parse(kotlinCommands.get().asFile) as Map<*, *>
            val detekt = kotlin["detekt"] as List<*>
            check(detekt.getOrNull(detekt.size - 2) == "--config") {
                "Expected kotlinQualityRuntime to export the detekt command with its config."
            }
            val commands =
                mapOf(
                    "ktfmt" to kotlin["ktfmt"],
                    "detekt" to detekt.dropLast(2),
                    "prettier" to listOf(nodeExecutable.get(), prettier.asFile.absolutePath),
                    "steiger" to listOf(nodeExecutable.get(), steiger.asFile.absolutePath),
                    "webModules" to webModules.asFile.absolutePath,
                )
            styleCommands.get().asFile.writeText(JsonOutput.toJson(commands) + "\n")
        }
    }

tasks.register<Exec>("styleCheck") {
    group = "verification"
    description = "Check formatting and lint for the tracked checkout without editing sources."
    dependsOn(styleRuntime)
    commandLine("python3", styleDriver, "--check", "--runtime", styleCommands.get().asFile)
}

tasks.register<Exec>("installGitHooks") {
    group = "build setup"
    description = "Opt in to the repository pre-commit hook in this local Git repository."
    dependsOn(styleRuntime)
    commandLine("git", "config", "--local", "core.hooksPath", ".githooks")
}
