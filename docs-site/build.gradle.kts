import com.github.gradle.node.npm.task.NpmInstallTask
import com.github.gradle.node.task.NodeTask
import groovy.json.JsonSlurper
import java.nio.file.Files
import java.nio.file.LinkOption.NOFOLLOW_LINKS
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

val npmInstall =
    tasks.named<NpmInstallTask>("npmInstall") {
        args = listOf("--ignore-scripts", "--no-audit", "--no-fund")
        inputs.files(nodeOwner, manifest, lockfile).withPathSensitivity(PathSensitivity.RELATIVE)
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

val repository = rootProject.layout.projectDirectory
val content = repository.dir("docs")
val templates = layout.projectDirectory.dir("src")
val reportPath = "feasibility/phase-01.md"
val canonicalReport = content.file(reportPath)
val publicArticles = listOf(reportPath, "quick-start.md", "maintainer-guide.md")
val publicTemplates =
    listOf(
        "index.11ty.js",
        "_includes/page.11ty.js",
        "feasibility/phase-01.11tydata.json",
        "site.css",
    )
val publicFonts =
    listOf("geist", "geist-mono").flatMap { font ->
        val fontPackage = layout.projectDirectory.dir("node_modules/@fontsource-variable/$font")
        val asset = "$font-latin-wght-normal.woff2"
        listOf(
            asset to fontPackage.file("files/$asset"),
            "$font-LICENSE.txt" to fontPackage.file("LICENSE"),
        )
    }
val staged = layout.buildDirectory.dir("staged")
val stageDocs =
    tasks.register<Sync>("stageDocs") {
        dependsOn(npmInstall)
        from(content) { include(publicArticles) }
        from(templates) { include(publicTemplates) }
        for ((name, source) in publicFonts) {
            from(source) {
                into("fonts")
                rename { name }
            }
        }
        into(staged)
        doFirst {
            val allowedSources =
                publicArticles.map(content::file) +
                    publicTemplates.map(templates::file) +
                    publicFonts.map { it.second }
            val repositoryPath = repository.asFile.toPath()
            val canonicalRepository = repository.asFile.canonicalFile.toPath()
            for (source in allowedSources) {
                val relativePath = repositoryPath.relativize(source.asFile.toPath())
                val expected = canonicalRepository.resolve(relativePath)
                check(
                    Files.isRegularFile(expected, NOFOLLOW_LINKS) &&
                        expected.toRealPath() == expected,
                ) {
                    "Expected a regular public source at $relativePath"
                }
            }
        }
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
val verifier = layout.projectDirectory.file("verify-site.mjs")
val cli = layout.projectDirectory.file("node_modules/@11ty/eleventy/cmd.cjs")

fun NodeTask.useDocsDependencies() {
    dependsOn(npmInstall, stageDocs)
    inputs
        .files(nodeOwner, manifest, lockfile, config, verifier, staged)
        .withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("docsBase", docsBase)
    inputs.property("docsAppUrl", docsAppUrl)
    inputs.property("docsTrustedAppOrigins", docsTrustedAppOrigins)
    environment.put("DOCS_BASE", docsBase)
    environment.put("DOCS_APP_URL", docsAppUrl)
    environment.put("DOCS_TRUSTED_APP_ORIGINS", docsTrustedAppOrigins)
    environment.put("DOCS_INPUT", staged.map { it.asFile.absolutePath })
}

fun clearOutput(directory: Directory) {
    val path = directory.asFile.toPath()
    if (Files.exists(path, NOFOLLOW_LINKS)) {
        Files.walk(path).use { entries ->
            entries.sorted(Comparator.reverseOrder()).forEach(Files::delete)
        }
    }
}

val distribution = layout.buildDirectory.dir("site")
val docsBuild =
    tasks.register<NodeTask>("docsBuild") {
        group = "build"
        description = "Render the allowlisted public documentation."
        useDocsDependencies()
        script = cli
        args = distribution.map { listOf("--output=${it.asFile}") }
        outputs.dir(distribution)
        timeout = Duration.ofMinutes(2)
        doFirst { clearOutput(distribution.get()) }
    }

tasks.assemble { dependsOn(docsBuild) }

val docsCheck =
    tasks.register<NodeTask>("docsCheck") {
        group = "verification"
        description = "Check the public file list, navigation, and both docs launch modes."
        dependsOn(docsBuild)
        useDocsDependencies()
        options = listOf("--test", "--test-reporter=tap")
        script = layout.projectDirectory.file("test/site.test.mjs")
        inputs.files(canonicalReport, distribution).withPathSensitivity(PathSensitivity.RELATIVE)
        environment.put("DOCS_OUTPUT", distribution.map { it.asFile.absolutePath })
        environment.put("DOCS_CANONICAL_REPORT", canonicalReport.asFile.absolutePath)
        timeout = Duration.ofMinutes(2)
    }

tasks.check { dependsOn(docsCheck) }

tasks.register<NodeTask>("serve") {
    group = "documentation"
    description = "Preview the built documentation at http://127.0.0.1:8081/."
    dependsOn(docsBuild)
    script = layout.projectDirectory.file("serve.mjs")
    args = distribution.zip(docsBase) { output, base -> listOf(output.asFile.absolutePath, base) }
}
