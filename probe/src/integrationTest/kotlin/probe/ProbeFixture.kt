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
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit.SECONDS
import org.axonframework.common.configuration.Configuration as AxonConfiguration
import org.axonframework.eventsourcing.eventstore.SourcingCondition
import org.axonframework.eventsourcing.eventstore.TerminalEventMessage
import org.axonframework.messaging.commandhandling.GenericCommandMessage
import org.axonframework.messaging.commandhandling.gateway.CommandGateway
import org.axonframework.messaging.core.GenericMessage
import org.axonframework.messaging.core.MessageType
import org.axonframework.messaging.eventhandling.EventMessage
import org.axonframework.messaging.eventstreaming.EventCriteria
import org.axonframework.messaging.queryhandling.GenericQueryMessage
import org.axonframework.messaging.queryhandling.gateway.QueryGateway
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.reactivestreams.Subscriber
import org.reactivestreams.Subscription
import org.springframework.context.ConfigurableApplicationContext
import org.testcontainers.DockerClientFactory
import org.testcontainers.containers.GenericContainer
import org.testcontainers.containers.wait.strategy.Wait
import org.testcontainers.containers.wait.strategy.WaitAllStrategy
import org.testcontainers.utility.DockerImageName
import tools.jackson.databind.JsonNode
import tools.jackson.databind.json.JsonMapper

internal val JSON = JsonMapper.builder().build()
private const val GRPC_PORT = 8124
private const val HTTP_PORT = 8024
private val SERVER_PORTS = listOf(HTTP_PORT, GRPC_PORT)

internal class ProbeFixture(val runId: String) : AutoCloseable {
    val evidence: Path = Path.of(System.getProperty("probe.evidenceDirectory"))
    private val attempt: Path = Files.createTempDirectory(Files.createDirectories(evidence), "$runId-")
    private val docker = DockerClientFactory.instance().client()
    private val server = probeServer(serverImage.nativeReference, runId)
    private val processes = mutableMapOf<ProbeRole, Process>()
    private var driver: ConfigurableApplicationContext? = null

    val axon: AxonConfiguration get() = checkNotNull(driver).getBean(AxonConfiguration::class.java)
    val connection get() = axon.getComponent(AxonServerConnectionManager::class.java).connection
    val engine get() = storageEngine(axon)
    val queries: QueryGateway get() = axon.getComponent(QueryGateway::class.java)
    val driverRole get() = roleIdentity(axon)
    private val endpoint get() = "127.0.0.1:${server.getMappedPort(GRPC_PORT)}"

    fun start(): ProbeFixture {
        val daemon = docker.versionCmd().exec()
        assertEquals("linux", daemon.operatingSystem)
        assertArm64(checkNotNull(daemon.arch))
        server.start()
        val live = docker.inspectContainerCmd(server.containerId).exec()
        val activeImage = docker.inspectImageCmd(live.imageId).exec()
        assertEquals(serverImage.arm64.config, activeImage.id)
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
            "runId" to runId, "checkedAt" to serverImage.checkedAt, "index" to serverImage.reference,
            "arm64" to serverImage.arm64, "amd64" to serverImage.amd64,
            "daemon" to "${daemon.operatingSystem}/${daemon.arch}", "daemonVersion" to checkNotNull(daemon.version),
            "runningImageId" to checkNotNull(activeImage.id), "runningArchitecture" to imageArchitecture,
        ))
        val config = Files.createFile(attempt.resolve("application.properties"))
        driver = startProbeRole(endpoint, clientName(ProbeRole.DRIVER), runId, config, ProbeRole.DRIVER)
        assertTrue(checkNotNull(driver).getBeansOfType(EnrollmentHandler::class.java).isEmpty())
        assertTrue(checkNotNull(driver).getBeansOfType(CourseProjection::class.java).isEmpty())
        requireServerContext(axon)
        assertRole(clientName(ProbeRole.DRIVER), driverRole)
        return this
    }

    fun startCommand(): RoleIdentity {
        val process = startChild(ProbeRole.COMMAND)
        val identity = awaitRole("command handler registration", process) {
            send(READY_COMMAND, runId, RoleIdentity::class.java)
        }
        assertChild(ProbeRole.COMMAND, process, identity)
        return identity
    }

    fun startProjection(query: ReadCourse): CourseState {
        val process = startChild(ProbeRole.PROJECTION)
        val state = awaitRole("projection handler registration and event processor", process) {
            readCourse(query).takeIf { it.processorReady }
        }
        assertChild(ProbeRole.PROJECTION, process, state.role)
        return state
    }

    private fun assertChild(role: ProbeRole, process: Process, identity: RoleIdentity) {
        assertRole(clientName(role), identity)
        assertEquals(process.pid(), identity.pid)
        assertEquals(driverRole.javaVersion, identity.javaVersion)
        assertEquals(driverRole.architecture, identity.architecture)
    }

    fun queryMessage(query: ReadCourse) = GenericQueryMessage(MessageType(READ_COURSE), query)

    fun readCourse(query: ReadCourse): CourseState =
        queries.query(queryMessage(query), CourseState::class.java).get(MESSAGE_TIMEOUT_SECONDS, SECONDS)

    fun subscribe(query: ReadCourse): CourseSubscription = CourseSubscription().also {
        queries.subscriptionQuery(queryMessage(query), CourseState::class.java, 8).subscribe(it)
    }

    fun registrations() = connection.adminChannel().getAllConnectedApplications(AXON_CONTEXT)
        .get(MESSAGE_TIMEOUT_SECONDS, SECONDS).applicationsList.associateBy { it.name }

    fun readHistory(criteria: EventCriteria): List<EventMessage> {
        val stream = engine.source(SourcingCondition.conditionFor(criteria), null)
        try {
            return stream.filter { it.message() !is TerminalEventMessage }
                .collect({ mutableListOf<EventMessage>() }, MutableList<EventMessage>::add)
                .get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
        } finally {
            stream.close()
        }
    }

    fun <T : Any> send(name: String, payload: Any, result: Class<T>, id: String = newId()): T {
        val message = GenericCommandMessage(GenericMessage(id, MessageType(name), payload, emptyMap()))
        return axon.getComponent(CommandGateway::class.java).send(message, result).get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
    }

    fun clientName(role: ProbeRole): String = "probe-${role.name.lowercase()}-$runId"

    private fun startChild(role: ProbeRole): Process {
        check(role !in processes)
        val name = role.name.lowercase()
        val home = Files.createDirectory(attempt.resolve("$name-home"))
        val work = Files.createDirectory(attempt.resolve("$name-work"))
        val builder = ProcessBuilder(
            System.getProperty("probe.roleJava"), "-Duser.home=$home", "-cp", System.getProperty("probe.roleClasspath"),
            "probe.ProbeApplicationKt", endpoint, clientName(role), runId, role.name,
        ).directory(work.toFile()).redirectErrorStream(true).redirectOutput(attempt.resolve("$name.log").toFile())
        builder.environment().keys.retainAll(setOf("LANG", "LC_ALL", "TMPDIR", "SystemRoot"))
        builder.environment()["HOME"] = home.toString()
        return builder.start().also { processes[role] = it }
    }

    override fun close() {
        server.use {
            try {
                driver?.use {
                    var failure: Throwable? = null
                    processes.values.forEach { process ->
                        try {
                            process.destroy()
                            if (!process.waitFor(10, SECONDS)) process.destroyForcibly()
                            check(process.waitFor(5, SECONDS)) { "Process ${process.pid()} did not exit" }
                        } catch (error: Exception) {
                            failure?.addSuppressed(error) ?: run { failure = error }
                        }
                    }
                    failure?.let { throw it }
                }
            } finally {
                if (server.containerId != null) Files.writeString(attempt.resolve("server.log"), server.logs)
            }
        }
    }

    companion object {
        private val serverImage by lazy { ServerImage.verify(System.getProperty("probe.serverImage")) }
    }
}

internal class CourseSubscription : Subscriber<CourseState>, AutoCloseable {
    private val results = LinkedBlockingQueue<Result<CourseState>>()
    private var subscription: Subscription? = null
    private var closed = false

    @Synchronized
    override fun onSubscribe(subscription: Subscription) {
        if (closed || this.subscription != null) {
            subscription.cancel()
        } else {
            this.subscription = subscription
            subscription.request(3)
        }
    }

    override fun onNext(state: CourseState) { results.add(Result.success(state)) }

    override fun onError(error: Throwable) { results.add(Result.failure(error)) }

    override fun onComplete() { onError(IllegalStateException("Subscription completed before the expected result")) }

    fun next(stage: String): CourseState =
        checkNotNull(results.poll(MESSAGE_TIMEOUT_SECONDS, SECONDS)) { "Timed out at $stage" }.getOrThrow()

    @Synchronized
    override fun close() {
        closed = true
        subscription?.cancel()
    }
}

private class ProbeServer(image: DockerImageName) : GenericContainer<ProbeServer>(image)

private fun probeServer(image: String, runId: String): ProbeServer = ProbeServer(DockerImageName.parse(image)).apply {
    withReuse(false)
    withLabel("probe.run", runId)
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

private fun <T : Any> awaitRole(stage: String, process: Process, request: () -> T?): T {
    val end = System.nanoTime() + Duration.ofSeconds(45).toNanos()
    var lastFailure: ExecutionException? = null
    while (System.nanoTime() < end && process.isAlive) {
        try {
            request()?.let { return it }
        } catch (failure: ExecutionException) {
            lastFailure = failure
        }
        Thread.sleep(200)
    }
    throw IllegalStateException("Readiness failed at $stage; inspect the local child log", lastFailure)
}

private fun assertRole(client: String, identity: RoleIdentity) {
    assertEquals(client, identity.clientId)
    assertArm64(identity.architecture)
    assertEquals("Eclipse Adoptium", identity.javaVendor)
    assertEquals(25, identity.javaFeature)
}

private fun assertArm64(architecture: String) {
    assertTrue(architecture in setOf("arm64", "aarch64"), "Expected native ARM64, found $architecture")
}

internal fun newId(): String = UUID.randomUUID().toString()

internal fun writeJson(path: Path, fields: Map<String, Any>) {
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
