package probe

import com.github.dockerjava.api.model.ExposedPort
import com.github.dockerjava.api.model.Ports
import io.axoniq.framework.axonserver.connector.api.AxonServerConnectionManager
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.file.Files
import java.nio.file.Path
import java.security.MessageDigest
import java.time.Duration
import java.time.Instant
import java.util.HexFormat
import java.util.UUID
import java.util.concurrent.ExecutionException
import java.util.concurrent.TimeUnit.SECONDS
import org.axonframework.common.configuration.Configuration as AxonConfiguration
import org.axonframework.eventsourcing.eventstore.SourcingCondition
import org.axonframework.eventsourcing.eventstore.TerminalEventMessage
import org.axonframework.messaging.commandhandling.GenericCommandMessage
import org.axonframework.messaging.commandhandling.gateway.CommandGateway
import org.axonframework.messaging.core.GenericMessage
import org.axonframework.messaging.core.MessageStream
import org.axonframework.messaging.core.MessageType
import org.axonframework.messaging.eventhandling.EventMessage
import org.axonframework.messaging.eventstreaming.EventCriteria
import org.axonframework.messaging.eventstreaming.Tag
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInfo
import org.testcontainers.DockerClientFactory
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.wait.strategy.Wait
import org.testcontainers.containers.wait.strategy.WaitAllStrategy
import org.testcontainers.utility.DockerImageName
import tools.jackson.databind.JsonNode
import tools.jackson.databind.json.JsonMapper

class AxonProbeTest {
    @Test
    fun `a remote command persists a tagged event`(testInfo: TestInfo) {
        val started = Instant.now()
        val runId = System.getProperty("probe.runId").ifBlank { newId() }
        require(runId.matches(Regex("[A-Za-z0-9_-]{1,80}"))) { "Invalid probe run ID" }
        val evidence = Path.of(System.getProperty("probe.evidenceDirectory"))
        Files.createDirectories(evidence)
        val attempt = Files.createTempDirectory(evidence, "remote-tagged-write-")
        val image = ServerImage.verify(System.getProperty("probe.serverImage"))
        val command = EnrollStudent(runId, newId(), newId())
        val course = EventCriteria.havingTags(Tag.of("courseId", command.courseId))
        val student = EventCriteria.havingTags(Tag.of("studentId", command.studentId))
        val commandId = newId()

        val docker = DockerClientFactory.instance().client()
        val daemon = docker.versionCmd().exec()
        assertEquals("linux", daemon.operatingSystem)
        assertArm64(checkNotNull(daemon.arch))

        val server = probeServer(image.nativeReference)
        server.use {
            try {
                server.start()
                val live = docker.inspectContainerCmd(server.containerId).exec()
                val activeImage = docker.inspectImageCmd(live.imageId).exec()
                assertEquals(image.arm64.config, activeImage.id)
                assertEquals("linux", activeImage.os)
                val imageArchitecture = checkNotNull(activeImage.arch)
                assertArm64(imageArchitecture)
                assertTrue(server.logs.contains("No license detected. Running in unregistered mode."))
                assertTrue(live.hostConfig.binds.orEmpty().isEmpty())
                for (port in SERVER_PORTS) {
                    val binding = live.networkSettings.ports.bindings.getValue(ExposedPort.tcp(port)).single()
                    assertEquals("127.0.0.1", binding.hostIp)
                }
                writeJson(evidence.resolve("images.json"), mapOf(
                    "runId" to runId, "checkedAt" to image.checkedAt, "index" to image.reference,
                    "arm64" to image.arm64, "amd64" to image.amd64,
                    "daemon" to "${daemon.operatingSystem}/${daemon.arch}", "runningImageId" to checkNotNull(activeImage.id),
                    "runningArchitecture" to imageArchitecture,
                ))
                val endpoint = "127.0.0.1:${server.getMappedPort(GRPC_PORT)}"
                val driverClient = "probe-driver-$runId"
                val commandClient = "probe-command-$runId"
                val driverConfig = Files.createFile(Path.of("application.properties")).toAbsolutePath()
                startProbeRole(endpoint, driverClient, runId, driverConfig, command = false).use { driver ->
                    assertTrue(driver.getBeansOfType(EnrollmentHandler::class.java).isEmpty())
                    val axon = driver.getBean(AxonConfiguration::class.java)
                    requireServerContext(axon)
                    val driverRole = roleIdentity(axon)
                    assertRole(driverClient, driverRole)

                    val engine = storageEngine(axon)
                    val initial = readHistory(engine.source(SourcingCondition.conditionFor(EventCriteria.havingAnyTag()), null))
                    assertTrue(initial.isEmpty(), "Fresh fixture history must be empty")

                    val process = startCommandRole(endpoint, commandClient, runId, attempt)
                    try {
                        val gateway = axon.getComponent(CommandGateway::class.java)
                        val writerRole = awaitRegistration(gateway, runId, process)
                        assertRole(commandClient, writerRole)
                        assertEquals(process.pid(), writerRole.pid)
                        assertNotEquals(driverRole.pid, writerRole.pid)

                        val receipt = send(gateway, WRITE_COMMAND, command, WriteReceipt::class.java, commandId)
                        assertEquals(writerRole, receipt.role)
                        assertEquals(runId, receipt.runId)
                        assertEquals(commandId, receipt.commandId)
                        assertEquals(5, setOf(runId, command.courseId, command.studentId, commandId, receipt.eventId).size)

                        val connection = axon.getComponent(AxonServerConnectionManager::class.java).connection
                        val registrations = connection.adminChannel().getAllConnectedApplications(AXON_CONTEXT)
                            .get(MESSAGE_TIMEOUT_SECONDS, SECONDS).applicationsList.associateBy { it.name }
                        val driverRegistration = registrations.getValue(driverClient)
                        val writerRegistration = registrations.getValue(commandClient)
                        assertTrue(driverRegistration.commandsList.isEmpty())
                        assertTrue(WRITE_COMMAND in writerRegistration.commandsList)

                        val courseHistory = readHistory(engine.source(SourcingCondition.conditionFor(course), null))
                        val studentHistory = readHistory(engine.source(SourcingCondition.conditionFor(student), null))
                        assertEquals(1, courseHistory.size, "The remote command must persist one course-tagged event")
                        assertEquals(1, studentHistory.size, "The remote command must persist one student-tagged event")
                        val expected = StudentEnrolled(runId, command.courseId, command.studentId, commandId)
                        for (stored in listOf(courseHistory.single(), studentHistory.single())) {
                            assertEquals(receipt.eventId, stored.identifier())
                            assertEquals(ENROLLED_EVENT, stored.type().qualifiedName().fullName())
                            assertEquals(expected, stored.payloadAs(StudentEnrolled::class.java))
                        }

                        val transcript = mapOf(
                            "test" to "${javaClass.name}.${testInfo.testMethod.orElseThrow().name}", "runId" to runId,
                            "startedAt" to started.toString(), "finishedAt" to Instant.now().toString(),
                            "context" to AXON_CONTEXT, "dcb" to true, "initialEvents" to initial.size,
                            "worker" to driverRole, "command" to writerRole, "receipt" to receipt,
                            "driverRegisteredClient" to driverRegistration.clientsList.single().name,
                            "commandRegisteredClient" to writerRegistration.clientsList.single().name,
                            "courseId" to command.courseId, "studentId" to command.studentId,
                            "courseEventId" to courseHistory.single().identifier(),
                            "studentEventId" to studentHistory.single().identifier(),
                        )
                        writeJson(evidence.resolve("core.json"), transcript)
                        println(JSON.writeValueAsString(transcript))
                    } finally {
                        process.destroy()
                        if (!process.waitFor(10, SECONDS)) process.destroyForcibly()
                        check(process.waitFor(5, SECONDS)) { "Command process ${process.pid()} did not exit" }
                    }
                }
            } finally {
                if (server.containerId != null) Files.writeString(attempt.resolve("server.log"), server.logs)
            }
        }
    }
}

private val JSON = JsonMapper.builder().build()
private const val GRPC_PORT = 8124
private const val HTTP_PORT = 8024
private val SERVER_PORTS = listOf(HTTP_PORT, GRPC_PORT)

private class ProbeServer(image: DockerImageName) : GenericContainer<ProbeServer>(image)

private fun probeServer(image: String): ProbeServer = ProbeServer(DockerImageName.parse(image)).apply {
    withReuse(false)
    withEnv("AXONIQ_AXONSERVER_STANDALONE_DCB", "true")
    withExposedPorts(*SERVER_PORTS.toTypedArray())
    withCreateContainerCmdModifier { create ->
        val ports = Ports()
        for (port in SERVER_PORTS) ports.bind(ExposedPort.tcp(port), Ports.Binding.bindIp("127.0.0.1"))
        checkNotNull(create.hostConfig).withPortBindings(ports)
        create.withPlatform("linux/arm64")
    }
    waitingFor(WaitAllStrategy()
        .withStrategy(Wait.forHttp("/v1/public/me").forPort(HTTP_PORT))
        .withStrategy(Wait.forLogMessage(".*default: context default created, my role PRIMARY.*\\n", 1))
        .withStartupTimeout(Duration.ofSeconds(90)))
}

private fun startCommandRole(endpoint: String, client: String, runId: String, directory: Path): Process {
    val home = Files.createDirectory(directory.resolve("command-home"))
    val work = Files.createDirectory(directory.resolve("command-work"))
    val builder = ProcessBuilder(
        System.getProperty("probe.roleJava"), "-Duser.home=$home", "-cp", System.getProperty("probe.roleClasspath"),
        "probe.ProbeApplicationKt", endpoint, client, runId,
    ).directory(work.toFile()).redirectErrorStream(true).redirectOutput(directory.resolve("command.log").toFile())
    builder.environment().keys.retainAll(setOf("LANG", "LC_ALL", "TMPDIR", "SystemRoot"))
    builder.environment()["HOME"] = home.toString()
    return builder.start()
}

private fun awaitRegistration(gateway: CommandGateway, runId: String, process: Process): RoleIdentity {
    val end = System.nanoTime() + Duration.ofSeconds(45).toNanos()
    var lastFailure: ExecutionException? = null
    while (System.nanoTime() < end && process.isAlive) {
        try {
            return send(gateway, READY_COMMAND, runId, RoleIdentity::class.java)
        } catch (failure: ExecutionException) {
            lastFailure = failure
            Thread.sleep(200)
        }
    }
    throw IllegalStateException("Command role failed to register; inspect local command.log", lastFailure)
}

private fun <T : Any> send(gateway: CommandGateway, name: String, payload: Any, result: Class<T>, id: String = newId()): T {
    val message = GenericCommandMessage(GenericMessage(id, MessageType(name), payload, emptyMap()))
    return gateway.send(message, result).get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
}

private fun readHistory(stream: MessageStream<EventMessage>): List<EventMessage> = try {
    stream.filter { it.message() !is TerminalEventMessage }
        .collect({ mutableListOf<EventMessage>() }, MutableList<EventMessage>::add)
        .get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
} finally {
    stream.close()
}

private fun assertRole(client: String, identity: RoleIdentity) {
    assertEquals(client, identity.clientId)
    assertArm64(identity.architecture)
    assertEquals("Eclipse Adoptium", identity.javaVendor)
    assertTrue(identity.javaVersion.startsWith("25."))
}

private fun assertArm64(architecture: String) {
    assertTrue(architecture in setOf("arm64", "aarch64"), "Expected native ARM64, found $architecture")
}

private fun newId(): String = UUID.randomUUID().toString()

private fun writeJson(path: Path, fields: Map<String, Any>) {
    JSON.writerWithDefaultPrettyPrinter().writeValue(path.toFile(), fields)
}

@JvmRecord
private data class ImageChild(val digest: String, val config: String, val architecture: String)

private data class ServerImage(val reference: String, val checkedAt: String, val arm64: ImageChild, val amd64: ImageChild) {
    val nativeReference: String get() = "axoniq/axonserver@${arm64.digest}"

    companion object {
        fun verify(reference: String): ServerImage {
            val match = requireNotNull(Regex("axoniq/axonserver:[0-9.]+@(sha256:[a-f0-9]{64})").matchEntire(reference))
            val (indexDigest) = match.destructured
            HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).followRedirects(HttpClient.Redirect.NORMAL)
                .build().use { http ->
                    val request = HttpRequest.newBuilder(URI.create(
                        "https://auth.docker.io/token?service=registry.docker.io&scope=repository:axoniq/axonserver:pull"
                    )).timeout(Duration.ofSeconds(20)).build()
                    val token = JSON.readTree(fetch(http, request)).required("token").asString()

                    fun registry(path: String, digest: String, accept: String): JsonNode {
                        require(digest.matches(Regex("sha256:[a-f0-9]{64}")))
                        val registryRequest = HttpRequest.newBuilder(URI.create(
                            "https://registry-1.docker.io/v2/axoniq/axonserver/$path"
                        )).timeout(Duration.ofSeconds(20)).header("Authorization", "Bearer $token")
                            .header("Accept", accept).build()
                        val bytes = fetch(http, registryRequest)
                        val sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes))
                        check(digest == "sha256:$sha") { "OCI digest mismatch for $path" }
                        return JSON.readTree(bytes)
                    }

                    val index = registry("manifests/$indexDigest", indexDigest, "application/vnd.oci.image.index.v1+json")
                    fun child(arch: String): ImageChild {
                        val descriptor = index.required("manifests").single {
                            it.path("platform").path("os").asString() == "linux" &&
                                it.path("platform").path("architecture").asString() == arch &&
                                it.path("annotations").path("vnd.docker.reference.type").asString() != "attestation-manifest"
                        }
                        val digest = descriptor.required("digest").asString()
                        val manifest = registry("manifests/$digest", digest, "application/vnd.oci.image.manifest.v1+json")
                        val config = manifest.required("config").required("digest").asString()
                        val configJson = registry("blobs/$config", config, "application/vnd.oci.image.config.v1+json")
                        check(configJson.required("os").asString() == "linux" && configJson.required("architecture").asString() == arch)
                        check(configJson.required("rootfs").required("diff_ids").size() > 0)
                        return ImageChild(digest, config, arch)
                    }
                    val arm64 = child("arm64")
                    val amd64 = child("amd64")
                    check(arm64.digest != amd64.digest && arm64.config != amd64.config)
                    return ServerImage(reference, Instant.now().toString(), arm64, amd64)
                }
        }

        private fun fetch(http: HttpClient, request: HttpRequest): ByteArray {
            val response = http.send(request, HttpResponse.BodyHandlers.ofByteArray())
            check(response.statusCode() == 200) { "OCI request to ${request.uri().host} failed: HTTP ${response.statusCode()}" }
            return response.body()
        }
    }
}
