package probe

import io.kotest.matchers.shouldBe
import io.kotest.property.Arb
import io.kotest.property.PropTestConfig
import io.kotest.property.arbitrary.int
import io.kotest.property.checkAll
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class KotestInteropTest {
    @Test
    fun `Jupiter runs a seeded Kotest property`() = runBlocking {
        val seed = 20261124L
        val iterations = 32
        var checks = 0

        checkAll(PropTestConfig(seed = seed, iterations = iterations), Arb.int(-1000..1000)) { value ->
            value.toString().toInt() shouldBe value
            checks += 1
        }

        checks shouldBe iterations
        assertEquals(
            KotlinVersion.CURRENT.toString(),
            System.getProperty("probe.kotlinVersion"),
            "The worker Kotlin runtime must match the selected Kotlin version",
        )
        println("PROBE_KOTEST_WORKER $seed $checks ${System.getProperty("java.vendor")}|${Runtime.version()}|${System.getProperty("os.arch")}")
    }
}
