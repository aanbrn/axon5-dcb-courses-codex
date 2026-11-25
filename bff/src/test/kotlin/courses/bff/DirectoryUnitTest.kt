package courses.bff

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
}
