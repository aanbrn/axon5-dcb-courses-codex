package probe

import org.axonframework.extension.springboot.autoconfig.JacksonConverterAutoConfiguration
import org.axonframework.messaging.eventstreaming.Tag
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import tools.jackson.databind.json.JsonMapper

class ProbeContractsTest {
    @Test
    fun `the enrollment contract preserves case sensitive tags`() {
        val converter = JacksonConverterAutoConfiguration().apply {
            setBeanClassLoader(ProbeContractsTest::class.java.classLoader)
        }.converter(JsonMapper.builder().findAndAddModules().build())
        val command = EnrollStudent("run", "Course-aB", "Student-Ba")
        val encodedCommand = checkNotNull(converter.convert(command, ByteArray::class.java))
        assertEquals(command, converter.convert(encodedCommand, EnrollStudent::class.java))
        val event = StudentEnrolled(command.runId, command.courseId, command.studentId, "command")
        val encodedEvent = checkNotNull(converter.convert(event, ByteArray::class.java))
        val restored = checkNotNull(converter.convert(encodedEvent, StudentEnrolled::class.java))
        assertEquals(event, restored)
        assertEquals(setOf(Tag.of("courseId", "Course-aB"), Tag.of("studentId", "Student-Ba")),
            enrollmentEvent("event", restored).tags())
        assertEquals("Eclipse Adoptium", System.getProperty("java.vendor"))
        assertEquals(Runtime.version().feature().toString(), System.getProperty("probe.javaFeature"),
            "The worker feature must come from the repository toolchain owner")
        assertEquals(System.getenv("HOME"), System.getProperty("user.home"))
        println("PROBE_JAVA vendor=${System.getProperty("java.vendor")} version=${Runtime.version()} arch=${System.getProperty("os.arch")}")
    }
}
