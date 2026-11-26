package courses.bff

import courses.fixtures.DirectoryFixtures
import io.kotest.common.ExperimentalKotest
import io.kotest.matchers.shouldBe
import io.kotest.property.Arb
import io.kotest.property.PropTestConfig
import io.kotest.property.arbitrary.int
import io.kotest.property.checkAll
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class DirectoryUnitTest {
    private val administrator = DemoRole("admin", "Administrator", "administrator")
    private val maya = DemoRole("maya", "Maya Chen", "student")
    private val alex = DemoRole("alex", "Alex Rivera", "student")
    private val blankValues = listOf("", " \t", "\u00A0", "\uFEFF")

    @Test
    fun `role identifiers cannot be blank`() {
        for (blank in blankValues) {
            assertThrows<IllegalArgumentException> { maya.copy(id = blank) }
        }
    }

    @Test
    fun `role labels cannot be blank`() {
        for (blank in blankValues) {
            assertThrows<IllegalArgumentException> { maya.copy(label = blank) }
        }
    }

    @Test
    fun `role strings keep content and surrounding whitespace`() {
        val role = maya.copy(id = "\u0085", label = " \u00A0Maya Chen \t")

        role.id shouldBe "\u0085"
        role.label shouldBe " \u00A0Maya Chen \t"
    }

    @Test
    fun `students cannot share an identifier`() {
        assertThrows<IllegalArgumentException> {
            DemoRoleDirectory(administrator, listOf(maya, alex.copy(id = maya.id)))
        }
    }

    @Test
    fun `students cannot use the administrator identifier`() {
        assertThrows<IllegalArgumentException> {
            DemoRoleDirectory(administrator, listOf(maya.copy(id = administrator.id)))
        }
    }

    @Test
    fun `directory identifiers are case sensitive`() {
        val student = maya.copy(id = "ADMIN")
        val directory = DemoRoleDirectory(administrator, listOf(student))

        directory.students shouldBe listOf(student)
    }

    @Test
    fun `directory keeps an unmodifiable snapshot of the student order`() {
        val students = mutableListOf(alex, maya)
        val directory = DemoRoleDirectory(administrator, students)

        students.clear()

        directory.students shouldBe listOf(alex, maya)
        assertThrows<UnsupportedOperationException> {
            (directory.students as MutableList<DemoRole>).clear()
        }
    }

    @OptIn(ExperimentalKotest::class)
    @Test
    fun `demo roles have identifiers and labels`() = runBlocking {
        val directory = DemoDirectoryController().listDemoRoles()
        val roles = listOf(directory.administrator) + directory.students
        val seed = 20261125L
        val iterations = 32
        val config = PropTestConfig(seed = seed, iterations = iterations)
        var checks = 0

        checkAll(config, Arb.int(roles.indices)) { index ->
            val role = roles[index]
            role.id.isNotBlank() shouldBe true
            role.label.isNotBlank() shouldBe true
            checks += 1
        }

        checks shouldBe iterations
        println("DIRECTORY_PROPERTY seed=$seed checks=$checks")
    }

    @OptIn(ExperimentalKotest::class)
    @Test
    fun `directory identifiers are unique for each sample size`() = runBlocking {
        val seed = 20261126L
        val iterations = 32
        val config = PropTestConfig(seed = seed, iterations = iterations)
        val sizes = mutableSetOf<Int>()
        var checks = 0

        checkAll(config, Arb.int(0..2)) { count ->
            val directory = DirectoryFixtures.defaultDirectory.withStudentCount(count)
            directory.students.size shouldBe count
            val ids = directory.roles.map { it.id }
            ids.distinct() shouldBe ids
            sizes += count
            checks += 1
        }

        sizes shouldBe setOf(0, 1, 2)
        checks shouldBe iterations
        println("DIRECTORY_FIXTURE_PROPERTY seed=$seed checks=$checks sizes=${sizes.sorted()}")
    }
}
