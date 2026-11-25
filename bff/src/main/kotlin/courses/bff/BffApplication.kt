package courses.bff

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@SpringBootApplication class BffApplication

fun main(args: Array<String>) {
    runApplication<BffApplication>(*args)
}

data class DemoRole(val id: String, val label: String, val kind: String)

data class DemoRoleDirectory(val administrator: DemoRole, val students: List<DemoRole>)

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

    @GetMapping("/api/demo-roles", produces = [MediaType.APPLICATION_JSON_VALUE])
    fun listDemoRoles(): DemoRoleDirectory = directory
}
