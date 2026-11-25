"""Exercise Kotlin quality gates with positive and negative controls in disposable copies."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SETS = {
    "bff": ("main", "courses.bff"),
    "fixtures": ("testFixtures", "courses.fixtures"),
}
PUBLICATION = "dokkaGeneratePublicationHtml"


def run(root, command):
    return subprocess.run(
        command,
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        timeout=300,
    )


def gradle(root, *tasks):
    return run(
        root, ["./gradlew", "--console=plain", "--no-configuration-cache", *tasks]
    )


def source_dir(root, module):
    source_set, package = SOURCE_SETS[module]
    return root / module / "src" / source_set / "kotlin" / package.replace(".", "/")


def kdoc_sections(source):
    before, _, rest = source.partition(b"/**\n")
    comment, _, after = rest.partition(b"\n */")
    summary, details = comment.split(b"\n *\n", 1)
    words = b" ".join(line.removeprefix(b" * ") for line in summary.splitlines())
    return before, words, details, after


class KotlinQualityTest(unittest.TestCase):
    def setUp(self):
        workspace = self.enterContext(
            tempfile.TemporaryDirectory(prefix="kotlin-quality-")
        )
        self.root = Path(workspace) / "project"
        shutil.copytree(
            ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git",
                ".gradle",
                ".kotlin",
                ".codex",
                ".gsd",
                ".planning",
                ".venv",
                ".executor-*",
                "build",
                "dist",
                "node_modules",
                "__pycache__",
            ),
        )

    def require_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout)

    def require_gradle_failure(self, result, task):
        self.assertIn(f"> Task {task} FAILED", result.stdout, result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_format_comments(self):
        clean_tasks = (
            ":bff:ktfmtCheck",
            ":bff:detektComments",
            ":fixtures:ktfmtCheck",
            ":fixtures:detektComments",
        )
        self.require_success(
            gradle(self.root, *clean_tasks, ":bff:kotlinQualityRuntime")
        )
        metadata = self.root / "bff/build/kotlin-quality/commands.json"
        commands = json.loads(metadata.read_text(encoding="utf-8"))

        specimen = self.root / "probe/kdoc/Specimen.kt"
        candidate = source_dir(self.root, "bff") / "KdocFormatWitness.kt"
        original = specimen.read_bytes()
        candidate.write_bytes(original)
        bad_format = gradle(self.root, ":bff:ktfmtCheck")
        self.require_gradle_failure(bad_format, ":bff:ktfmtCheck")
        reported_path = re.escape(str(candidate.relative_to(self.root)))
        self.assertRegex(
            bad_format.stdout, rf"(?m)^.*{reported_path}$", bad_format.stdout
        )
        self.assertIn("non-zero exit value 1", bad_format.stdout)
        self.assertEqual(candidate.read_bytes(), original)
        print(
            "ktfmtCheck reported KdocFormatWitness.kt and left its bytes unchanged (CLI exit 1)."
        )

        format_candidate = [*commands["ktfmt"], str(candidate)]
        self.require_success(run(self.root, format_candidate))
        first = candidate.read_bytes()
        self.assertNotEqual(original, first)
        self.assertEqual(kdoc_sections(original), kdoc_sections(first))
        self.require_success(run(self.root, format_candidate))
        self.assertEqual(candidate.read_bytes(), first)
        self.require_success(gradle(self.root, ":bff:ktfmtCheck"))
        candidate.unlink()

        production = source_dir(self.root, "bff") / "KdocCommentsWitness.kt"
        production.write_text("package courses.bff\n", encoding="utf-8")
        fixture = source_dir(self.root, "fixtures") / "KdocCommentsWitness.kt"
        fixture.write_text("package courses.fixtures\n", encoding="utf-8")
        script = self.root / "bff/build.gradle.kts"
        sources = {
            path: path.read_text(encoding="utf-8")
            for path in (production, fixture, script)
        }
        for path, source in sources.items():
            path.write_text(
                source
                + "\n/** Returns a quality witness */\nfun kdocCommentsWitness(): Int = 1\n",
                encoding="utf-8",
            )

        detekt = [
            *commands["detekt"],
            "--input",
            ",".join(str(path) for path in sources),
        ]
        cli = run(self.root, detekt)
        self.assertEqual(cli.returncode, 2, cli.stdout)
        self.assert_comment_findings(cli.stdout, sources)

        bad_comments = gradle(
            self.root, ":bff:detektComments", ":fixtures:detektComments", "--continue"
        )
        self.require_gradle_failure(bad_comments, ":bff:detektComments")
        self.require_gradle_failure(bad_comments, ":fixtures:detektComments")
        self.assert_comment_findings(bad_comments.stdout, sources)
        self.assertIn("non-zero exit value 2", bad_comments.stdout)

        invalid_config = self.root / "config/detekt/invalid.yml"
        invalid_config.write_text(
            "unrecognizedRuleSet:\n  active: true\n", encoding="utf-8"
        )
        invalid = run(
            self.root, [*detekt[:4], "--config", str(invalid_config), *detekt[-2:]]
        )
        self.assertEqual(invalid.returncode, 3, invalid.stdout)
        self.assertIn("unrecognizedRuleSet", invalid.stdout)
        self.assertNotIn("[EndOfSentenceFormat]", invalid.stdout)

        script.write_text(sources[script], encoding="utf-8")
        production.unlink()
        fixture.unlink()
        invalid_config.unlink()
        self.require_success(gradle(self.root, *clean_tasks))

    def assert_comment_findings(self, output, sources):
        for source in sources:
            self.assertRegex(
                output,
                rf"(?m)^.*{re.escape(str(source.relative_to(self.root)))}:\d+:\d+: "
                r"The first sentence of this KDoc does not end with the correct punctuation\. "
                r"\[EndOfSentenceFormat\]$",
                output,
            )

    def test_publication(self):
        tasks = [f":{module}:{PUBLICATION}" for module in SOURCE_SETS]
        dry_run = gradle(self.root, ":bff:check", ":fixtures:check", "--dry-run")
        self.require_success(dry_run)
        for task in tasks:
            self.assertIn(f"{task} SKIPPED", dry_run.stdout, dry_run.stdout)

        clean = gradle(self.root, *tasks)
        self.require_success(clean)
        self.assertNotIn("Undocumented:", clean.stdout)
        for module in SOURCE_SETS:
            index = self.root / module / "build/dokka/html/index.html"
            self.assertIn("</html>", index.read_text(encoding="utf-8"))

        witnesses = {}
        for module, (_, package) in SOURCE_SETS.items():
            path = source_dir(self.root, module) / "KdocPublicationWitness.kt"
            declaration = 'fun kdocPublicationWitness(): String = "quality witness"\n'
            path.write_text(f"package {package}\n\n{declaration}", encoding="utf-8")
            witnesses[path] = (package, declaration)

        bad = gradle(self.root, *tasks, "--continue")
        for module, (_, package) in SOURCE_SETS.items():
            diagnostic = f"[:{module}:{PUBLICATION}] Undocumented: {package}/kdocPublicationWitness/#/"
            self.assertIn(diagnostic, bad.stdout, bad.stdout)
            print(diagnostic)
        self.assertNotEqual(
            bad.returncode,
            0,
            f"Dokka emitted the witness warning but exited zero.\n{bad.stdout}",
        )
        for task in tasks:
            self.require_gradle_failure(bad, task)
        self.assertIn("warningCount=1 and errorCount=0", bad.stdout, bad.stdout)

        description = "Returns the value used to verify API documentation."
        for path, (package, declaration) in witnesses.items():
            path.write_text(
                f"package {package}\n\n/** {description} */\n{declaration}",
                encoding="utf-8",
            )
        repaired = gradle(self.root, *tasks)
        self.require_success(repaired)
        self.assertNotIn("Undocumented:", repaired.stdout)
        for module in SOURCE_SETS:
            html = self.root / module / "build/dokka/html"
            pages = list(html.rglob("kdoc-publication-witness.html"))
            self.assertEqual(len(pages), 1, f"Expected a witness page in {html}")
            self.assertIn(description, pages[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("format-comments", "publication"))
    args = parser.parse_args()
    unittest.main(
        argv=[__file__, f"KotlinQualityTest.test_{args.mode.replace('-', '_')}"]
    )
