package courses.fixtures

data class DirectoryRole(val id: String, val label: String, val kind: String)

data class DirectorySample(val administrator: DirectoryRole, val students: List<DirectoryRole>) {
    val roles: List<DirectoryRole>
        get() = listOf(administrator) + students

    fun withStudentCount(count: Int): DirectorySample {
        require(count in 0..students.size) { "Expected between zero and ${students.size} students" }
        return copy(students = students.take(count))
    }
}

object DirectoryFixtures {
    val defaultDirectory =
        DirectorySample(
            administrator =
                DirectoryRole(
                    "29807e59-c312-49d1-9654-e3c995ed066f",
                    "Administrator",
                    "administrator",
                ),
            students =
                listOf(
                    DirectoryRole("3dd449cf-25d6-4b78-bb71-90e7f46419c2", "Maya Chen", "student"),
                    DirectoryRole("f6dfcd57-f874-48ee-b85b-1f0965e7f09a", "Alex Rivera", "student"),
                ),
        )
}
