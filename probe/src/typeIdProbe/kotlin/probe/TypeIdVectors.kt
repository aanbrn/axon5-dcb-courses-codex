package probe

import de.fxlae.typeid.TypeId
import java.io.File
import java.nio.ByteBuffer
import java.util.HexFormat
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import tools.jackson.databind.JsonNode
import tools.jackson.databind.json.JsonMapper
import tools.jackson.databind.node.ObjectNode

private val json = JsonMapper.builder().build()
private val tags = mapOf("courseId" to "course", "studentId" to "student")
private val hex = HexFormat.of()

private fun JsonNode.text(key: String): String = required(key).asString()

private fun UUID.bytes(): ByteArray = ByteBuffer.allocate(16)
    .putLong(mostSignificantBits)
    .putLong(leastSignificantBits)
    .array()

private fun decodeExpected(value: String, prefix: String): TypeId = TypeId.parse(value).also {
    require(it.prefix() == prefix) { "Expected TypeID prefix '$prefix', found '${it.prefix()}'" }
}

private data class Sample(val tag: String, val prefix: String, val uuid: UUID)

private fun samples(fixture: JsonNode, origin: String): List<Sample> {
    val values = fixture.required(origin).asSequence().map { vector ->
        Sample(vector.text("tag"), vector.text("prefix"), UUID.fromString(vector.text("uuid")))
    }.toList()
    require(values.size == tags.size && values.associate { it.tag to it.prefix } == tags) {
        "$origin must provide the exact courseId and studentId tags and prefixes"
    }
    require(values.all { it.uuid.version() == 7 && it.uuid.variant() == 2 }) { "$origin requires RFC UUIDv7 inputs" }
    return values
}

private fun validateExchange(
    exchange: JsonNode,
    runId: String,
    exchangeId: String,
    origin: String,
    samples: List<Sample>,
) {
    require(exchange.text("runId") == runId && exchange.text("exchangeId") == exchangeId) { "Stale $origin exchange" }
    require(exchange.text("origin") == origin) { "Expected the $origin exchange" }
    val values = exchange.required("vectors")
    require(values.isArray && values.size() == samples.size) { "Unexpected $origin vector count" }
    for (sample in samples) {
        val record = values.single { it.text("tag") == sample.tag }
        val context = "$origin ${sample.tag}"
        require(record.text("prefix") == sample.prefix) { "$context prefix differs from the fixture" }
        val raw = record.text("uuidBytes")
        val expected = sample.uuid.bytes()
        require(raw == hex.formatHex(expected)) { "$context UUID bytes differ from the fixture" }
        val value = record.text("typeid")
        val decoded = decodeExpected(value, sample.prefix)
        require(decoded.uuid().bytes().contentEquals(expected)) { "$context decoded UUID bytes differ" }
        require(TypeId.of(sample.prefix, sample.uuid).toString() == value) { "$context is not canonically encoded" }
    }
}

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

        val runId = System.getProperty("probe.typeIdRunId")
        val exchangeId = System.getProperty("probe.typeIdExchangeId")
        val inputs = samples(fixture, "kotlin")
        val exchange = json.createObjectNode().put("origin", "kotlin").put("runId", runId).put("exchangeId", exchangeId)
        val vectors = exchange.putArray("vectors")
        for (sample in inputs) {
            vectors.addObject().put("tag", sample.tag).put("prefix", sample.prefix)
                .put("uuidBytes", hex.formatHex(sample.uuid.bytes()))
                .put("typeid", TypeId.of(sample.prefix, sample.uuid).toString())
        }
        validateExchange(exchange, runId, exchangeId, "kotlin", inputs)
        val output = File(System.getProperty("probe.typeIdKotlinExchange"))
        output.parentFile.mkdirs()
        json.writerWithDefaultPrettyPrinter().writeValue(output, exchange)
    }
}

fun main(args: Array<String>) {
    require(args.size == 5 && args[0] == "consume") {
        "Usage: TypeIdVectorsKt consume <fixture> <TypeScript exchange> <run ID> <exchange ID>"
    }
    val fixture = json.readTree(File(args[1]))
    val input = File(args[2])
    require(input.isFile) { "The TypeScript exchange is missing: $input" }
    val runId = args[3]
    val exchangeId = args[4]
    require(runId.isNotBlank() && exchangeId.isNotBlank()) { "Current run and exchange IDs are required" }
    val inputs = samples(fixture, "typescript")
    val exchange = json.readTree(input)
    validateExchange(exchange, runId, exchangeId, "typescript", inputs)

    fun rejectChanged(field: String, value: String) {
        val changed = exchange.deepCopy() as ObjectNode
        (changed.required("vectors").first() as ObjectNode).put(field, value)
        val exception = runCatching { validateExchange(changed, runId, exchangeId, "typescript", inputs) }.exceptionOrNull()
        check(exception is IllegalArgumentException) { "Kotlin accepted a corrupted TypeScript $field" }
    }
    val first = exchange.required("vectors").first()
    val bytes = hex.parseHex(first.text("uuidBytes"))
    bytes[0] = (bytes[0].toInt() xor 1).toByte()
    rejectChanged("uuidBytes", hex.formatHex(bytes))
    rejectChanged("prefix", "different")

    val previous = exchange.deepCopy() as ObjectNode
    previous.put("exchangeId", "previous-invocation")
    val stale = runCatching { validateExchange(previous, runId, exchangeId, "typescript", inputs) }.exceptionOrNull()
    check(stale is IllegalArgumentException) { "Kotlin accepted a stale TypeScript exchange" }
    println("Kotlin validated ${inputs.size} TypeScript UUID byte pairs and rejected changed prefix, bytes and exchange ID")
}
