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

/**
 * Describes a role that a visitor can select in the demo.
 *
 * @property id stable identifier used across demo requests.
 * @property label role name shown in the browser.
 * @property kind role category from the API contract.
 */
data class DemoRole(val id: String, val label: String, val kind: String)

/**
 * Lists the available administrator and student demo roles.
 *
 * @property administrator the role that manages courses.
 * @property students the student roles in display order.
 */
data class DemoRoleDirectory(val administrator: DemoRole, val students: List<DemoRole>)

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
