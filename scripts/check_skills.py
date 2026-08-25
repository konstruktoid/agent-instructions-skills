#!/usr/bin/env python3
"""Check this repository's skills and agent templates against its own authoring rules.

For every skills/<category>/<name>/SKILL.md, the rules stated in README.md are:

- The frontmatter block parses as YAML and defines `name` and `description`.
- `name` matches the skill's parent directory name.
- `description` is non-empty, under 1,024 characters, and written in third person.
- `capabilities` declares `tools`, `shell`, `paths` and `egress`, each a sorted list of
  strings, with `tools` drawn from the declarable set. The shape is checked, not the truth
  of it; `scripts/check_capabilities.py` reports what a diff adds without declaring it.
- The body (everything after the frontmatter) is under 500 lines.

It also checks the plugin marketplace manifest, since a skill that is not listed there
never reaches a project that installs this library as a plugin and a plugin entry with no
`version` turns every commit into a release, the cross-references
between skills and instructions/, which README.md requires to run in both directions and
which nothing else would catch drifting, the Contents list README.md requires of every
reference file past 100 lines, and the prose of every document this library publishes
against the em dash, arrow, inflated-vocabulary, and grammatical-person rules in
instructions/written_language_instructions.md.

For every agent-templates/<name>.md, the rules are the same frontmatter rules with
`name` matching the file stem, plus the neutral defaults a template must ship with:
`model: inherit` and an explicit `tools` allowlist. It also fails when an entry appears
at the repository root that is not on the packaging allowlist, because the marketplace
manifest sources every plugin from the root and Claude Code auto-discovers `agents/`,
`commands/`, `hooks/` and `.mcp.json` at a plugin root, installing what it finds into
every consuming project.

Run it from the repository root:

    python3 scripts/check_skills.py

Exits 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import io
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

# Anthropic's skill authoring guidance asks for a table of contents in a reference file past
# roughly this length: an agent previewing a long file with a partial read sees only its first
# screen, and without the list it cannot tell what the rest of the file covers.
TOC_REQUIRED_LINES = 100

REFERENCE_GLOB = "skills/*/*/references/*.md"

TOC_HEADING = "## Contents"

SECTION_HEADING = re.compile(r"^## (.+)$")

TOC_ENTRY = re.compile(r"^- (.+)$")

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")

# Every plugin entry has to declare a version, and all of them have to declare the same
# one. They ship from a single repository at a single tag, so a per-plugin version would be
# a claim this repository has no way to make true. Without a version, Claude Code treats
# every commit on the default branch as a new release and an update fetches whatever is
# there, which is the moving-ref exposure README.md's release section describes.
PLUGIN_VERSION = re.compile(r"^\d+\.\d+\.\d+$")

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
# Every plugin in the marketplace manifest is sourced from the repository root, which makes
# the repository root a plugin root: Claude Code auto-discovers `agents/`, `commands/`,
# `hooks/` and `.mcp.json` there and installs what it finds into every consuming project.
# This is an allowlist of the entries the repository is allowed to have rather than a
# denylist of those four names, because the discovery list belongs to Claude Code and can
# grow without this repository being told. An entry that is not listed fails, which is the
# direction a wrong answer has to fail in.
PLUGIN_ROOT_ALLOWED = frozenset(
    {
        ".claude-plugin",
        ".github",
        ".gitignore",
        ".markdownlint-cli2.yaml",
        "LICENSE",
        "README.md",
        "SECURITY.md",
        "agent-templates",
        "docs",
        "evals",
        "instructions",
        "pyproject.toml",
        "scripts",
        "skills",
        "uv.lock",
    }
)

# Local-only entries that .gitignore already keeps out of the repository, plus git's own
# directory. They are skipped rather than allowlisted: none of them is published, and a
# contributor's virtual environment is not a packaging decision.
PLUGIN_ROOT_IGNORED = frozenset({".git", ".ruff_cache", ".venv", "__pycache__", "node_modules"})

# A template pins no model of its own: it ships the model that follows the main
# conversation and leaves the choice to whoever copies it.
NEUTRAL_MODEL = "inherit"

# The capability block every SKILL.md declares, and the only keys it may hold. The block is
# checked for shape here and never for truth: the declaration and the body have the same
# author, so a capability added to both passes. Its value is that a capability change shows
# up in the frontmatter diff, one line per capability, where a reviewer has a chance of
# seeing it. `scripts/check_capabilities.py` reports what a diff adds without touching it.
CAPABILITY_KEYS = ("tools", "shell", "paths", "egress")

# The tools a skill may declare. Anything outside this set is a capability worth stopping
# on rather than absorbing: WebFetch and WebSearch are egress, Task spawns an agent this
# repository cannot describe, and an unknown name is one nobody has reviewed.
DECLARABLE_TOOLS = frozenset({"Bash", "Edit", "Glob", "Grep", "NotebookEdit", "Read", "Write"})

# instructions/written_language_instructions.md bans em dashes in prose and arrows outside
# diagrams, mapping tables, code, and command output. That rule governs every document this
# library publishes as guidance, and nothing enforced it: two reference files had already
# drifted past it before this check existed. Fenced blocks, inline code spans, and table
# rows are removed before the search, so a document that quotes a banned character as an
# example of what to avoid still passes.
PROSE_MARKERS = (("—", "em dash"), ("→", "arrow"))

# The prose this repository writes about itself. Eval fixtures are deliberately flawed
# inputs and eval results are verbatim evidence of what an agent wrote, so neither is held
# to this rule; the hand-written README of an eval suite is.
PROSE_GLOBS = (
    "README.md",
    "SECURITY.md",
    "instructions/*.md",
    "skills/**/*.md",
    AGENT_TEMPLATE_GLOB,
    "evals/README.md",
    "evals/*/README.md",
)

# Leading whitespace is allowed on both fences: a fenced block nested in a list item is
# indented, and anchoring at column zero would leave its contents scanned as prose. Both
# CommonMark fence characters are accepted, and the closing fence has to repeat the opening
# one, so a tilde block holding backticks is still closed where its author closed it.
FENCED_BLOCK = re.compile(
    r"^[ \t]*(?P<fence>```|~~~).*?^[ \t]*(?P=fence)", re.MULTILINE | re.DOTALL
)

INLINE_CODE = re.compile(r"`[^`]*`")

# The inflated vocabulary instructions/written_language_instructions.md rules out, restricted
# to the entries that carry no technical meaning in this repository's subject matter. `harness`
# and `elevate` are deliberately absent: "test harness" and "privilege elevation" are the
# domain's own terms, and that document says a term of art keeps its spelling. A word named as
# an example rather than used is written in backticks, which the code-span strip above exempts.
BANNED_WORDS = (
    "beacon",
    "cutting-edge",
    "delve",
    "empower",
    "ever-evolving",
    "facilitate",
    "foster",
    "game changer",
    "intricate",
    "landscape",
    "leverage",
    "meticulous",
    "multifaceted",
    "paradigm shift",
    "paramount",
    "pivotal",
    "realm",
    "robust",
    "seamless",
    "streamline",
    "supercharge",
    "synergy",
    "tapestry",
    "transformative",
    "underpinnings",
    "underscore",
    "utilize",
)

# Trailing \w* so an inflected form is caught too: "utilizes", "leveraging", "underscores".
BANNED_WORD = re.compile(
    r"\b(?:" + "|".join(re.escape(word) for word in BANNED_WORDS) + r")\w*",
    re.IGNORECASE,
)

# instructions/written_language_instructions.md requires the imperative and the third person in
# instructional and reference text. The two exemptions it grants, quoted material and the title
# of a cited work, are removed before the search: a Markdown link destroys its own link text, and
# a double-quoted span covers both a quoted example and a quoted probe prompt. The pronoun "I" is
# matched case-sensitively so that a single-letter flag such as `env -i` is not a finding.
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")

QUOTED_SPAN = re.compile(r'"[^"]*"')

SECOND_AND_FIRST_PERSON = re.compile(
    r"(?i:\b(?:we|us|our|ours|my|me|you|your|yours)\b)|\bI\b(?!/)",
)

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

# The bounded verify-fix loop, in the wording every skill must carry. README.md requires
# this block to be copied rather than paraphrased, so that the bound means the same thing
# in every skill; without a check, the only thing holding the wording together is whoever
# last copied it, and it had already drifted three ways before this check existed.
CANONICAL_VERIFY_LOOP = """
- Baseline the loop at 3 attempts.
- Continue past 3 only while making measurable progress, meaning each cycle ends with
  strictly fewer findings than the one before it.
- Stop early, before 3 attempts, if the loop is oscillating: the same findings recur, the
  count stops dropping, or a fix for one finding reintroduces another.
- When stopping for either reason, report to the user rather than proceeding or silently
  giving up. Name the failing check, include its output, and state what was tried.
"""

VERIFY_LOOP_ANCHOR = "- Baseline the loop at 3 attempts."
VERIFY_LOOP_TERMINATOR = "state what was tried."

# A testing skill counts failing tests, not findings, and saying otherwise would make the
# loop read wrong in the skill that needs it clearest. That substitution is the only
# licensed deviation: both spellings normalise to one before the comparison, so every
# other word still has to match exactly.
VERIFY_LOOP_SYNONYMS = (
    ("failing test", "failing check"),
    ("failures", "findings"),
    ("failure", "finding"),
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


def normalise_verify_loop(text: str) -> str:
    """Reduce a verify-loop block to the form the canonical comparison is made against.

    Collapses all whitespace, so a skill may wrap and indent the block to suit the
    surrounding section, and folds the licensed testing-skill synonyms onto one spelling.
    Everything else is compared verbatim.
    """
    collapsed = " ".join(text.split()).lower()
    for variant, canonical in VERIFY_LOOP_SYNONYMS:
        collapsed = collapsed.replace(variant, canonical)
    return collapsed


def check_verify_loop(body: list[str], errors: list[str]) -> None:
    """Validate that the skill carries the bounded verify-fix loop, in the shared wording."""
    text = "\n".join(body)

    start = text.find(VERIFY_LOOP_ANCHOR)
    if start == -1:
        errors.append(
            "does not state the bounded verify loop; every skill must carry the wording "
            "from README.md, beginning "
            f"{VERIFY_LOOP_ANCHOR!r}"
        )
        return

    end = text.find(VERIFY_LOOP_TERMINATOR, start)
    if end == -1:
        errors.append(
            f"bounded verify loop starts but does not reach {VERIFY_LOOP_TERMINATOR!r}; "
            "it is truncated or reworded"
        )
        return

    found = normalise_verify_loop(text[start : end + len(VERIFY_LOOP_TERMINATOR)])
    expected = normalise_verify_loop(CANONICAL_VERIFY_LOOP)
    if found != expected:
        errors.append(
            "bounded verify loop is reworded; README.md requires it copied verbatim so the "
            "bound means the same thing in every skill. Expected:\n"
            f"{CANONICAL_VERIFY_LOOP.strip()}"
        )


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


def check_capabilities(capabilities: object, errors: list[str]) -> None:
    """Check that a skill's capability block has the required shape.

    Shape only. Whether the declaration matches the body is not checkable here and is not
    claimed anywhere: a contributor who adds a command and declares it passes. The block
    exists so that the addition is visible in a four-line diff rather than a four-hundred
    line one, which makes a capability change reviewable rather than impossible.
    """
    if not isinstance(capabilities, dict):
        errors.append(
            f"frontmatter is missing a 'capabilities' mapping with {', '.join(CAPABILITY_KEYS)}"
        )
        return

    unknown = sorted(set(capabilities) - set(CAPABILITY_KEYS))
    if unknown:
        errors.append(f"'capabilities' has unknown key(s): {', '.join(unknown)}")

    for key in CAPABILITY_KEYS:
        if key not in capabilities:
            errors.append(f"'capabilities' is missing '{key}'")
            continue
        value = capabilities[key]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"'capabilities.{key}' must be a list of strings, got {value!r}")
            continue
        if value != sorted(value):
            errors.append(
                f"'capabilities.{key}' must be sorted, so that an addition is one line of diff"
            )

    tools = capabilities.get("tools")
    if isinstance(tools, list):
        outside = sorted({tool for tool in tools if tool not in DECLARABLE_TOOLS})
        if outside:
            errors.append(
                f"'capabilities.tools' names {', '.join(outside)}, which is outside the "
                f"declarable set ({', '.join(sorted(DECLARABLE_TOOLS))}); a tool that reaches "
                "the network or spawns an agent is a decision to make deliberately"
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

    check_description(frontmatter.get("description"), errors, "skill")
    check_capabilities(frontmatter.get("capabilities"), errors)
    check_verify_loop(body, errors)

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


def check_plugin_root(repo_root: Path) -> list[str]:
    """Fail when an entry at the repository root is not on the packaging allowlist.

    Every plugin in the marketplace manifest is sourced from the repository root, so a
    file or directory named for anything Claude Code auto-discovers at a plugin root
    ships into every consuming project. `agents/` is the case this repository already had
    a reason to name: it would install the copy-and-adapt templates as live subagents.
    `commands/`, `hooks/` and `.mcp.json` reach a consumer the same way, and a name added
    by a future release of Claude Code would too, which is why this reads as an allowlist.
    """
    errors: list[str] = []
    for entry in sorted(repo_root.iterdir(), key=lambda path: path.name):
        if entry.name in PLUGIN_ROOT_IGNORED or entry.name in PLUGIN_ROOT_ALLOWED:
            continue
        suffix = "/" if entry.is_dir() else ""
        errors.append(
            f"{entry.name}{suffix}: not on the repository-root allowlist. The marketplace "
            "manifest sources every plugin from here, so Claude Code auto-discovers "
            "agents/, commands/, hooks/ and .mcp.json at this level and installs what it "
            "finds into every consuming project; keep agent templates in agent-templates/, "
            "and add a name to PLUGIN_ROOT_ALLOWED only after checking that Claude Code "
            "does not discover it"
        )
    return errors


def check_plugin_versions(manifest: dict[str, object]) -> list[str]:
    """Check that every plugin entry declares one and the same MAJOR.MINOR.PATCH version.

    They ship from one repository at one tag, so differing versions would be a claim this
    repository cannot make true, and a missing one makes every commit a release.
    """
    errors: list[str] = []
    versions: set[str] = set()
    plugins = manifest.get("plugins")
    for entry in plugins if isinstance(plugins, list) else []:
        name = entry.get("name", "<unnamed>")
        version = entry.get("version")
        if isinstance(version, str) and PLUGIN_VERSION.match(version):
            versions.add(version)
        else:
            errors.append(
                f"{MARKETPLACE_PATH}: plugin {name!r} declares version {version!r}, must "
                "be a MAJOR.MINOR.PATCH string matching the release tag it ships from"
            )
    if len(versions) > 1:
        errors.append(
            f"{MARKETPLACE_PATH}: plugins declare {len(versions)} different versions "
            f"({', '.join(sorted(versions))}); one repository at one tag is one version"
        )
    return errors


def check_marketplace(repo_root: Path, skills: list[Path]) -> list[str]:
    """Check that the manifest exposes every skill exactly once and declares one version.

    A skill missing from the manifest is invisible to any project that installs this
    library as a Claude Code plugin, which no other check would catch. The version is
    checked here for a related reason: a plugin entry without one turns every commit into
    a release, so a consumer who followed the pinning instructions in README.md would be
    pinning to a version the manifest never declares.
    """
    errors: list[str] = []
    manifest_path = repo_root / MARKETPLACE_PATH
    if not manifest_path.is_file():
        return [f"{MARKETPLACE_PATH}: missing"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{MARKETPLACE_PATH}: does not parse as JSON: {exc}"]

    errors += check_plugin_versions(manifest)

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


def check_prose_markers(repo_root: Path) -> list[str]:
    """Return every banned prose marker found in the documents this library publishes.

    Code is exempt by the rule itself, so fenced blocks and inline code spans are removed
    before the search. Fenced blocks are replaced by their own newline count so the line
    numbers reported still match the file. Table rows are skipped, since the rule allows an
    arrow in a mapping table.
    """
    errors: list[str] = []
    paths = sorted({path for glob in PROSE_GLOBS for path in repo_root.glob(glob)})
    for path in paths:
        text = FENCED_BLOCK.sub(
            lambda match: "\n" * match.group().count("\n"),
            path.read_text(encoding="utf-8"),
        )
        relative = path.relative_to(repo_root)
        for number, line in enumerate(text.split("\n"), start=1):
            if line.lstrip().startswith("|"):
                continue
            prose = INLINE_CODE.sub("", line)
            errors.extend(
                f"{relative}:{number}: {label} in prose; "
                "instructions/written_language_instructions.md forbids it"
                for marker, label in PROSE_MARKERS
                if marker in prose
            )
            errors.extend(
                f"{relative}:{number}: inflated wording {match.group()!r}; "
                "instructions/written_language_instructions.md rules it out, so use the plain "
                "word, or write it in backticks when naming it as an example"
                for match in BANNED_WORD.finditer(prose)
            )
            impersonal = QUOTED_SPAN.sub("", MARKDOWN_LINK.sub("", prose))
            errors.extend(
                f"{relative}:{number}: first- or second-person {match.group()!r}; "
                "instructions/written_language_instructions.md requires the imperative and the "
                "third person outside quoted material and cited titles"
                for match in SECOND_AND_FIRST_PERSON.finditer(impersonal)
            )
    return errors


def check_reference_toc(repo_root: Path) -> list[str]:
    """Check that every long reference file carries a Contents list matching its headings.

    README.md requires one past TOC_REQUIRED_LINES lines, so an agent that previews the file
    rather than reading it whole still sees everything it covers. That is also why the list has
    to precede every other section: one placed further down is outside the screen the preview
    shows. The entries are compared against the headings that follow, because a list that has
    drifted from the document sends the reader looking for a section that is no longer there.
    """
    errors: list[str] = []
    for path in sorted(repo_root.glob(REFERENCE_GLOB)):
        relative = path.relative_to(repo_root)
        raw = path.read_text(encoding="utf-8")
        if len(raw.splitlines()) <= TOC_REQUIRED_LINES:
            continue

        # A fenced block can hold a line that looks like a heading, so drop the blocks first.
        lines = FENCED_BLOCK.sub(lambda match: "\n" * match.group().count("\n"), raw).split("\n")

        headings = [
            match.group(1).strip()
            for match in (SECTION_HEADING.match(line) for line in lines)
            if match and match.group(1).strip() != "Contents"
        ]

        if TOC_HEADING not in lines:
            errors.append(
                f"{relative}: is over {TOC_REQUIRED_LINES} lines and has no "
                f"{TOC_HEADING!r} section; README.md requires one listing: "
                f"{', '.join(headings)}"
            )
            continue

        start = lines.index(TOC_HEADING) + 1
        preceding = [
            match.group(1).strip()
            for match in (SECTION_HEADING.match(line) for line in lines[: start - 1])
            if match
        ]
        if preceding:
            errors.append(
                f"{relative}: the {TOC_HEADING!r} section follows {preceding[0]!r}; README.md "
                "places it after the opening paragraph and before the first section, so a partial "
                "read of the file still reaches it"
            )
            continue

        entries: list[str] = []
        for line in lines[start:]:
            if line.startswith("## "):
                break
            entry = TOC_ENTRY.match(line)
            if entry:
                entries.append(entry.group(1).strip())

        if entries != headings:
            errors.append(
                f"{relative}: the Contents list does not match the headings that follow it. "
                f"Listed: {entries}. Found: {headings}"
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


def report_repository_check(errors: list[str], clean_message: str) -> list[str]:
    """Print a repository-wide check's findings, or its clean line, and pass the findings back."""
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print(clean_message)
    return errors


def main() -> int:
    """Check every skill and agent template plus the manifest, and report the results."""
    # stdout is block-buffered when it is not a terminal, and stderr is line-buffered
    # always, so under a pipe or a CI log every finding would print before the pass lines
    # it belongs after. Line buffering puts the two streams back in the order they were
    # written, without merging them into one.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)

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

    manifest_errors = report_repository_check(
        check_marketplace(repo_root, skills) + check_plugin_root(repo_root),
        f"{MARKETPLACE_PATH}: ok",
    )
    reference_errors = report_repository_check(
        check_cross_references(repo_root, skills),
        f"{INSTRUCTIONS_DIR}/: cross-references ok",
    )
    toc_errors = report_repository_check(
        check_reference_toc(repo_root),
        f"references/: every file over {TOC_REQUIRED_LINES} lines lists its own contents",
    )
    prose_errors = report_repository_check(
        check_prose_markers(repo_root),
        "prose: no em dashes, arrows, inflated wording, or first- and second-person address",
    )

    repository_errors = manifest_errors + reference_errors + toc_errors + prose_errors
    if failed or template_failed or repository_errors:
        print(
            f"\n{failed} of {len(skills)} skill(s) failed, "
            f"{template_failed} of {len(templates)} agent template(s) failed, "
            f"{len(manifest_errors)} packaging problem(s), "
            f"{len(reference_errors)} cross-reference problem(s), "
            f"{len(toc_errors)} contents-list problem(s), "
            f"{len(prose_errors)} prose problem(s)",
            file=sys.stderr,
        )
        return 1

    print(f"\nall {len(skills)} skill(s) and {len(templates)} agent template(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
