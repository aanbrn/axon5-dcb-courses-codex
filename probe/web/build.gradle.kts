import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.npm.task.NpmTask
import com.github.gradle.node.task.NodeTask
import groovy.json.JsonOutput
import groovy.json.JsonSlurper
import java.io.ByteArrayOutputStream
import java.net.ProxySelector
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.file.Files
import java.nio.file.LinkOption.NOFOLLOW_LINKS
import java.security.MessageDigest
import java.time.Duration
import java.util.HexFormat
import java.util.UUID
import java.util.concurrent.ExecutionException
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

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
        val actual = output.toString(Charsets.UTF_8).trim()
        println("PROBE_TOOL node $actual")
        check(actual == "v$selectedNode") { "Unexpected Node version: $actual" }
    }
}
val npmVersion = tasks.register<NpmTask>("verifyNpmVersion") {
    args = listOf("--version")
    val output = ByteArrayOutputStream()
    execOverrides { standardOutput = output }
    doLast {
        val actual = output.toString(Charsets.UTF_8).trim()
        println("PROBE_TOOL npm $actual")
        check(actual == selectedNpm) { "Unexpected npm version: $actual" }
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

data class PaketoImage(val index: String, val armChild: String, val armConfig: String) {
    val nativeRef: String = index.substringBefore('@').substringBefore(':') + "@$armChild"

    fun evidence() = mapOf("index" to index, "arm64Manifest" to armChild, "arm64Config" to armConfig)
}

data class StaticBuild(val staging: String, val marker: String)

val firstImageBuild = StaticBuild("staged-image-first", "phase-one-static-first")
val secondImageBuild = StaticBuild("staged-image-second", "phase-one-static-second")
val firstImageAssets = stageStatic("stageFirstImageAssets", provider { firstImageBuild.marker }, firstImageBuild.staging)
val secondImageAssets = stageStatic("stageSecondImageAssets", provider { secondImageBuild.marker }, secondImageBuild.staging)
secondImageAssets.configure { mustRunAfter(firstImageAssets) }

fun boundedCommand(work: File, stage: String, seconds: Long, vararg argv: String): String {
    val log = Files.createTempFile(work.toPath(), "command-", ".txt")
    try {
        val process = ProcessBuilder(*argv).directory(work).redirectErrorStream(true).redirectOutput(log.toFile()).start()
        try {
            check(process.waitFor(seconds, TimeUnit.SECONDS)) { "$stage: command timed out: ${argv.joinToString(" ")}" }
        } finally {
            if (process.isAlive) {
                val ownedChildren = process.descendants().toList()
                ownedChildren.forEach { it.destroy() }
                process.destroy()
                if (!process.waitFor(3, TimeUnit.SECONDS)) {
                    process.destroyForcibly()
                    process.waitFor(3, TimeUnit.SECONDS)
                }
                ownedChildren.filter { it.isAlive }.forEach { it.destroyForcibly() }
            }
        }
        val output = Files.readString(log).trim()
        check(process.exitValue() == 0) { "$stage: exit ${process.exitValue()}: ${argv.joinToString(" ")}\n$output" }
        return output
    } catch (error: Exception) {
        if (error is InterruptedException) Thread.currentThread().interrupt()
        val details = Files.readString(log).trim()
        if (details.isNotEmpty()) logger.error(details)
        throw IllegalStateException("Frontend image $stage failed: ${error.message}", error)
    } finally {
        Files.deleteIfExists(log)
    }
}

fun awaitResponse(client: HttpClient, port: Int): HttpResponse<ByteArray> {
    val request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:$port/"))
        .timeout(Duration.ofSeconds(3)).GET().build()
    val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(30)
    var lastFailure = "No response"
    while (System.nanoTime() < deadline) {
        val response = client.sendAsync(request, HttpResponse.BodyHandlers.ofByteArray())
        try {
            return response.get(3, TimeUnit.SECONDS)
        } catch (error: ExecutionException) {
            lastFailure = error.cause?.toString() ?: error.toString()
        } catch (error: TimeoutException) {
            lastFailure = error.toString()
        } finally {
            if (!response.isDone) response.cancel(true)
        }
        Thread.sleep(250)
    }
    error("HTTP readiness timed out on the loopback port: $lastFailure")
}

class NativePackaging(
    private val work: File,
    private val builder: PaketoImage,
    private val runImage: PaketoImage,
    private val buildpack: PaketoImage,
) {
    private val platform = "linux/arm64"

    fun prepare(packVersion: String): Map<String, Any> {
        val actualPack = boundedCommand(work, "Pack version", 10, "pack", "--version")
        println("PROBE_TOOL pack $actualPack")
        check(actualPack.substringBefore('+') == packVersion) { "Pack $packVersion is required, found $actualPack" }
        val daemon = docker("Docker platform", "info", "--format", "{{.OSType}}/{{.Architecture}}")
        check(daemon in setOf(platform, "linux/aarch64") && System.getProperty("os.arch") in setOf("arm64", "aarch64")) {
            "Native linux/arm64 Docker and an ARM64 JVM are required. Docker reports $daemon"
        }
        for ((role, image) in mapOf("builder" to builder, "run image" to runImage, "buildpack" to buildpack)) {
            logger.lifecycle("Checking the native Paketo $role")
            boundedCommand(work, "$role pull", 90, "docker", "pull", "--platform", platform, image.nativeRef)
            val actual = docker("$role identity", "image", "inspect", "--format", "{{.Os}}/{{.Architecture}} {{.Id}}", image.nativeRef)
            check(actual == "$platform ${image.armConfig}") { "Unexpected $role identity: $actual" }
        }
        val builderMetadata = imageMetadata(builder.nativeRef, "io.buildpacks.builder.metadata")
        val lifecycle = (builderMetadata["lifecycle"] as Map<*, *>)["version"].toString()
        check(lifecycle.isNotBlank() && lifecycle != "null") { "Builder lifecycle version is missing" }
        val stack = (builderMetadata["stack"] as Map<*, *>)["runImage"] as Map<*, *>
        check(stack["image"] == "${runImage.index.substringBefore('@')}:latest") { "Unexpected builder run image: $stack" }
        val webPack = imageMetadata(buildpack.nativeRef, "io.buildpacks.buildpackage.metadata")
        val expectedBuildpackVersion = buildpack.index.substringBefore('@').substringAfterLast(':')
        check(webPack["id"] == "paketo-buildpacks/web-servers" && webPack["version"] == expectedBuildpackVersion) {
            "Unexpected Web Servers buildpack identity: $webPack"
        }
        return mapOf(
            "pack" to actualPack,
            "lifecycle" to lifecycle,
            "platform" to platform,
            "daemon" to daemon,
            "dockerVersion" to docker("Docker version", "version", "--format", "{{.Server.Version}}"),
            "builder" to builder.evidence(),
            "runImage" to runImage.evidence(),
            "buildpack" to buildpack.evidence(),
        )
    }

    fun packageAndServe(build: StaticBuild, stage: File, directory: File, client: HttpClient): Map<String, Any> {
        val source = validateStage(stage, build.marker)
        val name = "axon-static-probe-${UUID.randomUUID()}"
        val tag = "$name:local"
        val volumes = listOf("$name-build", "$name-launch")
        var failure: Throwable? = null
        try {
            docker("create build network", "network", "create", "--label", "io.axon.probe.run=$name", name)
            check(volumes.none { it in docker("check build cache names", "volume", "ls", "--quiet").lines() }) {
                "Probe cache names already exist"
            }
            logger.lifecycle("Packaging and serving ${build.marker}")
            val packOutput = boundedCommand(
                work, "Pack build for ${build.marker}", 205, "pack", "build", tag, "--no-color",
                "--platform", platform, "--builder", builder.nativeRef, "--run-image", runImage.nativeRef,
                "--buildpack", buildpack.nativeRef, "--trust-builder", "--trust-extra-buildpacks",
                "--disable-system-buildpacks", "--pull-policy", "if-not-present", "--network", name,
                "--path", stage.absolutePath,
                "--cache", "type=build;format=volume;name=${volumes[0]}",
                "--cache", "type=launch;format=volume;name=${volumes[1]}",
                "--env", "BP_WEB_SERVER=nginx", "--env", "BP_WEB_SERVER_ROOT=public",
            )
            println(packOutput)
            val identity = docker("output image identity", "image", "inspect", "--format", "{{.Os}}/{{.Architecture}} {{.Id}}", tag)
            val imageId = identity.substringAfter(' ')
            check(identity.startsWith("$platform ") && imageId.matches(Regex("sha256:[0-9a-f]{64}"))) {
                "Unexpected output image identity: $identity"
            }
            val buildMetadata = imageMetadata(tag, "io.buildpacks.build.metadata")
            val buildpacks = (buildMetadata["buildpacks"] as List<*>).map { (it as Map<*, *>)["id"].toString() }
            check("paketo-buildpacks/nginx" in buildpacks && buildpacks.none { it.contains("/node-") || it.contains("/npm-") }) {
                "Unexpected buildpack detection for prebuilt static assets: $buildpacks"
            }

            val container = docker(
                "start ${build.marker}", "run", "--detach", "--name", name, "--network", name,
                "--platform", platform, "--publish", "127.0.0.1::8080", "--env", "PORT=8080", tag,
            )
            val runningImage = docker("verify running image", "container", "inspect", "--format", "{{.Image}}", container)
            check(runningImage == imageId) { "The running container used $runningImage instead of $imageId" }
            val assigned = docker("read loopback port", "port", container, "8080/tcp")
            val port = Regex("127\\.0\\.0\\.1:([0-9]+)").matchEntire(assigned)?.groupValues?.get(1)?.toInt()
                ?: error("Expected one randomly mapped loopback port, found $assigned")
            val response = try {
                awaitResponse(client, port)
            } catch (error: Exception) {
                runCatching { docker("read failed container logs", "logs", container) }.onSuccess(::println)
                throw error
            }
            check(response.statusCode() == 200 && response.body().contentEquals(source)) {
                "Unexpected HTTP result for ${build.marker}: status ${response.statusCode()}, body SHA-256 ${sha256(response.body())}"
            }
            val artifact = "frontend-image-${build.marker}.html"
            directory.resolve(artifact).writeBytes(response.body())
            return mapOf(
                "marker" to build.marker, "status" to response.statusCode(), "sourceSha256" to sha256(source),
                "bodySha256" to sha256(response.body()), "artifact" to artifact, "port" to port,
                "containerId" to container, "imageId" to runningImage, "detectedBuildpacks" to buildpacks,
            )
        } catch (error: Throwable) {
            failure = error
            throw error
        } finally {
            val interrupted = Thread.interrupted()
            try {
                cleanup(name, tag, volumes)
            } catch (error: Exception) {
                if (failure == null) throw error
                failure.addSuppressed(error)
                logger.error("Frontend image cleanup failed: ${error.message}")
            } finally {
                if (interrupted || failure is InterruptedException) Thread.currentThread().interrupt()
            }
        }
    }

    private fun imageMetadata(image: String, label: String): Map<*, *> {
        val raw = docker("read $label", "image", "inspect", "--format", "{{index .Config.Labels \"$label\"}}", image)
        return JsonSlurper().parseText(raw) as Map<*, *>
    }

    private fun docker(stage: String, vararg args: String) = boundedCommand(work, stage, 18, "docker", *args)

    private fun cleanup(network: String, tag: String, volumes: List<String>) {
        val errors = mutableListOf<Exception>()
        fun remove(stage: String, action: () -> Unit) {
            try {
                action()
            } catch (error: Exception) {
                errors.add(IllegalStateException(stage, error))
            }
        }
        remove("build network and containers") {
            val networkId = docker(
                "find owned network", "network", "ls", "--quiet", "--no-trunc", "--filter", "label=io.axon.probe.run=$network",
            )
            if (networkId.isNotBlank()) {
                val ids = docker("find owned containers", "ps", "--all", "--quiet", "--filter", "network=$networkId")
                    .lines().filter { it.isNotBlank() }
                if (ids.isNotEmpty()) docker("remove owned containers", "rm", "--force", *ids.toTypedArray())
                docker("remove owned network", "network", "rm", networkId)
            }
        }
        remove("image") {
            if (docker("find owned output image", "image", "ls", "--quiet", "--filter", "reference=$tag").isNotBlank()) {
                docker("remove owned output image", "image", "rm", tag)
            }
        }
        remove("caches") {
            val present = docker("find owned build caches", "volume", "ls", "--quiet").lines().intersect(volumes.toSet())
            if (present.isNotEmpty()) docker("remove owned build caches", "volume", "rm", *present.toTypedArray())
        }
        if (errors.isNotEmpty()) {
            val failure = IllegalStateException("Failed to remove resources for $network: ${errors.joinToString { it.message.orEmpty() }}")
            errors.forEach(failure::addSuppressed)
            throw failure
        }
    }
}

tasks.register("frontendImageProbe") {
    dependsOn(firstImageAssets, secondImageAssets)
    timeout = Duration.ofMinutes(13)
    val packOwner = repository.resolve("mise.toml")
    inputs.file(packOwner)
    val builder = PaketoImage(libs.versions.paketo.builder.ref.get(), libs.versions.paketo.builder.child.get(), libs.versions.paketo.builder.config.get())
    val runImage = PaketoImage(libs.versions.paketo.run.ref.get(), libs.versions.paketo.run.child.get(), libs.versions.paketo.run.config.get())
    val buildpack = PaketoImage(libs.versions.paketo.web.ref.get(), libs.versions.paketo.web.child.get(), libs.versions.paketo.web.config.get())
    val builds = listOf(firstImageBuild, secondImageBuild)
    inputs.files(builds.map { layout.buildDirectory.dir(it.staging) }).withPathSensitivity(PathSensitivity.RELATIVE)
    doLast {
        val packVersion = Regex("(?m)^pack = \"([0-9.]+)\"$").find(packOwner.readText())?.groupValues?.get(1)
            ?: error("mise.toml must pin Pack to an exact release")
        val directory = evidenceDirectory.get()
        directory.mkdirs()
        val native = NativePackaging(temporaryDir, builder, runImage, buildpack)
        val tools = native.prepare(packVersion)
        val responses = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).proxy(ProxySelector.of(null))
            .build().use { client ->
                builds.map { native.packageAndServe(it, layout.buildDirectory.dir(it.staging).get().asFile, directory, client) }
            }
        check(responses.map { it["bodySha256"] }.distinct().size == builds.size) { "Both HTTP bodies were identical" }
        val toolsArtifact = "frontend-image-tools.json"
        directory.resolve(toolsArtifact).writeText(JsonOutput.prettyPrint(JsonOutput.toJson(tools)) + "\n")
        val observation = mapOf(
            "stage" to "frontend-image", "architecture" to "arm64", "responses" to responses,
            "artifacts" to responses.map { it.getValue("artifact") } + toolsArtifact, "resourcesRemoved" to true,
        )
        println("PROBE_SECONDARY ${JsonOutput.toJson(observation)}")
    }
}
