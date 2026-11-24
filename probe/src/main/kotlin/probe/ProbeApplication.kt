package probe

import io.axoniq.framework.axonserver.connector.api.AxonServerConfiguration
import io.axoniq.framework.axonserver.connector.api.AxonServerConnectionManager
import io.axoniq.framework.axonserver.connector.event.AxonServerEventStorageEngine
import io.axoniq.framework.messaging.commandhandling.distributed.DistributedCommandBus
import io.axoniq.framework.messaging.queryhandling.distributed.DistributedQueryBus
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit.SECONDS
import org.axonframework.common.configuration.Configuration as AxonConfiguration
import org.axonframework.common.infra.FilesystemStyleComponentDescriptor
import org.axonframework.eventsourcing.eventstore.AppendCondition
import org.axonframework.eventsourcing.eventstore.ConsistencyMarker
import org.axonframework.eventsourcing.eventstore.EventStorageEngine
import org.axonframework.eventsourcing.eventstore.GenericTaggedEventMessage
import org.axonframework.eventsourcing.eventstore.SourcingCondition
import org.axonframework.eventsourcing.eventstore.TerminalEventMessage
import org.axonframework.messaging.commandhandling.CommandMessage
import org.axonframework.messaging.commandhandling.CommandBus
import org.axonframework.messaging.commandhandling.annotation.CommandHandler
import org.axonframework.messaging.core.MessageType
import org.axonframework.messaging.eventhandling.GenericEventMessage
import org.axonframework.messaging.eventstreaming.EventCriteria
import org.axonframework.messaging.eventstreaming.Tag
import org.axonframework.messaging.queryhandling.QueryBus
import org.springframework.boot.SpringBootConfiguration
import org.springframework.boot.WebApplicationType
import org.springframework.boot.autoconfigure.EnableAutoConfiguration
import org.springframework.boot.builder.SpringApplicationBuilder
import org.springframework.context.ConfigurableApplicationContext
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.core.env.Environment

const val AXON_CONTEXT = "default"
const val WRITE_COMMAND = "probe.EnrollStudent"
const val ENROLLED_EVENT = "probe.StudentEnrolled"
const val READY_COMMAND = "probe.CommandRoleReady"
const val MESSAGE_TIMEOUT_SECONDS = 20L

@JvmRecord
data class EnrollStudent(val runId: String, val courseId: String, val studentId: String)

@JvmRecord
data class StudentEnrolled(val runId: String, val courseId: String, val studentId: String, val commandId: String)

@JvmRecord
data class WriteReceipt(val runId: String, val commandId: String, val eventId: String, val role: RoleIdentity)

@JvmRecord
data class RoleIdentity(
    val pid: Long,
    val clientId: String,
    val architecture: String,
    val javaVendor: String,
    val javaVersion: String,
    val engine: String,
    val javaFeature: Int,
    val commandBus: String,
    val queryBus: String,
)

enum class ProbeRole { DRIVER, COMMAND, PROJECTION }

@SpringBootConfiguration(proxyBeanMethods = false)
@EnableAutoConfiguration
class ProbeApplication

@Configuration(proxyBeanMethods = false)
class CommandRoleConfiguration {
    @Bean
    fun enrollmentHandler(environment: Environment, axon: AxonConfiguration): EnrollmentHandler =
        EnrollmentHandler(
            environment.getRequiredProperty("probe.run-id"),
            roleIdentity(axon),
            storageEngine(axon),
        )
}

class EnrollmentHandler(
    private val runId: String,
    private val identity: RoleIdentity,
    private val engine: EventStorageEngine,
) {
    @CommandHandler(commandName = READY_COMMAND)
    fun ready(requestRunId: String): RoleIdentity {
        require(requestRunId == runId)
        return identity
    }

    @CommandHandler(commandName = WRITE_COMMAND, routingKey = "courseId")
    fun enroll(command: EnrollStudent, message: CommandMessage): WriteReceipt {
        require(command.runId == runId)
        val courseTag = Tag.of("courseId", command.courseId)
        val studentTag = Tag.of("studentId", command.studentId)
        val boundary = EventCriteria.havingTags(courseTag).or(EventCriteria.havingTags(studentTag))
        val marker = emptyHistoryMarker(engine, boundary)
        val condition = AppendCondition.withCriteria(boundary).withMarker(marker)
        val commandId = message.identifier()
        val eventId = UUID.randomUUID().toString()
        val event = enrollmentEvent(eventId, StudentEnrolled(runId, command.courseId, command.studentId, commandId))
        val transaction = engine.appendEvents(condition, null, event)
            .get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
        transaction.commit().get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
        return WriteReceipt(runId, commandId, eventId, identity)
    }
}

fun emptyHistoryMarker(engine: EventStorageEngine, boundary: EventCriteria): ConsistencyMarker {
    val source = engine.source(SourcingCondition.conditionFor(boundary), null)
    try {
        val markers = source.reduce(emptyList<ConsistencyMarker>()) { collected, entry ->
            check(entry.message() is TerminalEventMessage) { "The enrollment boundary must start empty" }
            checkNotNull(collected) + checkNotNull(entry.getResource(ConsistencyMarker.RESOURCE_KEY))
        }.get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
        return checkNotNull(markers).single()
    } finally {
        source.close()
    }
}

fun enrollmentEvent(eventId: String, enrollment: StudentEnrolled): GenericTaggedEventMessage<GenericEventMessage> {
    val event = GenericEventMessage(eventId, MessageType(ENROLLED_EVENT), enrollment, emptyMap(), Instant.now())
    return GenericTaggedEventMessage(event, setOf(Tag.of("courseId", enrollment.courseId), Tag.of("studentId", enrollment.studentId)))
}

fun startProbeRole(endpoint: String, clientId: String, runId: String, configFile: Path, role: ProbeRole): ConfigurableApplicationContext {
    val sources = when (role) {
        ProbeRole.DRIVER -> arrayOf(ProbeApplication::class.java)
        ProbeRole.COMMAND -> arrayOf(ProbeApplication::class.java, CommandRoleConfiguration::class.java)
        ProbeRole.PROJECTION -> arrayOf(ProbeApplication::class.java, ProjectionRoleConfiguration::class.java)
    }
    return SpringApplicationBuilder(*sources)
        .web(WebApplicationType.NONE)
        .run(
            "--spring.config.location=${configFile.toUri()}",
            "--spring.application.name=$clientId",
            "--spring.main.banner-mode=off",
            "--axon.update-check.disabled=true",
            "--axon.axonserver.servers=$endpoint",
            "--axon.axonserver.context=$AXON_CONTEXT",
            "--axon.axonserver.client-id=$clientId",
            "--axon.axonserver.force-reconnect-through-servers=true",
            "--probe.run-id=$runId",
        )
}

fun storageEngine(axon: AxonConfiguration): AxonServerEventStorageEngine =
    checkNotNull(axon.getComponent(EventStorageEngine::class.java) as? AxonServerEventStorageEngine) {
        "The active event storage engine must be AxonServerEventStorageEngine"
    }

fun roleIdentity(axon: AxonConfiguration): RoleIdentity {
    val commandBus = axon.getComponent(CommandBus::class.java)
    val queryBus = axon.getComponent(QueryBus::class.java)
    val buses = FilesystemStyleComponentDescriptor().apply {
        describeProperty("commandBus", commandBus)
        describeProperty("queryBus", queryBus)
    }.describe()
    check(DistributedCommandBus::class.java.name in buses && DistributedQueryBus::class.java.name in buses) {
        "The configured bus wrappers must delegate to the distributed command and query buses"
    }
    return RoleIdentity(
        ProcessHandle.current().pid(),
        axon.getComponent(AxonServerConfiguration::class.java).clientId,
        System.getProperty("os.arch"),
        System.getProperty("java.vendor"),
        Runtime.version().toString(),
        storageEngine(axon).javaClass.name,
        Runtime.version().feature(),
        DistributedCommandBus::class.java.name,
        DistributedQueryBus::class.java.name,
    )
}

fun requireServerContext(axon: AxonConfiguration) {
    val context = axon.getComponent(AxonServerConnectionManager::class.java).connection
        .adminChannel().getContextOverview(AXON_CONTEXT).get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
    check(context.name == AXON_CONTEXT && context.dcbContext) { "The server must expose the DCB default context" }
}

fun main(args: Array<String>) {
    require(args.size == 4) { "Expected an endpoint, client ID, run ID and role" }
    val configFile = Files.createFile(Path.of("application.properties"))
    startProbeRole(args[0], args[1], args[2], configFile.toAbsolutePath(), ProbeRole.valueOf(args[3])).use { context ->
        requireServerContext(context.getBean(AxonConfiguration::class.java))
        CountDownLatch(1).await()
    }
}
