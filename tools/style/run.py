"""Apply one repository style policy to the tracked checkout or Git index."""

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from contextlib import redirect_stdout
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

POLICY = "tools/style/policy.json"
DETEKT_CONFIG = "config/detekt/comments.yml"
DEFAULT_RUNTIME = ".gradle/style/commands.json"
SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+"


class StyleError(Exception):
    """A failed check or a tool that could not safely run."""


def command(args, cwd, *, data=None, env=None):
    result = subprocess.run(
        args,
        check=False,
        cwd=cwd,
        input=data,
        capture_output=True,
        env=env,
        timeout=120,
    )
    if result.returncode:
        output = (
            (result.stderr + result.stdout).decode("utf-8", errors="replace").strip()
        )
        raise StyleError(
            f"{Path(args[0]).name} exited {result.returncode}\n{output}".rstrip()
        )
    return result.stdout


def git(root, *args, data=None, index=None):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    return command(["git", *args], root, data=data, env=env)


def git_paths(output):
    return [os.fsdecode(name) for name in output.split(b"\0") if name]


@dataclass(frozen=True)
class Entry:
    mode: str
    oid: str


def index_entries(root, index=None):
    entries = {}
    for record in git_paths(git(root, "ls-files", "--stage", "-z", index=index)):
        fields, path = record.split("\t", 1)
        mode, oid, stage = fields.split()
        if stage != "0":
            raise StyleError(f"Unmerged index entry {path!r}")
        if mode not in {"100644", "100755"}:
            raise StyleError(f"Unsupported mode {mode} for {path!r}")
        entries[path] = Entry(mode, oid)
    return entries


def staged_paths(root, index=None):
    return git_paths(
        git(root, "diff", "--cached", "--name-only", "--no-renames", "-z", index=index)
    )


def regular_file(root, path):
    target = root / path
    if target.resolve() != target:
        raise StyleError(f"Expected a regular file within the checkout for {path!r}")
    if not stat.S_ISREG(target.stat().st_mode):
        raise StyleError(f"Expected a regular file for {path!r}")
    return target


def materialize(root, snapshot, entries, *, staged):
    for path, entry in entries.items():
        target = snapshot / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if staged:
            content = git(root, "cat-file", "blob", entry.oid)
            mode = entry.mode
        else:
            source = regular_file(root, path)
            content = source.read_bytes()
            mode = "100755" if source.stat().st_mode & stat.S_IXUSR else "100644"
        target.write_bytes(content)
        if mode == "100755":
            target.chmod(0o755)


def json_document(content):
    def unique_members(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise StyleError(f"Duplicate JSON member {key!r}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise StyleError(f"Invalid JSON constant {value!r}")

    return json.loads(
        content, object_pairs_hook=unique_members, parse_constant=invalid_constant
    )


def text_format(data, *, preserve_lines=False):
    text = data.decode("utf-8")
    if "\0" in text:
        raise StyleError("Text contains a NUL byte")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if preserve_lines:
        return (text + "\n" if text and not text.endswith("\n") else text).encode()
    lines = "\n".join(line.rstrip(" \t") for line in text.split("\n")).rstrip("\n")
    return (lines + "\n" if lines else "").encode()


def validate_lock(snapshot, path, content):
    lock = json_document(content)
    manifest = json_document((snapshot / path).with_name("package.json").read_bytes())
    if lock.get("lockfileVersion") not in {3, 4} or not isinstance(
        lock.get("packages"), dict
    ):
        raise StyleError("Expected an npm lockfile with a version 3 or 4 package graph")
    packages = lock["packages"]
    root_package = packages[""]
    for field in (
        "name",
        "version",
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    ):
        if manifest.get(field) != root_package.get(field):
            raise StyleError(f"npm lock disagrees with package.json for {field}")
    for name, package in packages.items():
        if name == "" or package.get("inBundle"):
            continue
        if not re.fullmatch(
            r"https://registry\.npmjs\.org/.+\.tgz", package.get("resolved", "")
        ):
            raise StyleError(f"Expected a registry tarball for {name!r}")
        if not re.fullmatch(
            r"sha512-[A-Za-z0-9+/]{86}==", package.get("integrity", "")
        ):
            raise StyleError(f"Expected SHA-512 integrity for {name!r}")


class Policy:
    def __init__(self, snapshot, runtime, scratch):
        self.snapshot = snapshot
        self.runtime = runtime
        self.rules = json_document((snapshot / POLICY).read_bytes())
        options = self.rules["prettier"]
        supported = {
            "embeddedLanguageFormatting",
            "endOfLine",
            "printWidth",
            "tabWidth",
            "semi",
            "singleQuote",
        }
        if options.keys() - supported:
            raise StyleError("Unsupported option in the repository Prettier policy")
        self.prettier_config = scratch / "prettier.json"
        self.prettier_config.write_text(json.dumps(options), encoding="utf-8")
        self.independent_tools = {}

    def route(self, path):
        matches = [
            rule
            for rule in self.rules["rules"]
            if any(fnmatchcase(path, pattern) for pattern in rule["paths"])
            and not any(
                fnmatchcase(path, pattern) for pattern in rule.get("except", [])
            )
        ]
        if len(matches) > 1:
            ids = ", ".join(rule["id"] for rule in matches)
            raise StyleError(f"Ambiguous style rules for {path!r}: {ids}")
        rule = matches[0] if matches else self.rules["default"]
        return rule["id"], rule["reason"]

    def run(self, tool, *args, data=None, cwd=None):
        if self.runtime is None:
            raise StyleError("Style runtime missing. Run ./gradlew styleRuntime first.")
        return command([*self.runtime[tool], *args], cwd or self.snapshot, data=data)

    def cli(self, tool, *args, data):
        if tool not in self.independent_tools:
            pins = tomllib.loads(
                (self.snapshot / "mise.toml").read_text(encoding="utf-8")
            )
            expected = pins["tools"][tool]
            executable = shutil.which(tool)
            if not executable:
                raise StyleError(
                    f"{tool} {expected} is required. Run mise install {tool}."
                )
            observed = (
                command([executable, "--version"], self.snapshot).decode().strip()
            )
            if observed != f"{tool} {expected}":
                raise StyleError(
                    f"Expected {tool} {expected} from mise.toml, found {observed!r}"
                )
            self.independent_tools[tool] = executable
        env = dict(os.environ)
        env.pop("TAPLO_CONFIG", None)
        return command(
            [self.independent_tools[tool], *args], self.snapshot, data=data, env=env
        )

    def format(self, path, rule, data):
        if rule == "prettier":
            return self.run(
                "prettier",
                "--config",
                self.prettier_config,
                "--no-editorconfig",
                "--ignore-path",
                os.devnull,
                f"--stdin-filepath=./{path}",
                data=data,
            )
        if rule == "kotlin":
            return self.run("ktfmt", "-", data=data)
        if rule == "python":
            return self.cli(
                "ruff",
                "format",
                "--isolated",
                "--no-cache",
                "--stdin-filename",
                f"./{path}",
                "-",
                data=data,
            )
        if rule == "toml":
            return self.cli("taplo", "fmt", "--no-auto-config", "-", data=data)
        if rule in {"evidence", "shell", "text", "versions"}:
            return text_format(data, preserve_lines=rule == "evidence")
        if rule in {"wrapper", "npm-lock"}:
            return data
        raise StyleError(f"Unknown style rule {rule!r}")

    def lint(self, path, rule, content):
        if rule == "python":
            self.cli(
                "ruff",
                "check",
                "--isolated",
                "--no-cache",
                f"--select={self.rules['ruff']['select']}",
                f"--per-file-ignores={self.rules['ruff']['perFileIgnores']}",
                "--stdin-filename",
                f"./{path}",
                "-",
                data=content,
            )
        elif rule == "toml":
            self.cli(
                "taplo", "lint", "--no-schema", "--no-auto-config", "-", data=content
            )
        elif rule == "shell":
            command(["sh", "-n"], self.snapshot, data=content)
        elif rule == "npm-lock":
            validate_lock(self.snapshot, path, content)
        elif rule == "prettier" and path.endswith(".json"):
            json_document(content)
        elif rule == "versions":
            pattern = r"[1-9][0-9]*" if path == ".java-version" else SEMVER
            if not re.fullmatch(pattern + "\n", content.decode()):
                raise StyleError("Expected exactly one pinned version")
        elif rule == "wrapper":
            self.check_wrapper(path, content)

    def check_wrapper(self, path, content):
        wrapper = self.rules["wrapper"]
        if path == "gradle/wrapper/gradle-wrapper.properties":
            properties = dict(
                line.replace(r"\:", ":").split("=", 1)
                for line in content.decode().splitlines()
                if line and not line.startswith("#")
            )
            for key in ("distributionUrl", "distributionSha256Sum"):
                if properties.get(key) != wrapper[key]:
                    raise StyleError(f"Gradle wrapper {key} disagrees with policy")
            if properties.get("validateDistributionUrl") != "true":
                raise StyleError("Gradle wrapper must validate its distribution URL")
        else:
            mode = (
                "100755"
                if (self.snapshot / path).stat().st_mode & stat.S_IXUSR
                else "100644"
            )
            if (
                hashlib.sha256(content).hexdigest() != wrapper[path]["sha256"]
                or mode != wrapper[path]["mode"]
            ):
                raise StyleError(
                    "Gradle wrapper checksum or executable mode disagrees with policy"
                )

    def lint_kotlin(self, paths, scratch):
        lint_files = []
        for number, path in enumerate(paths):
            # detekt parses --input as a comma-delimited list.
            lint_file = (
                scratch / "detekt" / str(number) / Path(path).name.replace(",", "_")
            )
            lint_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.snapshot / path, lint_file)
            lint_files.append(lint_file)
        try:
            self.run(
                "detekt",
                "--config",
                self.snapshot / DETEKT_CONFIG,
                "--input",
                ",".join(map(str, lint_files)),
            )
        except StyleError as error:
            message = str(error)
            for path, filename in zip(paths, lint_files, strict=True):
                message = message.replace(str(filename), repr(path))
            raise StyleError(message) from error

    def lint_fsd(self):
        if self.runtime is None:
            raise StyleError("Style runtime missing. Run ./gradlew styleRuntime first.")
        web = self.snapshot / "web"
        (web / "node_modules").symlink_to(
            self.runtime["webModules"], target_is_directory=True
        )
        self.run("steiger", "./src", "--config", "steiger.config.ts", cwd=web)


@dataclass(frozen=True)
class Formatting:
    after: bytes
    rule: str


def evaluate(policy, entries, selected, scratch):
    routes = {path: policy.route(path)[0] for path in entries}
    selected = set(selected)
    targets = selected.intersection(entries)
    targets.update(
        path
        for path in routes
        if routes[path] == "npm-lock"
        and str(Path(path).with_name("package.json")) in selected
    )
    changed = {}
    failures = []
    for path in sorted(targets):
        rule = routes[path]
        target = policy.snapshot / path
        before = target.read_bytes()
        try:
            after = policy.format(path, rule, before)
            if after != before:
                if rule not in {"text", "evidence", "shell", "versions"}:
                    after.decode("utf-8")
                    if b"\0" in after or (before.strip() and not after.strip()):
                        raise StyleError("Formatter returned invalid text")
                target.write_bytes(after)
                changed[path] = Formatting(after, rule)
        except (StyleError, ValueError, OSError, subprocess.TimeoutExpired) as error:
            failures.append(f"{path!r} [{rule}] {error}")
    if failures:
        return changed, failures

    for path in sorted(targets):
        rule = routes[path]
        try:
            policy.lint(path, rule, (policy.snapshot / path).read_bytes())
        except (
            StyleError,
            ValueError,
            KeyError,
            AttributeError,
            OSError,
            subprocess.TimeoutExpired,
        ) as error:
            failures.append(f"{path!r} [{rule}] {error}")
    kotlin = sorted(
        path
        for path, rule in routes.items()
        if rule == "kotlin" and (path in targets or DETEKT_CONFIG in selected)
    )
    fsd = any(path.startswith("web/src/") for path in entries) and any(
        path.startswith("web/src/")
        or path
        in {
            "web/steiger.config.ts",
            "web/tsconfig.json",
            "web/package.json",
            "web/package-lock.json",
        }
        for path in selected
    )
    for tool, check in (
        ("detekt", lambda: policy.lint_kotlin(kotlin, scratch) if kotlin else None),
        ("steiger", lambda: policy.lint_fsd() if fsd else None),
    ):
        try:
            check()
        except (StyleError, OSError, subprocess.TimeoutExpired) as error:
            failures.append(f"[{tool}] {error}")
    return changed, failures


def inspect(root, runtime, *, staged=False, inventory=False):
    entries = index_entries(root)
    selected = staged_paths(root) if staged else entries
    if not selected:
        return 0
    with tempfile.TemporaryDirectory(prefix="repository-style-") as temporary:
        scratch = Path(temporary).resolve()
        snapshot = scratch / "tree"
        materialize(root, snapshot, entries, staged=staged)
        policy = Policy(snapshot, runtime, scratch)
        if inventory:
            for path in sorted(entries):
                rule, reason = policy.route(path)
                print(f"{json.dumps(path)}\t{rule}\t{reason}")
            return 0
        changed, failures = evaluate(policy, entries, selected, scratch)
        for path, delta in changed.items():
            print(f"{json.dumps(path)} [{delta.rule}] needs formatting")
        for failure in failures:
            print(failure, file=sys.stderr)
        return int(bool(changed or failures))


def read_version(path):
    with path.open("rb") as stream:
        data = stream.read()
        info = os.fstat(stream.fileno())
    return data, (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def publish_index(index, original, candidate):
    lock = index.with_name(index.name + ".lock")
    try:
        stream = lock.open("xb")
    except FileExistsError as error:
        raise StyleError(
            f"Git index is locked at {lock}. Retry after the writer finishes."
        ) from error
    published = False
    with stream:
        lock_info = os.fstat(stream.fileno())
        try:
            if not index.is_file() or read_version(index) != original:
                raise StyleError(
                    "Git index changed during style checks. Retry the commit."
                )
            if candidate is not None:
                os.fchmod(stream.fileno(), stat.S_IMODE(original[1][2]))
                stream.write(candidate.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
                lock.replace(index)
                published = True
        finally:
            if not published and lock.exists():
                current = lock.lstat()
                if (current.st_dev, current.st_ino) == (
                    lock_info.st_dev,
                    lock_info.st_ino,
                ):
                    lock.unlink()


def update_candidate(root, candidate, entries, changes):
    records = []
    for path, delta in changes.items():
        oid = git(root, "hash-object", "-w", "--stdin", data=delta.after).strip()
        records.append(
            entries[path].mode.encode() + b" " + oid + b"\t" + os.fsencode(path) + b"\0"
        )
    git(
        root,
        "-c",
        "core.splitIndex=false",
        "-c",
        "core.fsmonitor=false",
        "update-index",
        "-z",
        "--index-info",
        data=b"".join(records),
        index=candidate,
    )


def format_staged(root, runtime):
    index_path = git(root, "rev-parse", "--path-format=absolute", "--git-path", "index")
    index = Path(os.fsdecode(index_path.removesuffix(b"\n")))
    if not index.exists():
        return 0
    original = read_version(index)
    with tempfile.TemporaryDirectory(prefix="repository-style-candidate-") as temporary:
        scratch = Path(temporary).resolve()
        candidate = scratch / "index"
        candidate.write_bytes(original[0])
        entries = index_entries(root, candidate)
        selected = staged_paths(root, candidate)
        if not selected:
            return 0
        snapshot = scratch / "tree"
        materialize(root, snapshot, entries, staged=True)
        policy = Policy(snapshot, runtime, scratch)
        changed, failures = evaluate(policy, entries, selected, scratch)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1
        if changed:
            # Git names the temporary index after its own PID. The installed
            # hook execs this driver, so that Git process is also our parent.
            if index.name == f"next-index-{os.getppid()}.lock":
                git_dir = git(root, "rev-parse", "--absolute-git-dir")
                if index.parent == Path(os.fsdecode(git_dir.removesuffix(b"\n"))):
                    raise StyleError(
                        "A path-limited commit needs formatting. "
                        "Stage the intended paths with git add -- <paths>, "
                        "review git diff --cached, then run git commit without paths."
                    )
            update_candidate(root, candidate, entries, changed)
        publish_index(index, original, candidate if changed else None)

    for path, delta in changed.items():
        print(f"{json.dumps(path)} [{delta.rule}] formatted staged content")
    if changed:
        print(
            "Worktree files preserved. Review unstaged changes with git diff -- <path>."
        )
    return 0


def self_test(root, runtime):
    fixtures = {
        "One.kt": b"/** Keeps the Kotlin documentation. */\nfun one( ): Int=1\n",
        "space and quote '.md": b"#  Sample\n\n-   one\n-   two\n",
    }
    with tempfile.TemporaryDirectory(prefix="style-parity-") as temporary:
        fixture = Path(temporary).resolve()
        git(fixture, "init", "-q")
        for path in (POLICY, DETEKT_CONFIG):
            target = fixture / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, target)
        for path, content in fixtures.items():
            (fixture / path).write_bytes(content)
        git(fixture, "add", "--", POLICY, DETEKT_CONFIG, *fixtures)
        for staged in (True, False):
            with redirect_stdout(io.StringIO()) as reports:
                status = inspect(fixture, runtime, staged=staged)
            if status != 1 or not all(
                f"{json.dumps(path)} [{rule}] needs formatting" in reports.getvalue()
                for path, rule in zip(fixtures, ("kotlin", "prettier"), strict=True)
            ):
                raise StyleError(
                    f"Expected Kotlin and Markdown differences: {reports.getvalue()}"
                )
        first = None
        for staged in (True, False):
            with tempfile.TemporaryDirectory(prefix="style-parity-snapshot-") as temp:
                scratch = Path(temp).resolve()
                snapshot = scratch / "tree"
                entries = index_entries(fixture)
                materialize(fixture, snapshot, entries, staged=staged)
                policy = Policy(snapshot, runtime, scratch)
                result, failures = evaluate(policy, entries, fixtures, scratch)
                if failures or result.keys() != fixtures.keys():
                    raise StyleError(
                        f"Expected both formatting differences, got {result.keys()} and {failures}"
                    )
                if first is not None and first != result:
                    raise StyleError(
                        "Staged and tracked snapshots produced different formatting"
                    )
                first = result
                again, failures = evaluate(policy, entries, fixtures, scratch)
                if again or failures:
                    raise StyleError(
                        f"Formatting is not idempotent: {again.keys()} {failures}"
                    )
                for path, content in fixtures.items():
                    if (fixture / path).read_bytes() != content or git(
                        fixture, "show", f":{path}"
                    ) != content:
                        raise StyleError(f"Check-only mode edited {path!r}")
    print("Staged and tracked formatting agree for Kotlin/KDoc and Markdown")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("check", "staged", "inventory", "self-test"):
        modes.add_argument(f"--{mode}", action="store_true")
    parser.add_argument("--runtime", type=Path)
    args = parser.parse_args()
    try:
        root = Path(
            os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel").rstrip(b"\n"))
        ).resolve()
        runtime_file = args.runtime or root / DEFAULT_RUNTIME
        runtime = (
            json_document(runtime_file.read_bytes()) if runtime_file.is_file() else None
        )
        if args.self_test:
            return self_test(root, runtime)
        if args.staged:
            return format_staged(root, runtime)
        return inspect(root, runtime, inventory=args.inventory)
    except (
        StyleError,
        OSError,
        ValueError,
        KeyError,
        subprocess.TimeoutExpired,
    ) as error:
        print(f"style: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
