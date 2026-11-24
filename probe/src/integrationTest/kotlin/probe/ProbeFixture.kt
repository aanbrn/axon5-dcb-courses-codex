package probe

import com.github.dockerjava.api.model.ExposedPort
import com.github.dockerjava.api.model.Ports
import com.github.dockerjava.api.exception.NotFoundException
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
import java.util.concurrent.TimeoutException
import java.util.concurrent.TimeUnit.MILLISECONDS
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
private const val RUN_LABEL = "probe.run"

internal class ProbeFixture(val runId: String) : AutoCloseable {
    val evidence: Path = Path.of(System.getProperty("probe.evidenceDirectory"))
    private val attempt: Path = Files.createTempDirectory(Files.createDirectories(evidence), "$runId-")
    private val docker = DockerClientFactory.instance().client()
    private val server = probeServer(serverImage.nativeReference, runId)
    private val processes = mutableMapOf<ProbeRole, Process>()
    private val subscriptions = mutableListOf<CourseSubscription>()
    private val timings = linkedMapOf<String, Long>()
    private var driver: ConfigurableApplicationContext? = null
    private var containerId: String? = null
    lateinit var imageEvidence: Map<String, Any>
        private set
    lateinit var cleanup: CleanupEvidence
        private set

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
        measure("serverReadyMs") {
            try {
                server.start()
            } catch (failure: RuntimeException) {
                throw IllegalStateException("Readiness failed at server HTTP and default DCB leader", failure)
            }
        }
        val id = checkNotNull(server.containerId)
        containerId = id
        val live = docker.inspectContainerCmd(id).exec()
        assertEquals(runId, live.config.labels?.get(RUN_LABEL))
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
        imageEvidence = mapOf(
            "runId" to runId, "checkedAt" to serverImage.checkedAt, "index" to serverImage.reference,
            "arm64" to serverImage.arm64, "amd64" to serverImage.amd64,
            "daemon" to "${daemon.operatingSystem}/${daemon.arch}", "daemonVersion" to checkNotNull(daemon.version),
            "runningImageId" to checkNotNull(activeImage.id), "runningArchitecture" to imageArchitecture,
        )
        writeJson(attempt.resolve("images.json"), imageEvidence)
        val config = Files.createFile(attempt.resolve("application.properties"))
        driver = startProbeRole(endpoint, clientName(ProbeRole.DRIVER), runId, config, ProbeRole.DRIVER)
        assertTrue(checkNotNull(driver).getBeansOfType(EnrollmentHandler::class.java).isEmpty())
        assertTrue(checkNotNull(driver).getBeansOfType(CourseProjection::class.java).isEmpty())
        measure("driverContextReadyMs") {
            try {
                requireServerContext(axon)
            } catch (failure: Exception) {
                throw IllegalStateException("Readiness failed at driver DCB context", failure)
            }
        }
        assertRole(clientName(ProbeRole.DRIVER), driverRole)
        return this
    }

    fun startCommand(): RoleIdentity {
        val process = startChild(ProbeRole.COMMAND)
        val identity = measure("commandReadyMs") {
            awaitRole("command handler registration", process) { timeout ->
                send(READY_COMMAND, runId, RoleIdentity::class.java, timeoutMs = timeout)
            }
        }
        assertChild(ProbeRole.COMMAND, process, identity)
        return identity
    }

    fun startProjection(query: ReadCourse): CourseState {
        val process = startChild(ProbeRole.PROJECTION)
        val state = measure("projectionReadyMs") {
            awaitRole("projection handler registration and event processor", process) { timeout ->
                readCourse(query, timeout).takeIf { it.processorReady }
            }
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

    fun readCourse(query: ReadCourse, timeoutMs: Long = SECONDS.toMillis(MESSAGE_TIMEOUT_SECONDS)): CourseState =
        queries.query(queryMessage(query), CourseState::class.java).get(timeoutMs, MILLISECONDS)

    fun subscribe(query: ReadCourse): CourseSubscription = CourseSubscription().also {
        subscriptions.add(it)
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

    fun <T : Any> send(name: String, payload: Any, result: Class<T>, id: String = newId(),
                       timeoutMs: Long = SECONDS.toMillis(MESSAGE_TIMEOUT_SECONDS)): T {
        val message = GenericCommandMessage(GenericMessage(id, MessageType(name), payload, emptyMap()))
        return axon.getComponent(CommandGateway::class.java).send(message, result).get(timeoutMs, MILLISECONDS)
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
        var error: Exception? = null
        fun closeResource(action: () -> Unit) {
            try {
                action()
            } catch (failure: Exception) {
                error?.addSuppressed(failure) ?: run { error = failure }
            }
        }
        measure("cleanupMs") {
            subscriptions.forEach { closeResource(it::close) }
            processes.values.forEach { process -> closeResource {
                process.destroy()
                if (!process.waitFor(10, SECONDS)) process.destroyForcibly()
                check(process.waitFor(5, SECONDS)) { "Process ${process.pid()} did not exit" }
            } }
            closeResource { driver?.close() }
            closeResource {
                if (server.containerId != null) Files.writeString(attempt.resolve("server.log"), server.logs)
            }
            closeResource(server::close)
        }
        error?.let { throw it }
        val id = containerId ?: return
        val removed = try {
            docker.inspectContainerCmd(id).exec()
            false
        } catch (_: NotFoundException) {
            true
        }
        check(removed && docker.listContainersCmd().withShowAll(true)
            .withLabelFilter(mapOf(RUN_LABEL to runId)).exec().isEmpty()) { "Probe container was not removed" }
        check(processes.values.none { it.isAlive }) { "A probe child process did not exit" }
        check(subscriptions.all { it.cancellationObserved }) { "A probe subscription was not cancelled" }
        cleanup = CleanupEvidence(id, processes.values.map { it.pid() }, subscriptions.size, removed, timings.toMap())
    }

    private inline fun <T> measure(stage: String, action: () -> T): T {
        val start = System.nanoTime()
        try {
            return action()
        } finally {
            timings[stage] = Duration.ofNanos(System.nanoTime() - start).toMillis()
        }
    }

    companion object {
        private val serverImage by lazy { ServerImage.verify(System.getProperty("probe.serverImage")) }
    }
}

@JvmRecord
internal data class CleanupEvidence(
    val containerId: String,
    val exitedPids: List<Long>,
    val cancelledSubscriptions: Int,
    val containerRemoved: Boolean,
    val timingsMs: Map<String, Long>,
)

internal class CourseSubscription : Subscriber<CourseState>, AutoCloseable {
    private val results = LinkedBlockingQueue<Result<CourseState>>()
    private var subscription: Subscription? = null
    private var closed = false
    var cancellationObserved: Boolean = false
        private set

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
        if (closed) return
        closed = true
        subscription?.let {
            it.cancel()
            cancellationObserved = true
        }
    }
}

private class ProbeServer(image: DockerImageName) : GenericContainer<ProbeServer>(image)

private fun probeServer(image: String, runId: String): ProbeServer = ProbeServer(DockerImageName.parse(image)).apply {
    withReuse(false)
    withLabel(RUN_LABEL, runId)
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

private fun <T : Any> awaitRole(stage: String, process: Process, request: (Long) -> T?): T {
    val end = System.nanoTime() + Duration.ofSeconds(45).toNanos()
    var lastFailure: Exception? = null
    while (System.nanoTime() < end && process.isAlive) {
        try {
            val remainingMs = Duration.ofNanos(end - System.nanoTime()).toMillis().coerceIn(1, 2_000)
            request(remainingMs)?.let { return it }
        } catch (failure: ExecutionException) {
            lastFailure = failure
        } catch (failure: TimeoutException) {
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
