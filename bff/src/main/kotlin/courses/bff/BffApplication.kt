package courses.bff

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

/** Configures the Spring Boot application for the browser-facing API. */
@SpringBootApplication class BffApplication

/**
 * Starts the browser-facing API.
 *
 * @param args Spring Boot command-line arguments.
 */
fun main(args: Array<String>) {
    runApplication<BffApplication>(*args)
}

// Match the ECMAScript whitespace set used by the OpenAPI string patterns.
private val nonWhitespace =
    Regex("""[^\u0009-\u000D\u0020\u00A0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]""")

/**
 * Describes a role that a visitor can select in the demo.
 *
 * @property id stable identifier used across demo requests.
 * @property label role name shown in the browser.
 * @property kind role category from the API contract.
 */
data class DemoRole(val id: String, val label: String, val kind: String) {
    init {
        require(nonWhitespace.containsMatchIn(id)) {
            "A demo role ID must contain a non-whitespace character."
        }
        require(nonWhitespace.containsMatchIn(label)) {
            "A demo role label must contain a non-whitespace character."
        }
    }
}

/**
 * Lists the available administrator and student demo roles.
 *
 * @property administrator the role that manages courses.
 * @param students the student roles supplied by the caller.
 */
class DemoRoleDirectory(val administrator: DemoRole, students: List<DemoRole>) {
    /** The immutable snapshot of student roles in display order. */
    val students: List<DemoRole> = java.util.List.copyOf(students)

    init {
        val ids = mutableSetOf(administrator.id)
        require(this.students.all { ids.add(it.id) }) {
            "Demo role IDs must be unique across the directory."
        }
    }
}

/** Serves the directory used by the demo role selector. */
@RestController
class DemoDirectoryController {
    private val directory =
        DemoRoleDirectory(
            administrator =
                DemoRole("29807e59-c312-49d1-9654-e3c995ed066f", "Administrator", "administrator"),
            students =
                listOf(
                    DemoRole("3dd449cf-25d6-4b78-bb71-90e7f46419c2", "Maya Chen", "student"),
                    DemoRole("f6dfcd57-f874-48ee-b85b-1f0965e7f09a", "Alex Rivera", "student"),
                ),
        )

    /** Returns the administrator and student roles available in the demo. */
    @GetMapping("/api/demo-roles", produces = [MediaType.APPLICATION_JSON_VALUE])
    fun listDemoRoles(): DemoRoleDirectory = directory
}
