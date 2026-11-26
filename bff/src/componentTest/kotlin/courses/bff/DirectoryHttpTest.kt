package courses.bff

import com.networknt.schema.InvalidSchemaException
import com.networknt.schema.Schema
import com.networknt.schema.SchemaLocation
import com.networknt.schema.SchemaRegistry
import com.networknt.schema.dialect.Dialects
import courses.fixtures.DirectoryFixtures
import courses.fixtures.DirectoryRole
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.server.LocalServerPort
import tools.jackson.core.JsonPointer
import tools.jackson.databind.JsonNode
import tools.jackson.databind.json.JsonMapper
import tools.jackson.databind.node.ArrayNode
import tools.jackson.databind.node.ObjectNode

@SpringBootTest(
    classes = [BffApplication::class],
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    properties = ["server.address=127.0.0.1"],
)
class DirectoryHttpTest {
    @LocalServerPort private var port: Int = 0

    private val mapper = JsonMapper.builder().build()
    private val directoryPath = "/api/demo-roles"
    private val jsonMediaType = "application/json"
    private val contractBytes =
        checkNotNull(BffApplication::class.java.getResourceAsStream("/static/openapi.json")).use {
            it.readAllBytes()
        }

    @Test
    fun `directory response contains the documented roles in order`() {
        val response = get(directoryPath)
        assertEquals(200, response.statusCode())
        val mediaType = mediaType(response)
        assertEquals(jsonMediaType, mediaType)
        val directory = mapper.readTree(response.body())
        val violations = responseSchema(response.statusCode(), mediaType).validate(directory)
        assertTrue(violations.isEmpty()) { "Directory response violates OpenAPI: $violations" }

        val expected = DirectoryFixtures.defaultDirectory
        val administrator = readRole(directory.required("administrator"))
        assertEquals(expected.administrator, administrator)
        val students = directory.required("students").values().map(::readRole)
        assertEquals(expected.students, students)
        val ids = (listOf(administrator) + students).map { it.id }
        assertEquals(ids, ids.distinct())
    }

    @Test
    fun `served OpenAPI matches the canonical contract`() {
        val canonical = Files.readAllBytes(Path.of(System.getProperty("courses.openapi.source")))
        val response = get("/openapi.json")
        assertEquals(200, response.statusCode())
        assertEquals(jsonMediaType, mediaType(response))
        assertArrayEquals(canonical, response.body(), "Served OpenAPI differs from its source")
        assertArrayEquals(canonical, contractBytes, "Packaged OpenAPI differs from its source")

        val paths = mapper.readTree(contractBytes).required("paths")
        assertEquals(setOf(directoryPath), paths.propertyNames().toSet())
        val operations = paths.required(directoryPath)
        assertEquals(setOf("get"), operations.propertyNames().toSet())
        assertEquals("listDemoRoles", operations.required("get").required("operationId").asString())
    }

    @Test
    fun `a response without an administrator is rejected`() {
        val corrupted =
            mapper.writeValueAsBytes(
                mapOf("students" to DirectoryFixtures.defaultDirectory.students),
            )
        val violations = responseSchema(200, jsonMediaType).validate(mapper.readTree(corrupted))
        assertEquals(
            listOf("required" to "administrator"),
            violations.map { it.keyword to it.property },
        )
    }

    @Test
    fun `directory schema rejects whitespace-only role fields`() {
        val directory = mapper.readTree(get(directoryPath).body())
        val schema = responseSchema(200, jsonMediaType)
        for (rolePath in listOf("/administrator", "/students/0")) {
            for (field in listOf("id", "label")) {
                for (blank in listOf(" \t", "\u00A0", "\uFEFF")) {
                    val mutated = directory.deepCopy()
                    (mutated.at(rolePath) as ObjectNode).put(field, blank)
                    val violations = schema.validate(mutated)
                    assertEquals(
                        listOf("pattern" to "$rolePath/$field"),
                        violations.map { it.keyword to it.instanceLocation.toString() },
                    )
                }
            }
        }
    }

    @Test
    fun `directory schema accepts role fields with content and an empty student list`() {
        val directory = mapper.readTree(get(directoryPath).body())
        val schema = responseSchema(200, jsonMediaType)
        (directory.required("administrator") as ObjectNode)
            .put("id", " \tadmin ")
            .put("label", " \uFEFFAdministrator")
        (directory.at("/students/0") as ObjectNode)
            .put("id", "\u0085")
            .put("label", " \u00A0Maya Chen \t")
        assertTrue(schema.validate(directory).isEmpty())

        (directory.required("students") as ArrayNode).removeAll()
        assertTrue(schema.validate(directory).isEmpty())
    }

    @Test
    fun `schema references stay within the contract document`() {
        val mutated = mapper.readTree(contractBytes)
        val schema = mutated.at(responseSchemaPointer(200, jsonMediaType)) as ObjectNode
        schema.put("\$ref", "https://schemas.invalid/role.json")
        val failure =
            assertThrows<InvalidSchemaException> {
                responseSchema(200, jsonMediaType, mapper.writeValueAsBytes(mutated))
                    .validate(mapper.createObjectNode())
            }
        assertTrue(failure.message.orEmpty().contains("not allowed to be loaded"), failure.message)
    }

    private fun responseSchema(
        status: Int,
        mediaType: String,
        document: ByteArray = contractBytes,
    ): Schema {
        val documentIri = "https://contract.invalid/openapi.json"
        val registry =
            SchemaRegistry.withDialect(Dialects.getOpenApi31()) { builder ->
                builder.schemaLoader { loader ->
                    loader.allow { iri -> iri.toString() == documentIri }
                    loader.resourceLoaders {
                        it.resources(mapOf(documentIri to document.decodeToString()))
                    }
                }
            }
        return registry.getSchema(
            SchemaLocation.of("$documentIri#${responseSchemaPointer(status, mediaType)}"),
        )
    }

    private fun responseSchemaPointer(status: Int, mediaType: String): JsonPointer =
        JsonPointer.compile("/paths")
            .appendProperty(directoryPath)
            .appendProperty("get")
            .appendProperty("responses")
            .appendProperty(status.toString())
            .appendProperty("content")
            .appendProperty(mediaType)
            .appendProperty("schema")

    private fun readRole(role: JsonNode): DirectoryRole =
        DirectoryRole(
            id = role.required("id").asString(),
            label = role.required("label").asString(),
            kind = role.required("kind").asString(),
        )

    private fun get(path: String): HttpResponse<ByteArray> {
        val timeout = Duration.ofSeconds(10)
        val request =
            HttpRequest.newBuilder(URI.create("http://127.0.0.1:$port$path"))
                .timeout(timeout)
                .GET()
                .build()
        return HttpClient.newBuilder()
            .proxy(HttpClient.Builder.NO_PROXY)
            .connectTimeout(timeout)
            .build()
            .use { it.send(request, HttpResponse.BodyHandlers.ofByteArray()) }
    }

    private fun mediaType(response: HttpResponse<ByteArray>): String =
        response
            .headers()
            .firstValue("Content-Type")
            .orElseThrow()
            .substringBefore(';')
            .trim()
            .lowercase()
}
