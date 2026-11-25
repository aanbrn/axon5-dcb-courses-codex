"""Verify repository style with disposable Git repositories and real commits."""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
HOOK = ".githooks/pre-commit"
POLICY = "tools/style/policy.json"
RUNTIME = "build/style/commands.json"
DRIVER = "tools/style/run.py"
DETEKT = "config/detekt/comments.yml"


class Checkout:
    def __init__(self, root):
        self.root = root
        self.env = dict(
            os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1"
        )
        self.env.pop("GIT_INDEX_FILE", None)
        self.git("init", "-q", "--initial-branch=fixture")
        self.git("config", "user.name", "Repository Style Fixture")
        self.git("config", "user.email", "style-fixture@example.test")
        self.git("config", "core.fileMode", "true")
        self.git("config", "core.autocrlf", "false")
        for path in (POLICY, RUNTIME, DRIVER, DETEKT, "mise.toml", HOOK):
            source = PROJECT / path
            if source.is_file():
                target = self.write(path, source.read_bytes())
                target.chmod(source.stat().st_mode)
        self.git("add", "--", POLICY, DETEKT, "mise.toml")
        self.git("commit", "-qm", "Baseline policy")
        self.git("config", "--local", "core.hooksPath", ".githooks")

    def git(self, *args, expected=0, extra_env=None):
        return self.run(["git", *args], expected=expected, extra_env=extra_env)

    def run(self, args, *, expected=0, extra_env=None):
        result = subprocess.run(
            args,
            cwd=self.root,
            env=self.env | (extra_env or {}),
            capture_output=True,
            check=False,
            timeout=120,
        )
        if result.returncode != expected:
            raise AssertionError(
                f"{args!r}: expected exit {expected}, got {result.returncode}\n{result.stderr.decode(errors='replace')}\n{result.stdout.decode(errors='replace')}"
            )
        return result

    def hook(self, expected=0):
        return self.run([str(self.root / HOOK)], expected=expected)

    def write(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def stage(self, path, data):
        target = self.write(path, data)
        self.git("add", "--", path)
        return target

    def show(self, path, revision="HEAD"):
        return self.git("show", f"{revision}:{path}").stdout

    def set_prettier(self, program):
        runtime = json.loads((PROJECT / RUNTIME).read_bytes())
        runtime["prettier"] = [sys.executable, "-c", program, *runtime["prettier"]]
        self.write(RUNTIME, json.dumps(runtime).encode())


class HookTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="repository-hook-test-")
        self.addCleanup(temporary.cleanup)
        self.repo = Checkout(Path(temporary.name).resolve())
        self.index = self.repo.root / ".git/index"

    def test_commit_formats_staged_adjacent_edits_and_mode(self):
        repo = self.repo
        path = "deploy script.txt"
        tracked = repo.stage(path, b"first\nsecond\nthird\n")
        tracked.chmod(0o755)
        repo.git("add", "--", path)
        repo.git("commit", "-qm", "Baseline executable")
        repo.stage(path, b"first changed   \nsecond\nthird\n")
        repo.write(path, b"first changed   \nsecond unstaged   \nthird\n")
        repo.git("commit", "-qm", "Format staged executable")
        self.assertEqual(repo.show(path), b"first changed\nsecond\nthird\n")
        self.assertEqual(
            tracked.read_bytes(), b"first changed\nsecond unstaged   \nthird\n"
        )
        self.assertTrue(
            repo.git("ls-tree", "HEAD", "--", path).stdout.startswith(b"100755 ")
        )
        self.assertEqual(stat.S_IMODE(tracked.stat().st_mode), 0o755)

    def test_disjoint_and_overlapping_edits(self):
        repo = self.repo
        disjoint = "disjoint.txt"
        overlap = "overlap.txt"
        for path in (disjoint, overlap):
            repo.stage(path, b"first\nsecond\nthird\n")
        repo.git("commit", "-qm", "Baseline edited files")
        for path in (disjoint, overlap):
            repo.stage(path, b"staged first  \nsecond\nthird\n")
        repo.write(disjoint, b"staged first  \nsecond\nlocal third  \n")
        overlapping = repo.write(overlap, b"local first  \nsecond\nthird\n")
        overlap_before = overlapping.read_bytes()
        repo.git("commit", "-qm", "Format separate staged snapshots")
        for path in (disjoint, overlap):
            self.assertEqual(repo.show(path), b"staged first\nsecond\nthird\n")
        self.assertEqual(
            (repo.root / disjoint).read_bytes(),
            b"staged first\nsecond\nlocal third  \n",
        )
        self.assertEqual(overlapping.read_bytes(), overlap_before)

    def test_empty_rename_deletion_quoted_names_and_repeat(self):
        repo = self.repo
        repo.stage("origin.txt", b"source\n")
        repo.stage("delete.txt", b"removed\n")
        repo.git("commit", "-qm", "Baseline rename and removal")
        before = self.index.read_bytes()
        repo.hook()
        self.assertEqual(self.index.read_bytes(), before)
        path = "odd tab\tnewline\n \"quote' ;$(touch escaped).md"
        repo.git("mv", "--", "origin.txt", path)
        target = repo.stage(path, b"#  Changed\n\n-   item\n")
        repo.git("rm", "--", "delete.txt")
        repo.hook()
        reformatted = self.index.read_bytes()
        worktree = target.read_bytes()
        repo.hook()
        self.assertEqual(self.index.read_bytes(), reformatted)
        self.assertEqual(target.read_bytes(), worktree)
        repo.git("commit", "-qm", "Rename and delete")
        self.assertEqual(repo.show(path), b"# Changed\n\n- item\n")
        self.assertEqual(worktree, repo.show(path))
        self.assertEqual(
            repo.git("ls-tree", "HEAD", "--", "origin.txt", "delete.txt").stdout, b""
        )
        self.assertFalse((repo.root / "escaped").exists())

    def test_alternate_index_and_root_commit(self):
        repo = self.repo
        primary_index = self.index.read_bytes()
        env = {"GIT_INDEX_FILE": "alternate index"}
        repo.git("read-tree", "--empty", extra_env=env)
        repo.git("add", "--", POLICY, DETEKT, "mise.toml", extra_env=env)
        path = "alternate.txt"
        target = repo.write(path, b"alternate staged   \n")
        repo.git("add", "--", path, extra_env=env)
        repo.git("update-ref", "-d", "HEAD")
        repo.git("commit", "-qm", "Alternate-index initial commit", extra_env=env)
        self.assertEqual(repo.show(path), b"alternate staged\n")
        self.assertEqual(target.read_bytes(), b"alternate staged\n")
        self.assertEqual(self.index.read_bytes(), primary_index)

    def assert_aborted(self, diagnostic):
        repo = self.repo
        before = self.index.read_bytes()
        head = repo.git("rev-parse", "HEAD").stdout
        staged = repo.git("ls-files", "--stage", "-z").stdout
        changed = repo.git("diff", "--cached", "--name-only", "-z").stdout.split(b"\0")[
            :-1
        ]
        worktree = {
            os.fsdecode(path): (repo.root / os.fsdecode(path)).read_bytes()
            for path in changed
        }
        self.assertIn(diagnostic, repo.hook(expected=1).stderr)
        self.assertEqual(self.index.read_bytes(), before)
        result = repo.git("commit", "-qm", "Rejected candidate", expected=1)
        self.assertIn(diagnostic, result.stderr)
        self.assertEqual(repo.git("rev-parse", "HEAD").stdout, head)
        self.assertEqual(repo.git("ls-files", "--stage", "-z").stdout, staged)
        for path, data in worktree.items():
            self.assertEqual((repo.root / path).read_bytes(), data)

    def test_formatter_abort_and_invalid_output_preserve_every_path(self):
        repo = self.repo
        repo.stage("a.txt", b"text before tool failure   \n")
        for program, diagnostic in (
            (
                "import sys; print('formatter witness', file=sys.stderr); sys.exit(7)",
                b"formatter witness",
            ),
            (
                "import sys; sys.stdout.buffer.write(bytes([0]))",
                b"Formatter returned invalid text",
            ),
        ):
            with self.subTest(diagnostic=diagnostic):
                repo.set_prettier(program)
                repo.stage("z.md", b"#  Staged heading\n")
                repo.write("z.md", b"# local heading with text\n")
                self.assert_aborted(diagnostic)

    def test_lint_failure_preserves_candidate_and_worktree(self):
        repo = self.repo
        repo.stage("a.txt", b"pending format   \n")
        repo.stage("lint.py", b"import os\n\nvalue=  1\n")
        repo.write("lint.py", b"local_value = 2\n")
        self.assert_aborted(b"F401")

    def test_existing_lock_is_preserved(self):
        self.repo.stage("locked.txt", b"pending format   \n")
        lock = self.index.with_name("index.lock")
        lock.write_bytes(b"competing writer")
        before = self.index.read_bytes()
        result = self.repo.hook(expected=1)
        self.assertIn(b"index is locked", result.stderr)
        self.assertEqual(lock.read_bytes(), b"competing writer")
        self.assertEqual(self.index.read_bytes(), before)

    def test_linked_worktree_uses_its_own_index(self):
        repo = self.repo
        main_index = self.index.read_bytes()
        linked = repo.root / "linked checkout"
        repo.git("worktree", "add", "-qb", "linked", str(linked))
        for path in (RUNTIME, DRIVER, HOOK):
            target = linked / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo.root / path, target)
        path = "linked.txt"
        (linked / path).write_bytes(b"linked staged   \n")
        command = ["git", "-C", str(linked)]
        repo.run([*command, "add", "--", path])
        repo.run([*command, "commit", "-qm", "Format linked checkout"])
        self.assertEqual(
            repo.run([*command, "show", f"HEAD:{path}"]).stdout, b"linked staged\n"
        )
        self.assertEqual(self.index.read_bytes(), main_index)

    def test_unmerged_index_keeps_all_stages(self):
        repo = self.repo
        path = "conflict.txt"
        repo.stage(path, b"base\n")
        repo.git("commit", "-qm", "Base conflict")
        repo.git("branch", "other")
        repo.stage(path, b"first side\n")
        repo.git("commit", "-qm", "First side")
        repo.git("switch", "-q", "other")
        repo.stage(path, b"second side\n")
        repo.git("commit", "-qm", "Second side")
        repo.git("merge", "--no-edit", "fixture", expected=1)
        before = self.index.read_bytes()
        current = (repo.root / path).read_bytes()
        self.assertIn(b"Unmerged index entry", repo.hook(expected=1).stderr)
        self.assertEqual(self.index.read_bytes(), before)
        self.assertEqual((repo.root / path).read_bytes(), current)

    def test_competing_index_writer_keeps_its_update(self):
        repo = self.repo
        ready = repo.root / "formatter-ready"
        resume = repo.root / "formatter-resume"
        repo.set_prettier(
            f"import os, pathlib, sys, time; pathlib.Path({str(ready)!r}).touch()\n"
            f"for attempt in range(100):\n"
            f"    if pathlib.Path({str(resume)!r}).is_file(): break\n"
            "    time.sleep(0.05)\n"
            "else: sys.exit(71)\n"
            "os.execv(sys.argv[1], sys.argv[1:])\n"
        )
        path = "picked.md"
        current = repo.stage(path, b"#  Selected\n")
        with subprocess.Popen(
            [str(repo.root / HOOK)],
            cwd=repo.root,
            env=repo.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as hook:
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.03)
                self.assertTrue(
                    ready.exists(), "The formatter never reached the witness"
                )
                repo.stage("competing.txt", b"published by competing writer\n")
                competing = self.index.read_bytes()
            finally:
                resume.touch()
            stdout, stderr = hook.communicate(timeout=15)
        self.assertEqual(hook.returncode, 1, (stdout, stderr))
        self.assertIn(b"index changed during style checks", stderr)
        self.assertEqual(self.index.read_bytes(), competing)
        self.assertEqual(
            repo.show("competing.txt", ""), b"published by competing writer\n"
        )
        self.assertEqual(repo.show(path, ""), b"#  Selected\n")
        self.assertEqual(current.read_bytes(), b"#  Selected\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
