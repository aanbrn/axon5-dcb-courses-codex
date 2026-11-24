package probe

import de.fxlae.typeid.TypeId
import java.io.File
import java.nio.ByteBuffer
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import tools.jackson.databind.JsonNode
import tools.jackson.databind.json.JsonMapper

private val json = JsonMapper.builder().build()

private fun JsonNode.text(key: String): String = required(key).asString()

private fun UUID.bytes(): ByteArray = ByteBuffer.allocate(16)
    .putLong(mostSignificantBits)
    .putLong(leastSignificantBits)
    .array()

private fun decodeExpected(value: String, prefix: String): TypeId = TypeId.parse(value)

class TypeIdVectorsTest {
    @Test
    fun `canonical vectors preserve bytes and reject the wrong prefix`() {
        val fixture = json.readTree(File(System.getProperty("probe.typeIdFixture")))
        for (vector in fixture.required("valid")) {
            val name = vector.text("name")
            val prefix = vector.text("prefix")
            val uuid = UUID.fromString(vector.text("uuid"))
            val typeid = vector.text("typeid")
            val decoded = decodeExpected(typeid, prefix)
            assertEquals(prefix, decoded.prefix(), name)
            assertArrayEquals(uuid.bytes(), decoded.uuid().bytes(), name)
            assertEquals(typeid, TypeId.of(prefix, uuid).toString(), name)
        }
        for (vector in fixture.required("invalid")) {
            assertThrows(IllegalArgumentException::class.java, { TypeId.parse(vector.text("typeid")) }, vector.text("name"))
        }

        val student = fixture.required("kotlin").single { it.text("tag") == "studentId" }
        val studentId = TypeId.of(student.text("prefix"), UUID.fromString(student.text("uuid"))).toString()
        assertThrows(IllegalArgumentException::class.java, { decodeExpected(studentId, "course") },
            "A valid student TypeID must be rejected where a course prefix is expected")
    }
}
