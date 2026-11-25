import com.github.gradle.node.NodeExtension
import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.variant.VariantComputer
import com.github.gradle.node.variant.computeNodeExec
import com.github.gradle.node.variant.computeNpmScriptFile
import groovy.json.JsonOutput
import groovy.json.JsonSlurper
import java.io.ByteArrayInputStream

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

val bff = project(":bff")
val web = project(":web")
val docs = project(":docs-site")
val runningGradle = gradle.gradleVersion
val doctorScript = layout.projectDirectory.file("tools/doctor.py").asFile

fun doctorManagedTools(extension: NodeExtension): List<String> {
    val nodeDir = extension.resolvedNodeDir
    val platform = extension.resolvedPlatform
    val nodeBin = variants.computeNodeBinDir(nodeDir, platform)
    val npmDir = variants.computeNpmDir(extension, nodeDir)
    return listOf(
        computeNodeExec(extension, nodeBin).get(),
        computeNpmScriptFile(npmDir, "npm", platform.get().isWindows()).get(),
    )
}

tasks.register<Exec>("doctor") {
    group = "verification"
    description = "Report the observed toolchain and any repairs needed for each workflow."
    notCompatibleWithConfigurationCache("Observes the local toolchains and managed executables.")
    commandLine("python3", doctorScript, "--gradle-input")
    doFirst {
        val worker = runCatching {
            val spec = bff.extensions.getByType<JavaPluginExtension>().toolchain
            val toolchains = bff.extensions.getByType<JavaToolchainService>()
            toolchains.launcherFor(spec).get().executablePath.asFile.absolutePath
        }
            .getOrNull()
        val npm =
            mapOf("tools/style" to rootProject, "web" to web, "docs-site" to docs)
                .mapValues { (_, project) ->
                    runCatching {
                            doctorManagedTools(project.extensions.getByType<NodeExtension>())
                        }
                        .getOrDefault(emptyList())
                }
                .toMutableMap()
        // The TypeID consumer runs the standalone probe/web build with a different package
        // directory.
        val probe = layout.projectDirectory.dir("probe/web")
        val probeTools = runCatching {
            val manifest = JsonSlurper().parse(probe.file("package.json").asFile) as Map<*, *>
            val version = (manifest["packageManager"] as String).removePrefix("npm@")
            val platform = nodeExtension.resolvedPlatform.get()
            val nodeDir =
                probe.dir(".gradle/nodejs/node-v$selectedNode-${platform.name}-${platform.arch}")
            val npmDir = probe.dir(".gradle/npm/npm-v$version")
            val nodeBin =
                variants.computeNodeBinDir(provider { nodeDir }, nodeExtension.resolvedPlatform)
            listOf(
                computeNodeExec(nodeExtension, nodeBin).get(),
                computeNpmScriptFile(provider { npmDir }, "npm", platform.isWindows()).get(),
            )
        }
            .getOrDefault(emptyList())
        npm["probe/web"] = probeTools
        npm["probe/typeid"] = probeTools
        val data =
            JsonOutput.toJson(mapOf("gradle" to runningGradle, "worker" to worker, "npm" to npm))
        standardInput = ByteArrayInputStream(data.toByteArray(Charsets.UTF_8))
    }
}
