#!/usr/bin/env python3
"""Report capabilities a diff adds to a skill without declaring them in its frontmatter.

Every SKILL.md declares `capabilities` with `tools`, `shell`, `paths` and `egress`.
`scripts/check_skills.py` checks that block's shape. This script compares it against what a
change actually adds: hostnames, paths outside the repository under work, and command names
that appear in shell blocks. Anything added and not declared is printed for a reviewer.

It reports rather than fails, by design, and the reason is worth stating where someone
reading the output can see it. The declaration and the body have the same author, so a
contributor who adds a command and declares it passes any check that can be written here. A
capability block makes a capability change reviewable rather than impossible, and this
script is the attention list for that review, not a gate. `--strict` exists for a reviewer
who wants a non-zero exit while looking at one branch, and lint.yml does not use it.

The detector is limited in ways that matter more than what it catches, so they are stated
rather than left for someone to discover:

- Prose is invisible to it. "Check the current REST documentation" is an instruction to
  fetch a web page and no regex here will see it.
- A familiar name can hide arbitrary execution. `pre-commit run --all-files` runs whatever
  hooks the target repository configures.
- Discussion reads the same as instruction. A reference file explaining `curl` looks like a
  reference file running it, so this reports the file rather than judging it.
- A quoted command is invisible. Quoted spans are removed before a line is read, so that a
  `|` inside a pattern is not a pipeline, and `bash -c "curl ..."` reports `bash`.

Run it from the repository root, under `uv` because it reads YAML:

    uv run --frozen python scripts/check_capabilities.py          # against origin/main
    uv run --frozen python scripts/check_capabilities.py --base HEAD~1
    uv run --frozen python scripts/check_capabilities.py --strict  # non-zero exit on a finding

Exits 0 when the comparison ran, whatever it found, unless --strict is passed.
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# A frontmatter block splits a file into at least three parts on the delimiter: what comes
# before the opening `---`, the block, and the body.
FRONTMATTER_PARTS = 3
GIT = shutil.which("git") or "git"
BASELINE_REFS = ("origin/main", "main")

# A skill owns its SKILL.md and everything under its references/ directory. The references
# hold most of the commands, so a check that read only SKILL.md would miss the majority of
# what it is looking for.
SKILL_GLOB = "skills/*/*/SKILL.md"

# A hostname in an added line. Markdown link targets are included deliberately: a citation
# and a fetch instruction are the same text, and deciding which is a reviewer's job.
HOSTNAME = re.compile(r"https?://([A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?)")

# A path that leaves the repository under work.
OUTSIDE_PATH = re.compile(
    r"(?<![\w/])(~/[\w./-]*|\$HOME[\w./-]*|/(?:etc|usr|var|opt|root)/[\w./-]*)"
)

# A command name inside a shell fence. One line can run several: a pipeline, a list joined
# by `&&` or `||`, or a name behind an execution prefix.
FENCE = re.compile(r"^\s*```(sh|bash|shell|console)\s*$")
FENCE_END = re.compile(r"^\s*```\s*$")
COMMAND = re.compile(r"^([a-z][\w.-]*)\b")
SEPARATOR = re.compile(r"\|\||&&|[;|]")
ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*\+?=")

# A function the document defines itself. `die` is not a dependency of anything; it is three
# lines further up the same example.
DEFINITION = re.compile(r"^\s*(?:function\s+)?([a-z][\w.-]*)\s*\(\)", re.MULTILINE)

# An arithmetic expression holds `;` and reads nothing like a command list, so a line that
# opens one is not split: `for ((attempt = 1; attempt <= attempts; attempt++))` runs `for`.
ARITHMETIC = "(("

# Names that run another command. The dependency is what follows one of these, not the
# prefix, which is why `sudo apt-get` has to report `apt-get`.
EXEC_PREFIX = frozenset({"command", "env", "exec", "nohup", "sudo", "time", "xargs"})

# Control words, shell builtins, and the file and text utilities that every environment a
# skill runs in already has. None of them is a dependency a reviewer needs to look at.
NOT_A_COMMAND = frozenset(
    {
        "builtin",
        "case",
        "cat",
        "cd",
        "chmod",
        "cp",
        "declare",
        "do",
        "done",
        "echo",
        "elif",
        "else",
        "esac",
        "eval",
        "exec",
        "exit",
        "export",
        "false",
        "fi",
        "for",
        "function",
        "if",
        "in",
        "let",
        "local",
        "mapfile",
        "mkdir",
        "mv",
        "printf",
        "pwd",
        "read",
        "readonly",
        "return",
        "rm",
        "set",
        "shift",
        "shopt",
        "sleep",
        "source",
        "test",
        "then",
        "trap",
        "true",
        "umask",
        "unset",
        "until",
        "wait",
        "while",
    }
)


def git_output(arguments: list[str]) -> tuple[int, str]:
    """Return the exit code and stdout of one git command run in the repository root."""
    # A fixed argument list built from repository paths, with no shell involved.
    result = subprocess.run(  # noqa: S603
        [GIT, *arguments], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    return result.returncode, result.stdout


def resolve_baseline(requested: str) -> str | None:
    """Return the baseline ref to compare against, or None when none resolves."""
    candidates = (requested,) if requested else BASELINE_REFS
    for ref in candidates:
        code, _ = git_output(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])
        if code == 0:
            return ref
    return None


def file_at(baseline: str, path: str) -> str:
    """Return one file's contents at the baseline, empty when it did not exist there."""
    code, out = git_output(["show", f"{baseline}:{path}"])
    return out if code == 0 else ""


def files_under(baseline: str, directory: str) -> list[str]:
    """Return the paths under one directory, in the baseline and in the working tree both.

    A file present in only one of the two still has to be compared, since a reference file
    added by the change is exactly what this is looking for.
    """
    code, out = git_output(["ls-tree", "-r", "--name-only", baseline, "--", directory])
    paths = set(out.split()) if code == 0 else set()
    local = REPO_ROOT / directory
    if local.is_dir():
        paths |= {str(path.relative_to(REPO_ROOT)) for path in local.rglob("*") if path.is_file()}
    return sorted(paths)


def declared(text: str) -> dict[str, set[str]]:
    """Return the capability block one SKILL.md declares, empty when it is unreadable.

    It takes the text rather than the path because the same block has to be read twice: as
    the working tree holds it, and as the baseline held it, which arrives from `git show`.
    """
    parts = text.split("---")
    if len(parts) < FRONTMATTER_PARTS:
        return {}
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return {}
    block = (frontmatter or {}).get("capabilities")
    if not isinstance(block, dict):
        return {}
    return {
        key: {str(item) for item in value}
        for key, value in block.items()
        if isinstance(value, list)
    }


def unquote(line: str, opener: str) -> tuple[str, str]:
    """Return one line with its quoted spans removed, and the quote it leaves open.

    `opener` is the quote character an earlier line left open, empty when none. Quoting is
    read across lines because this content quotes across lines: a `jq` filter spanning three
    lines is one string, and `length` inside it is a filter rather than a command. Within a
    line it is what makes `grep -E 'a|b'` one command instead of two.

    A comment ends the line, which matters for more than the words in it: the apostrophe in
    `# the environment is the caller's` would otherwise open a quote that no later line
    closes, and every command for the rest of the block would be read as quoted text.

    It is a scanner, not a shell. Nothing here reproduces the way `$(` restarts quoting, so
    a substitution nested inside a quoted word leaves text this reads as bare.
    """
    kept: list[str] = []
    quote = opener
    for char in line:
        if quote:
            quote = "" if char == quote else quote
        elif char == "#" and (not kept or kept[-1].isspace()):
            break
        elif char in "'\"":
            quote = char
        else:
            kept.append(char)
    return "".join(kept), quote


def command_in(segment: str) -> set[str]:
    """Return the command name one segment of a shell line runs, empty when it names none.

    A segment is what a fence line leaves after its quoted spans are removed and it is split
    on `|`, `&&`, `||` and `;`. Leading execution prefixes and assignments are dropped, so
    `sudo apt-get` reports `apt-get` and `version=1 uv sync` reports `uv`. The caller drops
    the names the document defines as functions of its own.
    """
    words = segment.split()
    while words:
        if words[0] in EXEC_PREFIX:
            words = words[1:]
        elif ASSIGNMENT.match(words[0]):
            # An assignment whose value expands something is one word to a shell and several
            # to a regex. What follows it here is the tail of that value, not a command.
            if "$" in words[0]:
                return set()
            words = words[1:]
        else:
            break
    if not words:
        return set()
    match = COMMAND.match(words[0])
    if match is None or match.group(1) in NOT_A_COMMAND:
        return set()
    return {match.group(1)}


def capabilities_in(text: str) -> dict[str, set[str]]:
    """Return the hostnames, outside paths and shell command names one document holds.

    Command names come only from inside a fenced shell block, which is the difference
    between reading a document and guessing at it: the first word of a prose line is not a
    command, and an earlier version of this script reported `capabilities`, `paths` and
    `what` as commands because it did not track the fence.
    """
    hosts = set(HOSTNAME.findall(text))
    paths = set(OUTSIDE_PATH.findall(text))
    defined = set(DEFINITION.findall(text))
    commands: set[str] = set()
    in_fence = False
    continued = False
    quote = ""
    for line in text.splitlines():
        if not in_fence and FENCE.match(line):
            in_fence = True
            continue
        if in_fence and FENCE_END.match(line):
            in_fence, quote = False, ""
            continue
        if not in_fence:
            continue
        # Every line in the fence goes through the scanner, including the ones skipped
        # below, because a quote one line opens is closed by a later one.
        bare, quote = unquote(line, quote)
        # A continuation carries an argument, not a command name. Without this, the second
        # line of the digest-pinned `docker run` reports `rhysd` as a new dependency.
        was_continued, continued = continued, line.rstrip().endswith("\\")
        if was_continued:
            continue
        segments = [bare] if ARITHMETIC in bare else SEPARATOR.split(bare)
        for segment in segments:
            commands |= command_in(segment) - defined
    return {"egress": hosts, "paths": paths, "shell": commands, "defined": defined}


def report_for(skill: Path, baseline: str) -> list[str]:
    """Return the capabilities one skill gained against the baseline without declaring them."""
    block = declared(skill.read_text(encoding="utf-8"))
    relative = skill.parent.relative_to(REPO_ROOT)
    paths = [str(relative / "SKILL.md"), *files_under(baseline, str(relative / "references"))]

    added: dict[str, set[str]] = {"egress": set(), "paths": set(), "shell": set()}
    defined: set[str] = set()
    for path in paths:
        local = REPO_ROOT / path
        now = capabilities_in(local.read_text(encoding="utf-8")) if local.is_file() else {}
        before = capabilities_in(file_at(baseline, path))
        defined |= now.get("defined", set())
        for key in added:
            added[key] |= now.get(key, set()) - before.get(key, set())
    # A helper one reference file defines and another calls is the skill's own function.
    # The skill is the unit here, which is why this is subtracted across its files rather
    # than within each one.
    added["shell"] -= defined

    findings = [f"egress: {host}" for host in sorted(added["egress"] - block.get("egress", set()))]
    findings += [
        f"path outside the repository: {path}"
        for path in sorted(added["paths"])
        if not any(path in declaration for declaration in block.get("paths", set()))
    ]
    findings += [
        f"command: {command}" for command in sorted(added["shell"] - block.get("shell", set()))
    ]
    if not findings:
        return []

    skill_diff = git_output(["diff", "--quiet", baseline, "--", str(relative / "SKILL.md")])[0]
    before_block = declared(file_at(baseline, str(relative / "SKILL.md")))
    note = "" if skill_diff != 0 and before_block != block else "  (capability block unchanged)"
    return [f"{relative}{note}", *[f"    {finding}" for finding in findings]]


def main() -> int:
    """Compare every skill against the baseline and print what it adds without declaring."""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="", help="ref to compare against, default origin/main")
    parser.add_argument(
        "--strict", action="store_true", help="exit non-zero when anything is reported"
    )
    args = parser.parse_args()

    baseline = resolve_baseline(args.base)
    if baseline is None:
        tried = args.base or ", ".join(BASELINE_REFS)
        print(f"no baseline ref resolves here, tried {tried}; nothing to compare", file=sys.stderr)
        return 0

    skills = sorted(REPO_ROOT.glob(SKILL_GLOB))
    reported = 0
    for skill in skills:
        block = report_for(skill, baseline)
        if block:
            reported += 1
            print("\n".join(block))

    if reported == 0:
        print(f"no undeclared capability added against {baseline}, across {len(skills)} skill(s)")
        return 0
    print(
        f"\n{reported} skill(s) add something their capability block does not declare, "
        f"against {baseline}.\nThis is a reading list, not a verdict: a declared capability "
        "is not a safe one, and this\ndetector cannot see a capability written in prose."
    )
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
