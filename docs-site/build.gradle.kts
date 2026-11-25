import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.task.NodeTask
import groovy.json.JsonSlurper
import java.time.Duration

plugins {
    base
    alias(libs.plugins.gradle.node)
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

val npmInstall = tasks.named<NpmInstallTask>("npmInstall") {
    args = listOf("--ignore-scripts", "--no-audit", "--no-fund")
    inputs.files(nodeOwner, manifest, lockfile).withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("npmVersion", selectedNpm)
    timeout = Duration.ofMinutes(3)
    lateinit var lockBefore: ByteArray
    doFirst { lockBefore = lockfile.asFile.readBytes() }
    doLast {
        check(lockfile.asFile.readBytes().contentEquals(lockBefore)) { "npm ci changed package-lock.json" }
    }
}

val content = rootProject.layout.projectDirectory.dir("docs")
val reportPath = "feasibility/phase-01.md"
val canonicalReport = content.file(reportPath)
val staged = layout.buildDirectory.dir("staged")
val stageDocs = tasks.register<Sync>("stageDocs") {
    from(content) { include(reportPath, "quick-start.md", "maintainer-guide.md") }
    from(layout.projectDirectory.dir("src")) {
        include("index.11ty.js", "_includes/page.11ty.js", "feasibility/phase-01.11tydata.json", "site.css")
    }
    into(staged)
    doLast {
        val stagedReport = staged.get().file(reportPath).asFile
        check(stagedReport.readBytes().contentEquals(canonicalReport.asFile.readBytes())) {
            "Staged feasibility report differs from the canonical Markdown"
        }
    }
}

val docsBase = providers.gradleProperty("docsBase").orElse("/")
val docsAppUrl = providers.gradleProperty("docsAppUrl").orElse("")
val docsTrustedAppOrigins = providers.gradleProperty("docsTrustedAppOrigins").orElse("")
val config = layout.projectDirectory.file("eleventy.config.mjs")
val cli = layout.projectDirectory.file("node_modules/@11ty/eleventy/cmd.cjs")

fun NodeTask.useDocsDependencies() {
    dependsOn(npmInstall, stageDocs)
    inputs.files(nodeOwner, manifest, lockfile, config, staged).withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("docsBase", docsBase)
    inputs.property("docsAppUrl", docsAppUrl)
    inputs.property("docsTrustedAppOrigins", docsTrustedAppOrigins)
    environment.put("DOCS_BASE", docsBase)
    environment.put("DOCS_APP_URL", docsAppUrl)
    environment.put("DOCS_TRUSTED_APP_ORIGINS", docsTrustedAppOrigins)
    environment.put("DOCS_INPUT", staged.map { it.asFile.absolutePath })
}

fun NodeTask.renderDocs(destination: Provider<Directory>, vararg flags: String) {
    useDocsDependencies()
    script = cli
    args = destination.map { listOf("--output=${it.asFile}") + flags }
}

val distribution = layout.buildDirectory.dir("site")
val docsBuild = tasks.register<NodeTask>("docsBuild") {
    group = "build"
    description = "Render the allowlisted public documentation."
    renderDocs(distribution)
    outputs.dir(distribution)
    timeout = Duration.ofMinutes(2)
    doFirst {
        check(distribution.get().asFile.deleteRecursively()) { "Could not clear the previous docs build" }
    }
}

tasks.assemble { dependsOn(docsBuild) }

tasks.register<NodeTask>("serve") {
    group = "documentation"
    description = "Preview the staged documentation at http://127.0.0.1:8081/."
    renderDocs(layout.buildDirectory.dir("preview"), "--serve", "--port=8081")
}
