package probe

import io.axoniq.framework.axonserver.connector.api.AxonServerConfiguration
import io.axoniq.framework.axonserver.connector.api.AxonServerConnectionManager
import io.axoniq.framework.axonserver.connector.event.AxonServerEventStorageEngine
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit.SECONDS
import org.axonframework.common.configuration.Configuration as AxonConfiguration
import org.axonframework.eventsourcing.eventstore.EventStorageEngine
import org.axonframework.messaging.commandhandling.annotation.CommandHandler
import org.axonframework.messaging.commandhandling.CommandMessage
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
)

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
        )
}

class EnrollmentHandler(private val runId: String, private val identity: RoleIdentity) {
    @CommandHandler(commandName = READY_COMMAND)
    fun ready(requestRunId: String): RoleIdentity {
        require(requestRunId == runId)
        return identity
    }

    @CommandHandler(commandName = WRITE_COMMAND, routingKey = "courseId")
    fun enroll(command: EnrollStudent, message: CommandMessage): WriteReceipt {
        require(command.runId == runId)
        return WriteReceipt(runId, message.identifier(), UUID.randomUUID().toString(), identity)
    }
}

fun startProbeRole(endpoint: String, clientId: String, runId: String, configFile: Path, command: Boolean): ConfigurableApplicationContext {
    val sources = if (command) arrayOf(ProbeApplication::class.java, CommandRoleConfiguration::class.java)
        else arrayOf(ProbeApplication::class.java)
    return SpringApplicationBuilder(*sources)
        .web(WebApplicationType.NONE)
        .run(
            "--spring.config.location=${configFile.toUri()}",
            "--spring.application.name=$clientId",
            "--spring.main.banner-mode=off",
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

fun roleIdentity(axon: AxonConfiguration): RoleIdentity = RoleIdentity(
    ProcessHandle.current().pid(),
    axon.getComponent(AxonServerConfiguration::class.java).clientId,
    System.getProperty("os.arch"),
    System.getProperty("java.vendor"),
    Runtime.version().toString(),
    storageEngine(axon).javaClass.name,
)

fun requireServerContext(axon: AxonConfiguration) {
    val context = axon.getComponent(AxonServerConnectionManager::class.java).connection
        .adminChannel().getContextOverview(AXON_CONTEXT).get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
    check(context.name == AXON_CONTEXT && context.dcbContext) { "The server must expose the DCB default context" }
}

fun main(args: Array<String>) {
    require(args.size == 3) { "Expected an endpoint, client ID and run ID" }
    val configFile = Files.createFile(Path.of("application.properties"))
    startProbeRole(args[0], args[1], args[2], configFile.toAbsolutePath(), command = true).use { context ->
        requireServerContext(context.getBean(AxonConfiguration::class.java))
        CountDownLatch(1).await()
    }
}
