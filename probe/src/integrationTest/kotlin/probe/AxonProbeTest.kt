package probe

import io.grpc.Status
import java.time.Instant
import java.util.concurrent.ExecutionException
import java.util.concurrent.TimeUnit.SECONDS
import org.axonframework.eventsourcing.eventstore.AppendCondition
import org.axonframework.eventsourcing.eventstore.AppendEventsTransactionRejectedException
import org.axonframework.eventsourcing.eventstore.GlobalIndexConsistencyMarker
import org.axonframework.messaging.eventhandling.EventMessage
import org.axonframework.messaging.eventstreaming.EventCriteria
import org.axonframework.messaging.eventstreaming.Tag
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInfo

class AxonProbeTest {
    @Test
    fun `a forced failure closes the subscription and owned resources`() {
        val runId = newId()
        lateinit var subscription: CourseSubscription
        val failure = ControlledFailure()
        val observed = assertThrows(ControlledFailure::class.java) {
            ProbeFixture(runId).use { fixture ->
                fixture.start()
                fixture.startCommand()
                val query = ReadCourse(runId, newId())
                val before = fixture.startProjection(query)
                assertTrue(fixture.readHistory(EventCriteria.havingAnyTag()).isEmpty())
                subscription = fixture.subscribe(query)
                assertEquals(before, subscription.next("forced failure subscription initial result"))
                assertEquals(0, before.enrollments)
                throw failure
            }
        }
        assertTrue(observed === failure && failure.suppressed.isEmpty())
        assertTrue(subscription.cancellationObserved, "The fixture must cancel its live subscription on failure")
    }

    @Test
    fun `a remote command persists a tagged event`(testInfo: TestInfo) {
        ProbeFixture(newId()).use { fixture ->
            fixture.start()
            val writer = fixture.startCommand()
            val command = EnrollStudent(fixture.runId, newId(), newId())
            val commandId = newId()
            assertTrue(fixture.readHistory(EventCriteria.havingAnyTag()).isEmpty())
            val receipt = fixture.send(WRITE_COMMAND, command, WriteReceipt::class.java, commandId)
            assertReceipt(fixture, writer, command, commandId, receipt)

            val courseHistory = fixture.readHistory(criterion("courseId", command.courseId))
            val studentHistory = fixture.readHistory(criterion("studentId", command.studentId))
            assertWinner(courseHistory, command, receipt)
            assertWinner(studentHistory, command, receipt)
            val registrations = fixture.registrations()
            assertTrue(registrations.getValue(fixture.driverRole.clientId).commandsList.isEmpty())
            assertTrue(WRITE_COMMAND in registrations.getValue(writer.clientId).commandsList)
            val transcript = mapOf(
                "test" to testName(testInfo), "runId" to fixture.runId,
                "context" to AXON_CONTEXT, "dcb" to true, "initialEvents" to 0,
                "worker" to fixture.driverRole, "command" to writer, "receipt" to receipt,
                "courseId" to command.courseId, "studentId" to command.studentId,
                "courseEventId" to courseHistory.single().identifier(),
                "studentEventId" to studentHistory.single().identifier(),
            )
            writeJson(fixture.evidence.resolve("tracer.json"), transcript)
            println("PROBE_TRACER " + JSON.writeValueAsString(transcript))
        }
    }

    @Test
    fun `overlapping writes leave one winner and notify the remote subscriber`(testInfo: TestInfo) {
        val started = Instant.now()
        val runId = System.getProperty("probe.runId").ifBlank { newId() }
        require(runId.matches(Regex("[A-Za-z0-9_-]{1,80}"))) { "Invalid probe run ID" }
        ProbeFixture(runId).use { fixture ->
            fixture.start()
            val command = EnrollStudent(runId, newId(), newId())
            val losingStudent = newId()
            assertNotEquals(command.studentId, losingStudent)
            val query = ReadCourse(runId, command.courseId)
            val writer = fixture.startCommand()
            val baseline = fixture.startProjection(query)
            assertEquals(CourseState(runId, command.courseId, 0, null, baseline.role, true), baseline)

            val roles = listOf(fixture.driverRole, writer, baseline.role)
            assertEquals(roles.size, roles.map { it.pid }.toSet().size)
            assertEquals(roles.size, roles.map { it.clientId }.toSet().size)
            val registrations = fixture.registrations()
            val driverRegistration = registrations.getValue(fixture.driverRole.clientId)
            val writerRegistration = registrations.getValue(writer.clientId)
            val projectionRegistration = registrations.getValue(baseline.role.clientId)
            assertTrue(driverRegistration.commandsList.isEmpty() && driverRegistration.queriesList.isEmpty())
            assertEquals(setOf(READY_COMMAND, WRITE_COMMAND), writerRegistration.commandsList.toSet())
            assertTrue(writerRegistration.queriesList.isEmpty())
            assertTrue(projectionRegistration.commandsList.isEmpty())
            assertEquals(listOf(READ_COURSE), projectionRegistration.queriesList.map { it.request })
            val registeredClients = roles.associate { role ->
                role.clientId to registrations.getValue(role.clientId).clientsList.single().name
            }
            assertEquals(roles.size, registeredClients.values.toSet().size)
            val boundedHistory = EventCriteria.havingAnyTag()
            assertTrue(fixture.readHistory(boundedHistory).isEmpty(), "The fresh server must have no tagged events")

            fixture.subscribe(query).use { subscription ->
                val initial = subscription.next("subscription initial result")
                assertEquals(baseline, initial)

                val courseTag = Tag.of("courseId", command.courseId)
                val winnerTag = Tag.of("studentId", command.studentId)
                val loserTag = Tag.of("studentId", losingStudent)
                val course = EventCriteria.havingTags(courseTag)
                val oldBoundary = course.or(EventCriteria.havingTags(loserTag))
                val marker = emptyHistoryMarker(fixture.engine, oldBoundary)
                val markerPosition = GlobalIndexConsistencyMarker.position(marker)

                val commandId = newId()
                val receipt = fixture.send(WRITE_COMMAND, command, WriteReceipt::class.java, commandId)
                assertReceipt(fixture, writer, command, commandId, receipt)

                val losingEvent = newId()
                assertNotEquals(receipt.eventId, losingEvent)
                val losingWrite = enrollmentEvent(losingEvent, StudentEnrolled(runId, command.courseId, losingStudent, newId()))
                val append = fixture.engine.appendEvents(AppendCondition.withCriteria(oldBoundary).withMarker(marker), null, losingWrite)
                    .get(MESSAGE_TIMEOUT_SECONDS, SECONDS)
                val failure = assertThrows(ExecutionException::class.java) { append.commit().get(MESSAGE_TIMEOUT_SECONDS, SECONDS) }
                val rejection = generateSequence(failure as Throwable) { it.cause }
                    .filterIsInstance<AppendEventsTransactionRejectedException>().single()
                assertEquals(setOf(courseTag, loserTag), rejection.tags())
                assertEquals(Status.Code.CANCELLED, Status.fromThrowable(rejection).code)
                assertTrue(generateSequence(rejection as Throwable) { it.cause }
                    .any { it.message.orEmpty().contains("ConsistencyConditionException") })

                val courseEvents = fixture.readHistory(course)
                val studentEvents = fixture.readHistory(EventCriteria.havingTags(winnerTag))
                val jointEvents = fixture.readHistory(EventCriteria.havingTags(courseTag, winnerTag))
                val losingEvents = fixture.readHistory(EventCriteria.havingTags(loserTag))
                val allEvents = fixture.readHistory(boundedHistory)
                for (history in listOf(courseEvents, studentEvents, jointEvents, allEvents)) {
                    assertWinner(history, command, receipt)
                }
                assertTrue(losingEvents.isEmpty())

                val update = subscription.next("subscription live update")
                assertEquals(CourseState(runId, command.courseId, 1, receipt.eventId, baseline.role, true), update)
                val after = fixture.readCourse(query)
                assertEquals(update, after)

                val transcript = mapOf(
                    "test" to testName(testInfo), "runId" to runId,
                    "startedAt" to started.toString(), "finishedAt" to Instant.now().toString(),
                    "context" to AXON_CONTEXT, "dcb" to true, "credentialFree" to true, "initialEvents" to 0,
                    "worker" to fixture.driverRole, "command" to writer, "projection" to baseline.role,
                    "registeredClients" to registeredClients,
                    "before" to baseline, "initial" to initial, "update" to update, "after" to after,
                    "marker" to markerPosition, "receipt" to receipt, "losingEventId" to losingEvent,
                    "courseId" to command.courseId, "studentId" to command.studentId, "losingStudentId" to losingStudent,
                    "rejection" to mapOf("type" to rejection.javaClass.simpleName, "status" to Status.fromThrowable(rejection).code.name,
                        "serverReason" to "ConsistencyConditionException"),
                    "tagReads" to mapOf("course" to courseEvents.ids(), "winnerStudent" to studentEvents.ids(),
                        "courseAndStudent" to jointEvents.ids(), "loserStudent" to losingEvents.ids(), "history" to allEvents.ids()),
                )
                writeJson(fixture.evidence.resolve("core.json"), transcript)
                println("PROBE_CORE " + JSON.writeValueAsString(transcript))
            }
        }
    }

    private fun assertReceipt(fixture: ProbeFixture, writer: RoleIdentity, command: EnrollStudent, commandId: String, receipt: WriteReceipt) {
        assertEquals(writer, receipt.role)
        assertNotEquals(fixture.driverRole.pid, writer.pid)
        assertEquals(fixture.runId, receipt.runId)
        assertEquals(commandId, receipt.commandId)
        assertEquals(5, setOf(fixture.runId, command.courseId, command.studentId, commandId, receipt.eventId).size)
    }

    private fun assertWinner(history: List<EventMessage>, command: EnrollStudent, receipt: WriteReceipt) {
        assertEquals(listOf(receipt.eventId), history.ids())
        val event = history.single()
        assertEquals(ENROLLED_EVENT, event.type().qualifiedName().fullName())
        assertEquals(
            StudentEnrolled(command.runId, command.courseId, command.studentId, receipt.commandId),
            event.payloadAs(StudentEnrolled::class.java),
        )
    }

    private fun List<EventMessage>.ids() = map { it.identifier() }

    private fun criterion(key: String, value: String) = EventCriteria.havingTags(Tag.of(key, value))

    private fun testName(info: TestInfo) = "${javaClass.name}.${info.testMethod.orElseThrow().name}"
}

private class ControlledFailure : RuntimeException("controlled failure after subscription startup")
