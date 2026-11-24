import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.npm.task.NpmTask
import com.github.gradle.node.task.NodeTask
import groovy.json.JsonOutput
import groovy.json.JsonSlurper
import java.io.ByteArrayOutputStream
import java.nio.file.Files
import java.nio.file.LinkOption.NOFOLLOW_LINKS
import java.security.MessageDigest
import java.time.Duration
import java.util.HexFormat

plugins {
    alias(libs.plugins.gradle.node)
}

val probeRoot = projectDir.parentFile.canonicalFile
val repository = probeRoot.parentFile
val webDirectory = layout.projectDirectory
val defaultMarker = "phase-one-static"
val mainMarker = providers.gradleProperty("probeMarker").orElse(defaultMarker)
val staticScript = webDirectory.file("build.mjs")
val nodeOwner = repository.resolve(".nvmrc")
val semver = Regex("[0-9]+\\.[0-9]+\\.[0-9]+")

fun probePath(path: String): File {
    val file = repository.resolve(path).canonicalFile
    require(file.toPath().startsWith(probeRoot.toPath())) { "npm path must stay inside probe: $path" }
    return file
}

fun npmFile(directory: File, name: String): File {
    val file = directory.resolve(name)
    require(Files.isRegularFile(file.toPath(), NOFOLLOW_LINKS)) { "Expected regular npm input $file" }
    return file
}

fun packageJson(file: File) = JsonSlurper().parse(file) as Map<*, *>

val npmDirectory = probePath(providers.gradleProperty("probeNpmDir").orElse("probe/web").get())
val npmScript = providers.gradleProperty("probeNpmScript").orElse("build")
val manifest = npmFile(npmDirectory, "package.json")
val lockfile = npmFile(npmDirectory, "package-lock.json")
val staticManifest = npmFile(projectDir, "package.json")
val staticLockfile = npmFile(projectDir, "package-lock.json")
val selectedNode = nodeOwner.readText().trim()
val packageManager = packageJson(staticManifest)["packageManager"] as? String ?: ""
val selectedNpm = packageManager.removePrefix("npm@")
require(semver.matches(selectedNode)) { ".nvmrc must pin Node to an exact release" }
require(packageManager == "npm@$selectedNpm" && semver.matches(selectedNpm)) {
    "The web manifest must pin npm to an exact release"
}

node {
    version = selectedNode
    npmVersion = selectedNpm
    download = true
    npmInstallCommand = "ci"
    nodeProjectDir = layout.dir(provider { npmDirectory })
}

val nodeVersion = tasks.register<NodeTask>("verifyNodeVersion") {
    script = staticScript
    options = listOf("--version")
    val output = ByteArrayOutputStream()
    execOverrides { standardOutput = output }
    doLast {
        check(output.toString(Charsets.UTF_8).trim() == "v$selectedNode") { "Unexpected Node version: $output" }
    }
}
val npmVersion = tasks.register<NpmTask>("verifyNpmVersion") {
    args = listOf("--version")
    val output = ByteArrayOutputStream()
    execOverrides { standardOutput = output }
    doLast {
        check(output.toString(Charsets.UTF_8).trim() == selectedNpm) { "Unexpected npm version: $output" }
    }
}

val npmInstall = tasks.named<NpmInstallTask>("npmInstall") {
    dependsOn(nodeVersion, npmVersion)
    args = listOf("--no-audit", "--no-fund")
    timeout = Duration.ofMinutes(3)
    lateinit var before: ByteArray
    doFirst { before = lockfile.readBytes() }
    doLast { check(lockfile.readBytes().contentEquals(before)) { "npm ci changed $lockfile" } }
}

fun NpmTask.runScript(directory: File, name: Provider<String>, lock: File) {
    dependsOn(npmInstall)
    args = name.map { listOf("run", it) }
    workingDir = directory
    inputs.files(nodeOwner, staticManifest, directory.resolve("package.json"), lock)
        .withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("nodeVersion", selectedNode)
    inputs.property("npmVersion", selectedNpm)
    timeout = Duration.ofMinutes(2)
    lateinit var before: ByteArray
    doFirst {
        val scriptName = name.get()
        require(scriptName.matches(Regex("[a-zA-Z0-9][a-zA-Z0-9:_-]*"))) { "Invalid npm script: $scriptName" }
        val scripts = packageJson(directory.resolve("package.json"))["scripts"] as? Map<*, *>
        require(scripts?.get(scriptName) is String) { "Missing npm script $scriptName in $directory" }
        before = lock.readBytes()
    }
    doLast { check(lock.readBytes().contentEquals(before)) { "npm script changed $lock" } }
}

fun validateStage(directory: File, marker: String): ByteArray {
    val root = directory.toPath()
    val publicDirectory = root.resolve("public")
    val index = publicDirectory.resolve("index.html")
    check(Files.isDirectory(root, NOFOLLOW_LINKS) && root.toRealPath() == root.toAbsolutePath().normalize()) {
        "Invalid staging root $root"
    }
    Files.walk(root).use { tree ->
        check(tree.toList().toSet() == setOf(root, publicDirectory, index)) { "Unexpected files in $root" }
    }
    check(Files.isDirectory(publicDirectory, NOFOLLOW_LINKS) && Files.isRegularFile(index, NOFOLLOW_LINKS)) {
        "Invalid staged asset tree in $root"
    }
    val bytes = Files.readAllBytes(index)
    check(bytes.toString(Charsets.UTF_8).contains("<p id=\"marker\">$marker</p>")) { "Expected marker $marker in $index" }
    return bytes
}

fun stageStatic(name: String, marker: Provider<String>, staging: String) = tasks.register<NpmTask>(name) {
    require(npmDirectory == projectDir.canonicalFile) { "$name requires probe/web npm inputs" }
    val destination = layout.buildDirectory.dir(staging)
    runScript(projectDir, provider { "build" }, staticLockfile)
    environment.put("PROBE_MARKER", marker)
    environment.put("PROBE_STAGING", staging)
    inputs.file(staticScript).withPathSensitivity(PathSensitivity.RELATIVE)
    outputs.dir(destination)
    doLast { validateStage(destination.get().asFile, marker.get()) }
}

fun sha256(bytes: ByteArray): String = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes))

val evidenceDirectory = providers.environmentVariable("PROBE_EVIDENCE_DIR")
    .map(repository::resolve)
    .orElse(probeRoot.resolve("build/reports/feasibility"))

val staticAssets = stageStatic("stageStaticAssets", mainMarker, "staged")

tasks.register("frontendAssets") {
    dependsOn(staticAssets)
    doLast {
        val bytes = validateStage(layout.buildDirectory.dir("staged").get().asFile, mainMarker.get())
        val artifact = "frontend-assets.html"
        val directory = evidenceDirectory.get()
        directory.mkdirs()
        directory.resolve(artifact).writeBytes(bytes)
        val observation = mapOf(
            "stage" to "frontend-assets",
            "artifacts" to listOf(artifact),
            "nodeVersion" to "v$selectedNode",
            "npmVersion" to selectedNpm,
            "stagedSha256" to sha256(bytes),
            "lockfileSha256" to sha256(staticLockfile.readBytes()),
            "stagedTreeValidated" to true,
        )
        println("PROBE_SECONDARY ${JsonOutput.toJson(observation)}")
    }
}

fun declaredPaths(property: String) = providers.gradleProperty(property).map { paths ->
    paths.split(',').map { probePath(it.trim()) }
}.orElse(emptyList())

tasks.register("scopedNpmBuild") {
    if (npmDirectory == projectDir.canonicalFile && npmScript.get() == "build") {
        dependsOn(staticAssets)
    } else {
        dependsOn("runScopedNpmScript")
    }
}

tasks.register<NpmTask>("runScopedNpmScript") {
    runScript(npmDirectory, npmScript, lockfile)
    inputs.files(fileTree(npmDirectory) { exclude("build/**", "node_modules/**", ".gradle/**", "dist/**") })
        .withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.files(declaredPaths("probeNpmInputs")).withPathSensitivity(PathSensitivity.RELATIVE)
    outputs.files(declaredPaths("probeNpmOutputs"))
    outputs.upToDateWhen { declaredPaths("probeNpmOutputs").get().isNotEmpty() }
}
