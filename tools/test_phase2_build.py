"""Verify the Phase 2 build and runnable reader entry points."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase2BuildTest(unittest.TestCase):
    def test_site_smoke_is_a_public_verification_task(self):
        result = subprocess.run(
            ["./gradlew", "--console=plain", ":web:tasks", "--group", "verification"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        tasks = {line.partition(" - ")[0] for line in result.stdout.splitlines()}
        self.assertIn(
            "siteSmoke", tasks, "The runnable reader smoke must be discoverable"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
