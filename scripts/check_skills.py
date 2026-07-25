#!/usr/bin/env python3
"""Check every skills/<category>/<name>/SKILL.md against this repository's authoring rules.

The rules are the ones stated in README.md:

- The frontmatter block parses as YAML and defines `name` and `description`.
- `name` matches the skill's parent directory name.
- `description` is non-empty, under 1,024 characters, and written in third person.
- The body (everything after the frontmatter) is under 500 lines.

It also checks the plugin marketplace manifest, since a skill that is not listed there
never reaches a project that installs this library as a plugin.

Run it from the repository root:

    python3 scripts/check_skills.py

Exits 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

MAX_DESCRIPTION_CHARS = 1024
MAX_BODY_LINES = 500

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")

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
    """Split a SKILL.md into its raw frontmatter block and its body lines.

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


def check_description(description: object, errors: list[str]) -> None:
    """Validate the description field: present, non-empty, bounded, third person."""
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
            errors.append(f"'description' opens with {opening!r}; lead with what the skill does")
            break

    found = sorted({match.group().lower() for match in FIRST_OR_SECOND_PERSON.finditer(stripped)})
    if found:
        errors.append(
            f"'description' uses first- or second-person wording ({', '.join(found)}); "
            "write it in third person, stating what the skill does"
        )


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

    check_description(frontmatter.get("description"), errors)

    if len(body) >= MAX_BODY_LINES:
        errors.append(f"body is {len(body)} lines, must be under {MAX_BODY_LINES}")

    return errors


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


def main() -> int:
    """Check every skill and the marketplace manifest, and report the results."""
    repo_root = Path(__file__).resolve().parent.parent
    skills = sorted(repo_root.glob("skills/*/*/SKILL.md"))

    if not skills:
        print("error: no skills/*/*/SKILL.md files found", file=sys.stderr)
        return 1

    failed = 0
    for skill_path in skills:
        relative = skill_path.relative_to(repo_root)
        errors = check_skill(skill_path)
        if errors:
            failed += 1
            for error in errors:
                print(f"{relative}: {error}", file=sys.stderr)
        else:
            print(f"{relative}: ok")

    marketplace_errors = check_marketplace(repo_root, skills)
    for error in marketplace_errors:
        print(error, file=sys.stderr)
    if not marketplace_errors:
        print(f"{MARKETPLACE_PATH}: ok")

    if failed or marketplace_errors:
        print(
            f"\n{failed} of {len(skills)} skill(s) failed, "
            f"{len(marketplace_errors)} marketplace problem(s)",
            file=sys.stderr,
        )
        return 1

    print(f"\nall {len(skills)} skill(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
