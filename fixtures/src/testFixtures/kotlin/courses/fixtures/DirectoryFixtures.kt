package courses.fixtures

/**
 * Represents one entry in a test directory.
 *
 * @property id stable identifier expected by directory tests.
 * @property label role name expected by directory tests.
 * @property kind role category expected by directory tests.
 */
data class DirectoryRole(val id: String, val label: String, val kind: String)

/**
 * Provides the expected directory for the selected test case.
 *
 * @property administrator the administrator entry.
 * @property students the student entries in expected response order.
 */
data class DirectorySample(val administrator: DirectoryRole, val students: List<DirectoryRole>) {
    /** Lists the administrator followed by the configured students. */
    val roles: List<DirectoryRole>
        get() = listOf(administrator) + students

    /**
     * Returns a sample containing the first [count] students.
     *
     * @param count student count from zero through the size of [students].
     */
    fun withStudentCount(count: Int): DirectorySample {
        require(count in 0..students.size) { "Expected between zero and ${students.size} students" }
        return copy(students = students.take(count))
    }
}

/** Supplies shared directory expectations for the BFF test suites. */
object DirectoryFixtures {
    /** Provides the complete directory used by the default demo. */
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
