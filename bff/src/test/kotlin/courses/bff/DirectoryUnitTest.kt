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

class DirectoryUnitTest {
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
