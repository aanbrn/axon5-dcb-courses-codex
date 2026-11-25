package courses.bff

import courses.fixtures.DirectoryFixtures
import courses.fixtures.DirectoryRole
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.server.LocalServerPort
import tools.jackson.databind.JsonNode
import tools.jackson.databind.json.JsonMapper

@SpringBootTest(
    classes = [BffApplication::class],
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    properties = ["server.address=127.0.0.1"],
)
class DirectoryHttpTest {
    @LocalServerPort private var port: Int = 0

    private val mapper = JsonMapper.builder().build()

    @Test
    fun `directory response contains the documented roles in order`() {
        val response = get("/api/demo-roles")
        assertEquals(200, response.statusCode())
        assertEquals("application/json", mediaType(response))
        val body = response.body()
        assertEquals(emptyList<Pair<String, String?>>(), schemaViolations(body))

        val directory = mapper.readTree(body)
        val expected = DirectoryFixtures.defaultDirectory
        assertEquals(expected.administrator, readRole(directory.required("administrator")))
        val students =
            directory.required("students").iterator().asSequence().map(::readRole).toList()
        assertEquals(expected.students, students)
    }

    @Test
    fun `a response without an administrator is rejected`() {
        val corrupted =
            mapper.writeValueAsBytes(
                mapOf("students" to DirectoryFixtures.defaultDirectory.students),
            )
        assertEquals(listOf("required" to "administrator"), schemaViolations(corrupted))
    }

    private fun schemaViolations(body: ByteArray): List<Pair<String, String?>> {
        mapper.readTree(body)
        return emptyList()
    }

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
        response.headers().firstValue("Content-Type").orElseThrow().substringBefore(';').trim()
}
