package probe

import java.util.concurrent.ConcurrentHashMap
import org.axonframework.common.configuration.Configuration as AxonConfiguration
import org.axonframework.messaging.eventhandling.EventMessage
import org.axonframework.messaging.eventhandling.annotation.EventHandler
import org.axonframework.messaging.eventhandling.processing.streaming.StreamingEventProcessor
import org.axonframework.messaging.eventhandling.processing.streaming.token.store.TokenStore
import org.axonframework.messaging.eventhandling.processing.streaming.token.store.inmemory.InMemoryTokenStore
import org.axonframework.messaging.queryhandling.QueryUpdateEmitter
import org.axonframework.messaging.queryhandling.annotation.QueryHandler
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.core.env.Environment

const val READ_COURSE = "probe.ReadCourse"

@JvmRecord data class ReadCourse(val runId: String, val courseId: String)

@JvmRecord
data class CourseState(
    val runId: String,
    val courseId: String,
    val enrollments: Int,
    val eventId: String?,
    val role: RoleIdentity,
    val processorReady: Boolean,
)

@Configuration(proxyBeanMethods = false)
class ProjectionRoleConfiguration {
    @Bean fun tokenStore(): TokenStore = InMemoryTokenStore()

    @Bean
    fun courseProjection(environment: Environment, axon: AxonConfiguration): CourseProjection =
        CourseProjection(environment.getRequiredProperty("probe.run-id"), axon)
}

class CourseProjection(private val runId: String, private val axon: AxonConfiguration) {
    private val identity by lazy { roleIdentity(axon) }
    private val courses = ConcurrentHashMap<String, CourseState>()

    @QueryHandler(queryName = READ_COURSE)
    fun course(query: ReadCourse): CourseState {
        require(query.runId == runId)
        return courses[query.courseId]
            ?: CourseState(runId, query.courseId, 0, null, identity, processorReady())
    }

    @EventHandler(eventName = ENROLLED_EVENT)
    fun enrolled(enrollment: StudentEnrolled, event: EventMessage, emitter: QueryUpdateEmitter) {
        require(enrollment.runId == runId)
        val state =
            checkNotNull(
                courses.compute(enrollment.courseId) { courseId, previous ->
                    CourseState(
                        runId,
                        courseId,
                        (previous?.enrollments ?: 0) + 1,
                        event.identifier(),
                        identity,
                        processorReady(),
                    )
                },
            )
        emitter.emit(
            ReadCourse::class.java,
            { it.runId == runId && it.courseId == enrollment.courseId },
            state,
        )
    }

    private fun processorReady(): Boolean {
        val processor =
            axon
                .getModuleConfiguration("EventProcessor[probe]")
                .orElseThrow()
                .getComponent(StreamingEventProcessor::class.java, "probe")
        return processor.isRunning &&
            !processor.isError &&
            processor.processingStatus().isNotEmpty()
    }
}
