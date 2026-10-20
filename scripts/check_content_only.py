#!/usr/bin/env python3
"""Fail when the plugin ships anything that runs code inside a consumer's Claude Code.

This repository is installed as a Claude Code plugin from its own marketplace. A plugin can
also carry hooks, mods (JavaScript or TypeScript event handlers that run inside the Claude Code
process with the user's privileges), MCP servers, LSP servers, monitors, workflows, and
executables, and an update to any of them arrives through the same channel as a change to a
skill. The value of this repository is that a reviewer can read all of it. This script holds
the plugin to skills and instruction documents.

The plugin root is the repository root, because every plugin entry in
`.claude-plugin/marketplace.json` has `"source": "./"`. Four checks run:

1. Paths. No file at a location Claude Code discovers by default in any plugin root the
   marketplace names, no file anywhere with a module or MCP bundle extension, and no symlink,
   since a symlink can point a discovered location at any file.
2. Manifests. `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` may use only
   the keys on an allowlist, and every plugin entry must source from a relative path. An
   allowlist rather than a denylist, so a key a future Claude Code release adds fails until
   someone has read what it does.
3. Skill content. No `hooks` or `shell` frontmatter key, and no dynamic-context shell
   injection, in any `SKILL.md` or any Markdown file under a `skills/` or `commands/` directory.
4. Validator. When `claude` is on `PATH`, `claude plugin validate` is run on a copy of the
   plugin and the run fails on any `hooks:` or `calls:` line or gating hook it reports. The
   validator reports a mod as `Validation passed`, so its exit status is not the signal. It also
   does not open a plugin's hooks module when it is given a marketplace file, so the copy
   carries a synthesized `plugin.json` in place of the marketplace file. When `claude` is
   absent or too old to report mods, this check is skipped and the script says so.

`agent-templates/` is exempt from the path and content checks on purpose. Its files are
copy-and-adapt definitions that Claude Code does not discover from the plugin root, and five of
them carry a `hooks:` frontmatter key that takes effect only after a consumer copies the file
into their own `.claude/agents/`.

Locations and fields are taken from the Claude Code documentation:

- https://code.claude.com/docs/en/plugins/manifest-reference (Standard layout, Fields)
- https://code.claude.com/docs/en/plugins/marketplace-reference (Plugin entries, Plugin sources)
- https://code.claude.com/docs/en/plugins/mods/reference (Files, Commands)
- https://code.claude.com/docs/en/plugins/mods/overview (Decide whether to trust a mod)
- https://code.claude.com/docs/en/skills (frontmatter fields, dynamic context injection)
- https://code.claude.com/docs/en/plugins/cli-reference (plugin validate)

Run it from anywhere; it needs only the standard library:

    python3 scripts/check_content_only.py
    python3 scripts/check_content_only.py --self-test
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

GIT = shutil.which("git") or "git"

REPO_ROOT = Path(__file__).resolve().parent.parent

# Local-only entries that git ignores or that are not content, skipped when git cannot list.
WALK_IGNORED = frozenset({".git", ".ruff_cache", ".venv", "__pycache__", "node_modules"})

# Directories Claude Code loads from the plugin root without being told to.
# https://code.claude.com/docs/en/plugins/manifest-reference#standard-layout
FORBIDDEN_ROOT_DIRS = {
    "hooks": "hooks/hooks.json is loaded as hook configuration and may name a mod module",
    "monitors": "monitors/monitors.json starts background shell commands in a session",
    "bin": "files in bin/ are put on the Bash tool's PATH",
    "workflows": "workflows/*.js files are JavaScript the plugin runs",
}

# Files Claude Code loads from the plugin root without being told to.
FORBIDDEN_ROOT_FILES = {
    ".mcp.json": "declares MCP servers the plugin starts",
    ".lsp.json": "declares language servers the plugin starts",
    "settings.json": "its subagentStatusLine key names a command to run",
}

# A hooks module is any of these. https://code.claude.com/docs/en/plugins/mods/reference#files
MODULE_SUFFIXES = frozenset({".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"})

# An MCP bundle is unpacked and run. https://code.claude.com/docs/en/plugins/manifest-reference
BUNDLE_SUFFIXES = frozenset({".mcpb", ".dxt"})

# Content metadata, plus `skills`, which only points at directories of SKILL.md files.
PLUGIN_KEYS = frozenset(
    {
        "$schema",
        "name",
        "displayName",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "metadata",
        "defaultEnabled",
        "category",
        "tags",
        "strict",
        "skills",
    }
)
# `source` is the one marketplace-entry key that is not plugin metadata.
ENTRY_KEYS = PLUGIN_KEYS | {"source"}
MARKETPLACE_KEYS = frozenset(
    {"$schema", "name", "description", "version", "owner", "metadata", "plugins"}
)

# Exempt from the path and content checks, so no manifest path may make it part of a plugin.
EXEMPT_DIR = "agent-templates"

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")
PLUGIN_MANIFEST_PATH = Path(".claude-plugin/plugin.json")

# A frontmatter key that registers hooks or selects the shell that injected commands run in.
FORBIDDEN_FRONTMATTER = {
    "hooks": "registers hooks that stay active for the rest of the session",
    "shell": "selects the shell for dynamic-context commands, which a skill must not use",
}
FRONTMATTER_KEY = re.compile(r"""^["']?([A-Za-z0-9_-]+)["']?\s*:""")
# Inline `!` plus a backtick runs a shell command when the skill loads, and so does a fenced
# block whose info string is `!`. https://code.claude.com/docs/en/skills
INLINE_INJECTION = re.compile(r"(?:^|\s)!`", re.MULTILINE)
FENCED_INJECTION = re.compile(r"^\s*(?:```|~~~)!", re.MULTILINE)

# `claude plugin validate` reports mods from v2.1.287, when mods became available.
MIN_VALIDATOR = (2, 1, 287)
VALIDATOR_FINDING = re.compile(r"\b(?:hooks|calls)\s*:")
VALIDATOR_TIMEOUT_SECONDS = 120


def list_files(root: Path) -> list[str]:
    """Return the repository-relative posix paths of every file git tracks or could add."""
    try:
        result = subprocess.run(  # noqa: S603
            [GIT, "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        result = None
    if result is not None and result.returncode == 0:
        return sorted(
            path
            for path in result.stdout.split("\0")
            if path and ((root / path).is_file() or (root / path).is_symlink())
        )
    files: list[str] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if WALK_IGNORED.intersection(relative.parts):
            continue
        if not (path.is_file() or path.is_symlink()):
            continue
        files.append(relative.as_posix())
    return sorted(files)


def plugin_roots(root: Path) -> list[str]:
    """Return every plugin root the marketplace names, as a posix prefix, `""` for the root."""
    manifest, _ = load_json(root / MARKETPLACE_PATH, str(MARKETPLACE_PATH))
    plugins = manifest.get("plugins") if isinstance(manifest, dict) else None
    roots = {""}
    for entry in plugins if isinstance(plugins, list) else []:
        source = entry.get("source") if isinstance(entry, dict) else None
        if isinstance(source, str) and source.startswith("."):
            relative = Path(source).as_posix().strip("/")
            roots.add("" if relative in {".", ""} else relative.removeprefix("./") + "/")
    return sorted(roots)


def check_paths(root: Path, files: list[str]) -> list[str]:
    """Check that no file sits at a discovered location or carries a code-bearing extension."""
    errors: list[str] = []
    roots = plugin_roots(root)
    for path in files:
        # Lower-cased because a case-insensitive filesystem opens `Hooks/` as `hooks/`.
        lowered = path.lower()
        if lowered.split("/")[0] == EXEMPT_DIR:
            continue
        if (root / path).is_symlink():
            errors.append(f"{path}: a symlink can point a discovered location at any file")
        for prefix in roots:
            if not lowered.startswith(prefix.lower()):
                continue
            parts = lowered.removeprefix(prefix.lower()).split("/")
            if len(parts) > 1 and parts[0] in FORBIDDEN_ROOT_DIRS:
                reason = FORBIDDEN_ROOT_DIRS[parts[0]]
                errors.append(f"{path}: {parts[0]}/ is not allowed in a plugin root, {reason}")
            elif len(parts) == 1 and parts[0] in FORBIDDEN_ROOT_FILES:
                errors.append(f"{path}: not allowed, {FORBIDDEN_ROOT_FILES[parts[0]]}")
        suffix = Path(path).suffix.lower()
        if suffix in MODULE_SUFFIXES:
            errors.append(f"{path}: a {suffix} file is a candidate hooks module")
        elif suffix in BUNDLE_SUFFIXES:
            errors.append(f"{path}: a {suffix} file is an MCP bundle Claude Code unpacks and runs")
    return errors


def load_json(path: Path, label: str) -> tuple[object, list[str]]:
    """Return the parsed JSON at path, or an error when it cannot be read."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{label}: cannot be read as JSON: {exc}"]


def check_keys(label: str, value: object, allowed: frozenset[str]) -> list[str]:
    """Report every key of a manifest object that is not on the allowlist."""
    if not isinstance(value, dict):
        return [f"{label}: must be a JSON object"]
    return [
        f"{label}: key {key!r} is not on the content-only allowlist, and it may declare code to "
        "run or a plugin to install"
        for key in sorted(set(value) - allowed)
    ]


def manifest_path_errors(label: str, key: str, value: object) -> list[str]:
    """Reject a manifest path that leaves the marketplace root or reaches the exempt directory."""
    errors: list[str] = []
    for item in value if isinstance(value, list) else [value]:
        if not isinstance(item, str):
            continue
        parts = [part for part in Path(item).parts if part != "."]
        if ".." in parts:
            errors.append(f"{label}: {key} {item!r} leaves the marketplace root")
        elif parts and parts[0].lower() == EXEMPT_DIR:
            errors.append(f"{label}: {key} {item!r} reaches {EXEMPT_DIR}/, which the gate exempts")
    return errors


def check_manifests(root: Path) -> list[str]:
    """Check the marketplace and plugin manifests against the key and source allowlists."""
    errors: list[str] = []
    marketplace_path = root / MARKETPLACE_PATH
    if marketplace_path.is_file():
        manifest, load_errors = load_json(marketplace_path, str(MARKETPLACE_PATH))
        errors += load_errors
        errors += check_keys(str(MARKETPLACE_PATH), manifest, MARKETPLACE_KEYS) if manifest else []
        plugins = manifest.get("plugins") if isinstance(manifest, dict) else None
        for index, entry in enumerate(plugins if isinstance(plugins, list) else []):
            label = f"{MARKETPLACE_PATH}: plugins[{index}]"
            errors += check_keys(label, entry, ENTRY_KEYS)
            source = entry.get("source") if isinstance(entry, dict) else None
            errors += manifest_path_errors(label, "source", source)
            if isinstance(entry, dict):
                errors += manifest_path_errors(label, "skills", entry.get("skills"))
            if not (isinstance(source, str) and source.startswith(".")):
                errors.append(
                    f"{label}: source must be a relative path, since any other source type "
                    "fetches code from outside this repository or runs a command to find it"
                )
    for prefix in plugin_roots(root):
        label = f"{prefix}{PLUGIN_MANIFEST_PATH.as_posix()}"
        if (root / label).is_file():
            manifest, load_errors = load_json(root / label, label)
            errors += load_errors
            errors += check_keys(label, manifest, PLUGIN_KEYS) if manifest else []
    return errors


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return the top-level frontmatter keys of a Markdown file and the text after them."""
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return [], text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            keys = [m.group(1) for raw in lines[1:index] if (m := FRONTMATTER_KEY.match(raw))]
            return keys, "\n".join(lines[index + 1 :])
    return [], text


def is_skill_or_command(path: str) -> bool:
    """Return whether Claude Code could load path as a skill or a command file."""
    parts = path.lower().split("/")
    if parts[0] == EXEMPT_DIR or not parts[-1].endswith(".md"):
        return False
    return parts[-1] == "skill.md" or "skills" in parts[:-1] or "commands" in parts[:-1]


def check_skill_content(root: Path, files: list[str]) -> list[str]:
    """Check skill and command Markdown for hook frontmatter and shell-injection syntax."""
    errors: list[str] = []
    for path in files:
        if not is_skill_or_command(path) or (root / path).is_symlink():
            continue
        text = (root / path).read_text(encoding="utf-8", errors="replace")
        keys, body = split_frontmatter(text)
        errors += [
            f"{path}: frontmatter key {key!r} {FORBIDDEN_FRONTMATTER[key]}"
            for key in keys
            if key in FORBIDDEN_FRONTMATTER
        ]
        if INLINE_INJECTION.search(body) or FENCED_INJECTION.search(body):
            errors.append(f"{path}: dynamic-context shell injection runs a command at load time")
    return errors


def parse_version(text: str) -> tuple[int, ...] | None:
    """Return the first dotted version number in text as a tuple, or None."""
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    return tuple(int(part) for part in match.groups()) if match else None


def report_findings(report: dict[str, object]) -> list[str]:
    """Return every hooks:, calls: or gating-hook finding in a `plugin validate --json` report."""
    findings: list[str] = []
    entries: list[dict[str, object]] = []
    manifest = report.get("manifest")
    if isinstance(manifest, dict):
        entries.append(manifest)
    contents = report.get("contents")
    if isinstance(contents, list):
        entries += [item for item in contents if isinstance(item, dict)]
    for entry in entries:
        file = str(entry.get("file", "<unknown>"))
        if entry.get("type") == "hooks":
            findings.append(f"{file}: the validator read a hooks file")
        if entry.get("gatingHooks"):
            findings.append(f"{file}: the validator reports gating hooks")
        notes = entry.get("notes")
        findings += [
            f"{file}: {note}"
            for note in (notes if isinstance(notes, list) else [])
            if isinstance(note, str) and VALIDATOR_FINDING.search(note)
        ]
    return findings


def copy_for_validation(root: Path, files: list[str], destination: Path) -> None:
    """Copy the plugin into destination with a synthesized manifest and no marketplace file."""
    for path in files:
        if path.startswith(("evals/", ".claude-plugin/")):
            continue
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / path, target)
    manifest_dir = destination / ".claude-plugin"
    manifest_dir.mkdir(exist_ok=True)
    manifest = {"name": "content-only-check", "version": "0.0.0", "description": "check copy"}
    (manifest_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")


def run_validator(root: Path, files: list[str]) -> tuple[list[str], str]:
    """Run `claude plugin validate` on a copy of the plugin; return findings and a status line."""
    claude = shutil.which("claude")
    if claude is None:
        return [], "SKIPPED, claude is not on PATH, so mods and hooks were not checked by it"
    try:
        version_run = subprocess.run(  # noqa: S603
            [claude, "--version"], capture_output=True, text=True, check=False, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], f"SKIPPED, claude --version failed: {exc}"
    version = parse_version(version_run.stdout)
    if version is None or version < MIN_VALIDATOR:
        return [], (
            f"SKIPPED, claude {version_run.stdout.strip() or 'of unknown version'} is older "
            f"than {'.'.join(map(str, MIN_VALIDATOR))} and does not report mods"
        )
    with tempfile.TemporaryDirectory() as scratch:
        copy = Path(scratch) / "plugin"
        copy_for_validation(root, files, copy)
        try:
            run = subprocess.run(  # noqa: S603
                [claude, "plugin", "validate", str(copy), "--json"],
                capture_output=True,
                text=True,
                check=False,
                timeout=VALIDATOR_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return [f"claude plugin validate did not complete: {exc}"], "FAILED to run"
    try:
        report = json.loads(run.stdout)
    except json.JSONDecodeError:
        return [f"claude plugin validate gave no JSON report (exit {run.returncode})"], "FAILED"
    findings = report_findings(report) if isinstance(report, dict) else ["unreadable report"]
    return findings, f"ran with claude {'.'.join(map(str, version))}"


def check_all(root: Path, *, use_validator: bool) -> tuple[list[str], str]:
    """Run every check against root; return the errors and the validator's status line."""
    files = list_files(root)
    errors = check_paths(root, files) + check_manifests(root) + check_skill_content(root, files)
    if not use_validator:
        return errors, "not requested"
    findings, status = run_validator(root, files)
    return errors + findings, status


def write(path: Path, text: str) -> None:
    """Write text to path, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def edit_manifest(path: str, change: Callable[[dict[str, object]], None]) -> Callable[[Path], None]:
    """Return a mutation that rewrites a JSON manifest in a fixture through change."""

    def mutate(fixture: Path) -> None:
        target = fixture / path
        manifest = json.loads(target.read_text(encoding="utf-8"))
        change(manifest)
        target.write_text(json.dumps(manifest), encoding="utf-8")

    return mutate


def first_entry(manifest: dict[str, object]) -> dict[str, object]:
    """Return the first plugin entry of a marketplace manifest."""
    plugins = manifest["plugins"]
    assert isinstance(plugins, list)  # noqa: S101
    entry = plugins[0]
    assert isinstance(entry, dict)  # noqa: S101
    return entry


def first_skill(fixture: Path) -> Path:
    """Return the path of one SKILL.md in a fixture."""
    return min((fixture / "skills").rglob("SKILL.md"))


def append_to_skill(text: str) -> Callable[[Path], None]:
    """Return a mutation that appends text to the first SKILL.md in a fixture."""

    def mutate(fixture: Path) -> None:
        skill = first_skill(fixture)
        skill.write_text(skill.read_text(encoding="utf-8") + text, encoding="utf-8")

    return mutate


def add_frontmatter_key(key: str) -> Callable[[Path], None]:
    """Return a mutation that adds a top-level frontmatter key to the first SKILL.md."""

    def mutate(fixture: Path) -> None:
        skill = first_skill(fixture)
        skill.write_text(
            skill.read_text(encoding="utf-8").replace("---\n", f"---\n{key}: {{}}\n", 1),
            encoding="utf-8",
        )

    return mutate


HOOKS_MODULE = (
    "export function register(on) {\n  on('tool.call', async ($, e, next) => next(e))\n}\n"
)


def add_hooks_module(fixture: Path) -> None:
    """Add the smallest complete mod: hooks/hooks.json naming a trivial hooks module."""
    write(fixture / "hooks/hooks.json", '{"modules": ["./register.js"]}\n')
    write(fixture / "hooks/register.js", HOOKS_MODULE)


def add_second_root(fixture: Path) -> None:
    """Point the first plugin entry at a subdirectory that holds a hooks configuration."""
    write(fixture / "sub/hooks/hooks.json", '{"modules": ["./register.js"]}\n')
    edit_manifest(
        ".claude-plugin/marketplace.json", lambda m: first_entry(m).update({"source": "./sub"})
    )(fixture)


# Each case names a mutation of a fixture copy and a fragment its error message must contain.
MUTATIONS: dict[str, tuple[Callable[[Path], None], str]] = {
    "a hooks module with hooks/hooks.json": (add_hooks_module, "hooks/"),
    "a hooks module nested in a skill": (
        lambda f: write(first_skill(f).parent / "register.mjs", HOOKS_MODULE),
        "candidate hooks module",
    ),
    "an .mcp.json file": (lambda f: write(f / ".mcp.json", "{}\n"), ".mcp.json"),
    "an .lsp.json file": (lambda f: write(f / ".lsp.json", "{}\n"), ".lsp.json"),
    "a monitors file": (lambda f: write(f / "monitors/monitors.json", "[]\n"), "monitors/"),
    "a bin executable": (lambda f: write(f / "bin/tool", "#!/bin/sh\n"), "bin/"),
    "a workflows script": (lambda f: write(f / "workflows/run.cjs", ""), "workflows/"),
    "a root settings.json": (lambda f: write(f / "settings.json", "{}\n"), "settings.json"),
    "an MCP bundle": (lambda f: write(f / "tools/server.mcpb", ""), "MCP bundle"),
    "a hooks key in plugin.json": (
        lambda f: write(f / ".claude-plugin/plugin.json", '{"name": "x", "hooks": "./h.json"}\n'),
        "'hooks'",
    ),
    "mcpServers in a marketplace entry": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"mcpServers": {"x": {"command": "node"}}}),
        ),
        "'mcpServers'",
    ),
    "hooks in a marketplace entry": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"hooks": {"PreToolUse": []}}),
        ),
        "'hooks'",
    ),
    "a dependency on another plugin": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"dependencies": ["other@elsewhere"]}),
        ),
        "'dependencies'",
    ),
    "a command plugin source": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update(
                {"source": {"source": "command", "command": "tool path"}}
            ),
        ),
        "relative path",
    ),
    "a github plugin source": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"source": {"source": "github", "repo": "owner/repo"}}),
        ),
        "relative path",
    ),
    "a hooks frontmatter key in a skill": (add_frontmatter_key("hooks"), "'hooks'"),
    "a shell frontmatter key in a skill": (add_frontmatter_key("shell"), "'shell'"),
    "a symlinked hooks directory": (
        lambda f: (f / "hooks").symlink_to(first_skill(f).parent, target_is_directory=True),
        "symlink",
    ),
    "a hooks module in a second plugin root": (add_second_root, "sub/hooks/hooks.json"),
    "a plugin source that leaves the marketplace root": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"source": "./../elsewhere"}),
        ),
        "leaves the marketplace root",
    ),
    "a plugin source in the exempt directory": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"source": "./agent-templates"}),
        ),
        "reaches agent-templates/",
    ),
    "a skills path in the exempt directory": (
        edit_manifest(
            ".claude-plugin/marketplace.json",
            lambda m: first_entry(m).update({"skills": ["./agent-templates/x"]}),
        ),
        "reaches agent-templates/",
    ),
    "a mixed-case hooks directory": (
        lambda f: write(f / "Hooks/hooks.json", '{"modules": ["./register.js"]}\n'),
        "Hooks/hooks.json",
    ),
    "a mixed-case .mcp.json file": (lambda f: write(f / ".MCP.json", "{}\n"), ".MCP.json"),
    "a quoted hooks frontmatter key in a skill": (add_frontmatter_key('"hooks"'), "'hooks'"),
    "shell injection in a command file": (
        lambda f: write(f / "commands/run.md", "Status: !`git status`\n"),
        "commands/run.md",
    ),
    "inline shell injection in a skill": (
        append_to_skill("\nBranch: !`git branch`\n"),
        "injection",
    ),
    "fenced shell injection in a skill": (append_to_skill("\n```!\nid\n```\n"), "injection"),
}


def self_test(root: Path) -> int:
    """Prove the checks pass on a copy of the real plugin and reject each mutation of it."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as scratch:
        base = Path(scratch) / "base"
        shutil.copytree(root / ".claude-plugin", base / ".claude-plugin")
        shutil.copytree(root / "skills", base / "skills")
        errors, _ = check_all(base, use_validator=False)
        print(f"clean copy of the plugin: {'rejected' if errors else 'accepted'}")
        failures += [f"clean copy: {error}" for error in errors]
        for name, (mutate, expected) in MUTATIONS.items():
            fixture = Path(scratch) / f"case-{len(list(Path(scratch).iterdir()))}"
            shutil.copytree(base, fixture)
            mutate(fixture)
            errors, _ = check_all(fixture, use_validator=False)
            rejected = any(expected in error for error in errors)
            print(f"{name}: {'rejected' if rejected else 'NOT REJECTED'}")
            if not rejected:
                failures.append(f"{name}: no error containing {expected!r}")
        fixture = Path(scratch) / "validator"
        shutil.copytree(base, fixture)
        add_hooks_module(fixture)
        findings, status = run_validator(fixture, list_files(fixture))
        print(f"claude plugin validate on a copy with a hooks module: {status}")
        if status.startswith("ran") and not findings:
            failures.append("the validator ran and did not report the hooks module")
        elif status.startswith("ran"):
            print("  rejected by the validator")
    for failure in failures:
        print(f"SELF-TEST FAILURE: {failure}", file=sys.stderr)
    return 1 if failures else 0


def main() -> int:
    """Parse arguments, run the checks, print the result, and return the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="plugin root to check")
    parser.add_argument(
        "--self-test", action="store_true", help="check the checks against mutated copies"
    )
    parser.add_argument(
        "--no-validator", action="store_true", help="skip `claude plugin validate` even if present"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if args.self_test:
        return self_test(root)
    errors, status = check_all(root, use_validator=not args.no_validator)
    for error in errors:
        print(error)
    print(f"static checks: paths, manifests, skill content ran; claude plugin validate: {status}")
    if errors:
        print(f"{len(errors)} content-only violation(s)")
        return 1
    checked_by = "the static checks and claude plugin validate"
    if not status.startswith("ran"):
        checked_by = "the static checks only"
    print(f"content-only by {checked_by}: no hooks, mods, MCP servers, or other extension code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
