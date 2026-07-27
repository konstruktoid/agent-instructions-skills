#!/usr/bin/env python3
"""Check this repository's skills and agent templates against its own authoring rules.

For every skills/<category>/<name>/SKILL.md, the rules stated in README.md are:

- The frontmatter block parses as YAML and defines `name` and `description`.
- `name` matches the skill's parent directory name.
- `description` is non-empty, under 1,024 characters, and written in third person.
- The body (everything after the frontmatter) is under 500 lines.

It also checks the plugin marketplace manifest, since a skill that is not listed there
never reaches a project that installs this library as a plugin, and the cross-references
between skills and instructions/, which README.md requires to run in both directions and
which nothing else would catch drifting.

For every agent-templates/<name>.md, the rules are the same frontmatter rules with
`name` matching the file stem, plus the neutral defaults a template must ship with:
`model: inherit` and an explicit `tools` allowlist. It also fails when an `agents`
directory appears at the repository root, because Claude Code auto-discovers that name
at a plugin root and would install every template as a live subagent.

Run it from the repository root:

    python3 scripts/check_skills.py

Exits 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import yaml

MAX_DESCRIPTION_CHARS = 1024
MAX_BODY_LINES = 500

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")

AGENT_TEMPLATE_GLOB = "agent-templates/*.md"

INSTRUCTIONS_DIR = Path("instructions")

# `instructions/<name>.md` as this library's own path, anchored so it does not also match a
# path that merely ends in that directory name. `.github/instructions/*.instructions.md`,
# which ansible-verification-loop names as a repository convention file, is not a reference
# to this library and must not be checked as one.
INSTRUCTIONS_REFERENCE = re.compile(r"(?<![\w./-])instructions/([A-Za-z0-9_-]+\.md)")

# `skills/<category>/<name>/SKILL.md`, the form the instructions documents use when they
# point back at a skill.
SKILL_REFERENCE = re.compile(r"(?<![\w./-])skills/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)/SKILL\.md")

# Claude Code auto-discovers subagents from an `agents/` directory at a plugin root, and
# every plugin in the marketplace manifest is sourced from the repository root. Templates
# placed there would install into every consuming project as live subagents, which is the
# opposite of the copy-and-adapt rule they exist under.
PLUGIN_AGENT_DIR = Path("agents")

# A template pins no model of its own: it ships the model that follows the main
# conversation and leaves the choice to whoever copies it.
NEUTRAL_MODEL = "inherit"

# Openings that describe the skill from the reader's side rather than stating what the
# skill does. The README requires the description to lead with what the skill does.
BANNED_OPENINGS = (
    "use this to",
    "use this skill",
)

# First- and second-person wording, matched anywhere in the description rather than only
# at its start: "Reviews Terraform, and I will report what I changed" is as much a rule
# violation as opening with it. Contractions need no pattern of their own, since an
# apostrophe is a word boundary and "I'll" is matched by the bare pronoun. That pronoun
# excludes the "I" in "I/O", which is not first person.
FIRST_OR_SECOND_PERSON = re.compile(
    r"""
      \bI\b(?!/)
    | \b(?:me|my|mine|myself)\b
    | \b(?:we|us|our|ours|ourselves)\b
    | \b(?:you|your|yours|yourself|yourselves)\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

FRONTMATTER_DELIMITER = "---"


def split_frontmatter(text: str, errors: list[str]) -> tuple[str | None, list[str]]:
    """Split a Markdown file into its raw frontmatter block and its body lines.

    Returns (None, []) and appends to `errors` when no delimited block is present.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        errors.append("does not start with a '---' frontmatter delimiter")
        return None, []

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONTMATTER_DELIMITER:
            return "\n".join(lines[1:index]), lines[index + 1 :]

    errors.append("frontmatter block is not closed by a second '---'")
    return None, []


def check_description(description: object, errors: list[str], subject: str) -> None:
    """Validate the description field: present, non-empty, bounded, third person.

    `subject` names what the file defines, "skill" or "agent", so the wording of a
    violation matches the file it is reported against.
    """
    if description is None:
        errors.append("frontmatter is missing 'description'")
        return
    if not isinstance(description, str):
        errors.append(f"'description' must be a string, got {type(description).__name__}")
        return

    stripped = description.strip()
    if not stripped:
        errors.append("'description' is empty")
        return
    if len(description) >= MAX_DESCRIPTION_CHARS:
        errors.append(
            f"'description' is {len(description)} characters, must be under {MAX_DESCRIPTION_CHARS}"
        )

    lowered = stripped.lower()
    for opening in BANNED_OPENINGS:
        if lowered.startswith(opening):
            errors.append(
                f"'description' opens with {opening!r}; lead with what the {subject} does"
            )
            break

    found = sorted({match.group().lower() for match in FIRST_OR_SECOND_PERSON.finditer(stripped)})
    if found:
        errors.append(
            f"'description' uses first- or second-person wording ({', '.join(found)}); "
            f"write it in third person, stating what the {subject} does"
        )


def check_tools(tools: object, errors: list[str]) -> None:
    """Validate the tools field: an explicit, non-empty allowlist of tool names.

    Claude Code reads the field as either a comma-separated string or a YAML list, so
    both forms pass here. A missing field is the case that matters: it grants the agent
    every tool the main conversation has, which is what a template must not ship.
    """
    if tools is None:
        errors.append(
            "frontmatter is missing 'tools'; without an explicit allowlist a copied "
            "template grants every tool the main conversation has"
        )
        return

    if isinstance(tools, str):
        entries: list[object] = [entry.strip() for entry in tools.split(",")]
    elif isinstance(tools, list):
        entries = tools
    else:
        errors.append(
            f"'tools' must be a comma-separated string or a YAML list, got {type(tools).__name__}"
        )
        return

    if not entries or any(not isinstance(entry, str) or not entry.strip() for entry in entries):
        errors.append("'tools' must list at least one tool name, with no empty entries")


def check_skill(skill_path: Path) -> list[str]:
    """Return the list of rule violations for one SKILL.md, empty when it passes."""
    errors: list[str] = []
    text = skill_path.read_text(encoding="utf-8")

    raw_frontmatter, body = split_frontmatter(text, errors)
    if raw_frontmatter is None:
        return errors

    try:
        frontmatter = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        errors.append(f"frontmatter does not parse as YAML: {exc}")
        return errors

    if not isinstance(frontmatter, dict):
        errors.append("frontmatter must be a YAML mapping")
        return errors

    expected_name = skill_path.parent.name
    name = frontmatter.get("name")
    if name is None:
        errors.append("frontmatter is missing 'name'")
    elif name != expected_name:
        errors.append(f"'name' is {name!r}, must match the directory name {expected_name!r}")

    check_description(frontmatter.get("description"), errors, "skill")

    if len(body) >= MAX_BODY_LINES:
        errors.append(f"body is {len(body)} lines, must be under {MAX_BODY_LINES}")

    return errors


def check_agent_template(template_path: Path) -> list[str]:
    """Return the list of rule violations for one agent template, empty when it passes."""
    errors: list[str] = []
    text = template_path.read_text(encoding="utf-8")

    raw_frontmatter, _ = split_frontmatter(text, errors)
    if raw_frontmatter is None:
        return errors

    try:
        frontmatter = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        errors.append(f"frontmatter does not parse as YAML: {exc}")
        return errors

    if not isinstance(frontmatter, dict):
        errors.append("frontmatter must be a YAML mapping")
        return errors

    expected_name = template_path.stem
    name = frontmatter.get("name")
    if name is None:
        errors.append("frontmatter is missing 'name'")
    elif name != expected_name:
        errors.append(f"'name' is {name!r}, must match the file name {expected_name!r}")

    check_description(frontmatter.get("description"), errors, "agent")

    model = frontmatter.get("model")
    if model != NEUTRAL_MODEL:
        errors.append(
            f"'model' is {model!r}, must be {NEUTRAL_MODEL!r} so a copied template pins "
            "no model on the consumer"
        )

    check_tools(frontmatter.get("tools"), errors)

    return errors


def check_plugin_agent_dir(repo_root: Path) -> list[str]:
    """Fail when an `agents/` directory exists at the repository root.

    Every plugin in the marketplace manifest is sourced from the repository root, so that
    directory name would ship the copy-and-adapt templates as installable subagents.
    """
    if not (repo_root / PLUGIN_AGENT_DIR).is_dir():
        return []
    return [
        (
            f"{PLUGIN_AGENT_DIR}/: Claude Code auto-discovers this directory at a plugin "
            "root, which would install its contents into every consuming project as live "
            "subagents; keep agent templates in agent-templates/"
        )
    ]


def check_marketplace(repo_root: Path, skills: list[Path]) -> list[str]:
    """Check that the marketplace manifest exposes every skill exactly once.

    A skill missing from the manifest is invisible to any project that installs this
    library as a Claude Code plugin, which no other check would catch.
    """
    errors: list[str] = []
    manifest_path = repo_root / MARKETPLACE_PATH
    if not manifest_path.is_file():
        return [f"{MARKETPLACE_PATH}: missing"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{MARKETPLACE_PATH}: does not parse as JSON: {exc}"]

    declared: dict[Path, str] = {}
    for entry in manifest.get("plugins", []):
        plugin_name = entry.get("name", "<unnamed>")
        for raw_path in entry.get("skills", []):
            path = (repo_root / raw_path).resolve()
            if not (path / "SKILL.md").is_file():
                errors.append(
                    f"{MARKETPLACE_PATH}: plugin {plugin_name!r} lists {raw_path}, "
                    "which has no SKILL.md"
                )
                continue
            if path in declared:
                errors.append(
                    f"{MARKETPLACE_PATH}: {raw_path} is listed by both "
                    f"{declared[path]!r} and {plugin_name!r}"
                )
            declared[path] = plugin_name

    for skill_path in skills:
        if skill_path.parent.resolve() not in declared:
            relative = skill_path.relative_to(repo_root).parent
            errors.append(
                f"{MARKETPLACE_PATH}: {relative} is not listed by any plugin, so it "
                "would not install"
            )

    return errors


def check_cross_references(repo_root: Path, skills: list[Path]) -> list[str]:
    """Check that skill and instructions cross-references resolve, and point both ways.

    README.md requires a skill that extends an instructions document to cross-reference it
    by path in both directions. That rule is prose in two files and drifts silently, so it
    is checked here rather than trusted. Three failures are reported:

    1. A SKILL.md names an `instructions/*.md` file that does not exist.
    2. An `instructions/*.md` names a `skills/*/*/SKILL.md` that does not exist.
    3. A skill names an instructions document that does not name that skill back.
    """
    errors: list[str] = []
    instructions = sorted((repo_root / INSTRUCTIONS_DIR).glob("*.md"))
    documents = {path.name: path.read_text(encoding="utf-8") for path in instructions}

    # Skill -> instructions, collected first so the reverse check can consult it.
    named_by: dict[str, list[Path]] = {}
    for skill_path in skills:
        relative = skill_path.relative_to(repo_root)
        text = skill_path.read_text(encoding="utf-8")
        for name in sorted(set(INSTRUCTIONS_REFERENCE.findall(text))):
            if name not in documents:
                errors.append(f"{relative}: references instructions/{name}, which does not exist")
                continue
            named_by.setdefault(name, []).append(skill_path)

    for path in instructions:
        relative = path.relative_to(repo_root)
        for category, name in sorted(set(SKILL_REFERENCE.findall(documents[path.name]))):
            target = repo_root / "skills" / category / name / "SKILL.md"
            if not target.is_file():
                errors.append(
                    f"{relative}: references skills/{category}/{name}/SKILL.md, "
                    "which does not exist"
                )

    for name, referring in sorted(named_by.items()):
        document = documents[name]
        for skill_path in referring:
            expected = str(skill_path.relative_to(repo_root))
            if expected not in document:
                errors.append(
                    f"instructions/{name}: is named by {expected} but does not name it back; "
                    "README.md requires the cross-reference in both directions"
                )

    return errors


def report(repo_root: Path, paths: list[Path], check: Callable[[Path], list[str]]) -> int:
    """Run `check` over every path, print one line per file, and return the failure count."""
    failed = 0
    for path in paths:
        relative = path.relative_to(repo_root)
        errors = check(path)
        if errors:
            failed += 1
            for error in errors:
                print(f"{relative}: {error}", file=sys.stderr)
        else:
            print(f"{relative}: ok")
    return failed


def main() -> int:
    """Check every skill and agent template plus the manifest, and report the results."""
    repo_root = Path(__file__).resolve().parent.parent
    skills = sorted(repo_root.glob("skills/*/*/SKILL.md"))
    templates = sorted(repo_root.glob(AGENT_TEMPLATE_GLOB))

    if not skills:
        print("error: no skills/*/*/SKILL.md files found", file=sys.stderr)
        return 1
    if not templates:
        print(f"error: no {AGENT_TEMPLATE_GLOB} files found", file=sys.stderr)
        return 1

    failed = report(repo_root, skills, check_skill)
    template_failed = report(repo_root, templates, check_agent_template)

    manifest_errors = check_marketplace(repo_root, skills) + check_plugin_agent_dir(repo_root)
    for error in manifest_errors:
        print(error, file=sys.stderr)
    if not manifest_errors:
        print(f"{MARKETPLACE_PATH}: ok")

    reference_errors = check_cross_references(repo_root, skills)
    for error in reference_errors:
        print(error, file=sys.stderr)
    if not reference_errors:
        print(f"{INSTRUCTIONS_DIR}/: cross-references ok")

    if failed or template_failed or manifest_errors or reference_errors:
        print(
            f"\n{failed} of {len(skills)} skill(s) failed, "
            f"{template_failed} of {len(templates)} agent template(s) failed, "
            f"{len(manifest_errors)} packaging problem(s), "
            f"{len(reference_errors)} cross-reference problem(s)",
            file=sys.stderr,
        )
        return 1

    print(f"\nall {len(skills)} skill(s) and {len(templates)} agent template(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
