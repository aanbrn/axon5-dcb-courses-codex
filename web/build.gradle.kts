import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.task.NodeTask
import groovy.json.JsonSlurper
import java.time.Duration

plugins {
    `java-base`
    alias(libs.plugins.gradle.node)
}

val javaFeature =
    providers.fileContents(rootProject.layout.projectDirectory.file(".java-version")).asText.map {
        it.trim().toInt()
    }
val javaLauncher = javaToolchains.launcherFor {
    languageVersion = javaFeature.map(JavaLanguageVersion::of)
    vendor = JvmVendorSpec.ADOPTIUM
}

val nodeOwner = rootProject.layout.projectDirectory.file(".nvmrc")
val manifest = layout.projectDirectory.file("package.json")
val lockfile = layout.projectDirectory.file("package-lock.json")
val selectedNode = providers.fileContents(nodeOwner).asText.get().trim()
val packageManager = (JsonSlurper().parse(manifest.asFile) as Map<*, *>)["packageManager"] as String
val selectedNpm = packageManager.removePrefix("npm@")
val exactVersion = Regex("[0-9]+\\.[0-9]+\\.[0-9]+")

require(exactVersion.matches(selectedNode)) { ".nvmrc must pin an exact Node release" }

require(packageManager == "npm@$selectedNpm" && exactVersion.matches(selectedNpm)) {
    "packageManager must pin an exact npm release"
}

node {
    version = selectedNode
    npmVersion = selectedNpm
    download = true
    npmInstallCommand = "ci"
}

val npmInstall =
    tasks.named<NpmInstallTask>("npmInstall") {
        args = listOf("--ignore-scripts", "--no-audit", "--no-fund")
        inputs.file(nodeOwner).withPathSensitivity(PathSensitivity.RELATIVE)
        inputs.property("npmVersion", selectedNpm)
        timeout = Duration.ofMinutes(3)
        lateinit var lockBefore: ByteArray
        doFirst { lockBefore = lockfile.asFile.readBytes() }
        doLast {
            check(lockfile.asFile.readBytes().contentEquals(lockBefore)) {
                "npm ci changed package-lock.json"
            }
        }
    }

val openApiDependencies = configurations.dependencyScope("openApiDependencies").get()
val openApiContract =
    configurations.resolvable("openApiContract") {
        extendsFrom(openApiDependencies)
    }
val roleTracerDependencies = configurations.dependencyScope("roleTracerDependencies").get()
val roleTracerJar =
    configurations.resolvable("roleTracerJar") {
        extendsFrom(roleTracerDependencies)
    }

dependencies {
    add(openApiDependencies.name, project(path = ":bff", configuration = "openApiElements"))
    add(
        roleTracerDependencies.name,
        project(path = ":bff", configuration = "bootExecutableElements"),
    )
}

val generated = layout.buildDirectory.dir("generated")
val distribution = layout.buildDirectory.dir("dist")
val storybookDistribution = layout.buildDirectory.dir("storybook")
val source = layout.projectDirectory.dir("src")
val vite = layout.projectDirectory.file("node_modules/vite/bin/vite.js")

fun NodeTask.useWebDependencies(vararg sources: Any) {
    dependsOn(npmInstall)
    inputs
        .files(nodeOwner, manifest, lockfile, *sources)
        .withPathSensitivity(PathSensitivity.RELATIVE)
    timeout = Duration.ofMinutes(2)
}

val generateClient =
    tasks.register<NodeTask>("generateClient") {
        useWebDependencies(openApiContract, "orval.config.ts")
        script = layout.projectDirectory.file("node_modules/orval/dist/bin/orval.mjs")
        args = listOf("--config", "orval.config.ts")
        environment.put(
            "BFF_OPENAPI_FILE",
            openApiContract.get().elements.map { it.single().asFile.absolutePath },
        )
        outputs.dir(generated)
    }

val typecheck =
    tasks.register<NodeTask>("typecheck") {
        dependsOn(generateClient)
        useWebDependencies(source, generated, "tsconfig.json")
        script = layout.projectDirectory.file("node_modules/typescript/bin/tsc")
        args = listOf("--project", "tsconfig.json")
    }

val webBuild =
    tasks.register<NodeTask>("webBuild") {
        dependsOn(typecheck)
        useWebDependencies(source, generated, "index.html", "vite.config.ts", "tsconfig.json")
        inputs
            .files(
                fileTree(projectDir) {
                    include(".env", ".env.local", ".env.production", ".env.production.local")
                },
            )
            .withPathSensitivity(PathSensitivity.RELATIVE)
        inputs.property("docsBase", providers.environmentVariable("VITE_DOCS_BASE").orElse(""))
        script = vite
        args = listOf("build")
        outputs.dir(distribution)
    }

val webCheck =
    tasks.register<NodeTask>("webCheck") {
        group = "verification"
        description = "Typecheck the browser application and test its generated HTTP client."
        dependsOn(typecheck)
        useWebDependencies(source, generated, "test/generated-client.test.ts", "tsconfig.json")
        options = listOf("--test", "--test-reporter=tap")
        script = layout.projectDirectory.file("test/generated-client.test.ts")
    }

tasks.register<Exec>("verifyClientGraph") {
    group = "verification"
    description = "Verify generated client invalidation and recovery in a disposable source copy."
    workingDir = rootProject.layout.projectDirectory.asFile
    commandLine("python3", "web/test/client-graph.py", "--invalidation")
    timeout = Duration.ofMinutes(10)
}

val buildStorybook =
    tasks.register<NodeTask>("buildStorybook") {
        group = "build"
        description = "Build the static Storybook from the production components."
        dependsOn(typecheck)
        useWebDependencies(source, generated, ".storybook", "vite.config.ts", "tsconfig.json")
        script = layout.projectDirectory.file("node_modules/storybook/dist/bin/dispatcher.js")
        args = listOf("build", "--output-dir", "build/storybook", "--disable-telemetry")
        outputs.dir(storybookDistribution)
    }

tasks.named("assemble") { dependsOn(webBuild, buildStorybook) }

tasks.named("check") { dependsOn(webCheck) }

tasks.register<NodeTask>("dev") {
    dependsOn(generateClient)
    script = vite
}

val provisionBrowser =
    tasks.register<NodeTask>("provisionBrowser") {
        useWebDependencies()
        script = layout.projectDirectory.file("node_modules/playwright/cli.js")
        args = listOf("install", "chromium")
        timeout = Duration.ofMinutes(5)
    }

tasks.register<NodeTask>("storyTest") {
    group = "verification"
    description = "Run the Storybook interactions and accessibility checks in Chromium."
    dependsOn(provisionBrowser, generateClient)
    useWebDependencies(source, generated, ".storybook", "vitest.config.ts", "tsconfig.json")
    script = layout.projectDirectory.file("node_modules/vitest/vitest.mjs")
    args = listOf("run", "--project", "storybook")
}

val shellSmoke =
    tasks.register<NodeTask>("shellSmoke") {
        group = "verification"
        description = "Verify the built browser shell and live role directory in Chromium."
        dependsOn(provisionBrowser, webBuild)
        useWebDependencies(
            roleTracerJar,
            distribution,
            source,
            generated,
            "test/role-tracer.mjs",
            "test/role-states.test.tsx",
            "tsconfig.json",
            "vite.config.ts",
        )
        options = listOf("--test", "--test-reporter=tap")
        script = layout.projectDirectory.file("test/role-tracer.mjs")
        environment.put(
            "ROLE_TRACER_JAVA",
            javaLauncher.map { it.executablePath.asFile.absolutePath },
        )
        environment.put(
            "ROLE_TRACER_BFF_JAR",
            roleTracerJar.get().elements.map { it.single().asFile.absolutePath },
        )
        environment.put("ROLE_TRACER_WEB_DIST", distribution.map { it.asFile.absolutePath })
    }

tasks.register("roleTracer") {
    group = "verification"
    description = "Run the live role directory browser smoke test."
    dependsOn(shellSmoke)
}
