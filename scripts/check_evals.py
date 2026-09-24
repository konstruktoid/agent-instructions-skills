#!/usr/bin/env python3
"""Check this repository's eval suites against the rules README.md and evals/README.md state.

For every evals/<skill>/ suite, the structural rules are:

- `tasks.json`, `assertions.json`, and `trigger-eval.json` parse, and each names the skill
  its directory is named after.
- The suite defines 4 to 7 tasks, each with an id, a title, a prompt, and a fixture at
  `fixtures/<task-id>` that exists and is not empty. No fixture directory is unreferenced.
- `assertions.json` covers exactly the tasks `tasks.json` defines. Every assertion carries a
  unique id, a known kind, and a `source` naming the line of the skill it comes from. Every
  `workspace_command` parses under `bash -n`, every regex compiles, and every `expect` value
  is one the harness understands.
- `trigger-eval.json` holds 10 probes, 5 expecting a trigger and 5 expecting none.
- The suite has a README and at least one rendered results file, and every raw stamp holding
  graded runs has a rendered `results/<stamp>.md` beside it. A measurement that was run and
  never reported is invisible to every reader of the repository.
- Every graded stamp dated on or after REVISION_REQUIRED_FROM records the revision it
  measured. Stamps written before the field existed are grandfathered, since a stamp cannot
  be given a provenance it never recorded.

Further findings are reported separately rather than as structural errors, because the
fix for each is a paid re-run rather than an edit:

- A skill under skills/ that no suite here measures at all. It is reported rather than
  failed for the same reason as the rest: the structural rules above require a rendered
  results file, so a suite cannot be authored complete without paying for a run first.
- Every task the suite defines has been graded in at least one stamp.
- The skill, its `tasks.json`, and its `assertions.json` are no newer than the latest
  rendered stamp. README.md states that editing any of them invalidates the stamp above it.
  This compares revisions, not dates: a stamp records the commit it measured in
  `results/raw/<stamp>/source-revision.json`, and a change is newer when that commit does
  not contain it. A stamp with no usable revision falls back to comparing committer dates,
  which cannot see a change made later on the day of the run.
- A stamp that recorded a modified working tree, or one that could not read the tree it
  measured at all. Either way it graded source that no commit is known to hold, so the
  measurement cannot be reproduced and the revision comparison above cannot certify it.

Every evals/agents/<template>/ suite measures an agent template rather than a skill, and is
held to the same rules with three differences: the specification files are `tasks.json` and
`assertions.json` and name the template, each task carries the fixer's `patch` under
`patches/<task-id>.patch`, a `request` and a `fixer_summary` in place of a prompt, and a suite
with no rendered results file yet is reported as unmeasured rather than failed. A template
with no suite is reported the same way.

It reports on the checkout it lives in and can be run from anywhere:

    python3 scripts/check_evals.py           # structural errors fail, the rest is reported
    python3 scripts/check_evals.py --strict  # unmeasured skills and staleness fail as well

Exits 0 when everything passes, 1 otherwise. It needs only the standard library.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

BASH = shutil.which("bash") or "bash"
GIT = shutil.which("git") or "git"

# The checkout this validator reports on, resolved from the file rather than from the
# working directory, so it names the same repository wherever the command was run from.
REPO_ROOT = Path(__file__).resolve().parent.parent

EVALS_DIR = Path("evals")

SKILL_GLOB = "skills/*/*/SKILL.md"

# Directories under evals/ that are harness material rather than a suite. `agents` holds
# the agent-template suites, which are checked on their own terms below.
AGENTS_DIR = "agents"
NOT_A_SUITE = {"probe-sandbox", "__pycache__", AGENTS_DIR}

AGENT_TEMPLATE_GLOB = "agent-templates/*.md"
AGENT_SPEC_FILES = ("tasks.json", "assertions.json")
AGENT_TASK_FIELDS = ("id", "title", "fixture", "patch", "request", "fixer_summary")

SPEC_FILES = ("tasks.json", "assertions.json", "trigger-eval.json")

# evals/README.md: "4 to 7 realistic multi-step task prompts".
MIN_TASKS = 4
MAX_TASKS = 7

# evals/README.md: "10 routing probes, 5 in scope and 5 adjacent but out of scope".
PROBE_COUNT = 10
PROBE_SPLIT = 5

# The assertion kinds run_eval.py grades. Anything else raises there at grading time, which
# is after the model calls have been paid for.
COMMAND_KIND = "workspace_command"
REGEX_KINDS = ("transcript_regex", "final_regex", "bash_regex", "skill_used")
COMMAND_EXPECT = ("exit_zero", "non_zero")
REGEX_EXPECT = ("match", "no_match")

# The fields each entry names as text. A field of another type reaches a set, a path join,
# or a regex compile before the check that would report it, so the type is established first.
TASK_FIELDS = ("id", "title", "fixture", "prompt")
ASSERTION_FIELDS = ("id", "kind", "source", "command", "pattern", "expect")
PROBE_FIELDS = ("id", "prompt", "expect")

# A rendered stamp is named for its date; a hand-written analysis beside it, such as
# ansible-verification-loop's avl-05 autopsy, is not and is not treated as one.
STAMP_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    """Read one JSON file, appending to `errors` and returning None when it does not parse."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: {exc}")
        return None
    if not isinstance(doc, dict):
        errors.append(f"{path.name}: top level is {type(doc).__name__}, expected an object")
        return None
    return doc


def object_entries(value: Any, where: str, errors: list[str]) -> list[dict[str, Any]]:  # noqa: ANN401
    """Return the object entries of a list, reporting the container and every entry that is not.

    A specification that parses is not a specification the checks below can read. Reporting
    the shape as an error keeps a malformed file a finding rather than a traceback.
    """
    if not isinstance(value, list):
        errors.append(f"{where}: is {type(value).__name__}, expected a list")
        return []
    entries: list[dict[str, Any]] = []
    for index, entry in enumerate(value):
        if isinstance(entry, dict):
            entries.append(entry)
        else:
            errors.append(f"{where}[{index}]: is {type(entry).__name__}, expected an object")
    return entries


def scalar_fields(
    entries: list[dict[str, Any]], fields: tuple[str, ...], where: str, errors: list[str]
) -> list[dict[str, Any]]:
    """Return the entries whose named fields are text, reporting and dropping the rest.

    `object_entries` establishes that an entry is an object; this establishes that the fields
    the checks below read are the type those checks assume. An id that is a list reaches a set,
    a fixture that is a number reaches a path join, and a pattern that is neither reaches
    `re.compile`, each raising before anything reports the file as malformed.
    """
    valid: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        wrong = [
            f"{name} is {type(entry[name]).__name__}"
            for name in fields
            if name in entry and not isinstance(entry[name], str)
        ]
        if wrong:
            errors.append(f"{where}[{index}]: {', '.join(wrong)}, expected a string")
            continue
        valid.append(entry)
    return valid


def check_spec_headers(suite: Path, docs: dict[str, dict[str, Any]], errors: list[str]) -> None:
    """Check that each specification file names its own suite and states its notes."""
    for name, doc in docs.items():
        if doc.get("skill") != suite.name:
            errors.append(f"{name}: 'skill' is {doc.get('skill')!r}, expected {suite.name!r}")
        if not doc.get("notes"):
            errors.append(f"{name}: no 'notes' block explaining what the suite measures")


def check_tasks(suite: Path, tasks: list[dict[str, Any]], errors: list[str]) -> None:
    """Check task ids, required fields, and the fixture each task starts from."""
    ids = [task.get("id") for task in tasks]
    if len(set(ids)) != len(ids):
        errors.append("tasks.json: duplicate task ids")
    if not MIN_TASKS <= len(tasks) <= MAX_TASKS:
        errors.append(
            f"tasks.json: {len(tasks)} tasks, evals/README.md states {MIN_TASKS} to {MAX_TASKS}"
        )

    for task in tasks:
        task_id = task.get("id", "<unnamed>")
        missing = [field for field in TASK_FIELDS if not task.get(field)]
        if missing:
            errors.append(f"tasks.json {task_id}: missing {', '.join(missing)}")
        expected = f"fixtures/{task_id}"
        if task.get("fixture") != expected:
            errors.append(
                f"tasks.json {task_id}: fixture is {task.get('fixture')!r}, expected {expected!r}"
            )
        fixture = suite / task.get("fixture", "")
        if not fixture.is_dir():
            errors.append(f"tasks.json {task_id}: fixture {task.get('fixture')} does not exist")
        elif not any(fixture.rglob("*")):
            errors.append(f"tasks.json {task_id}: fixture {task.get('fixture')} is empty")

    referenced = {task.get("fixture") for task in tasks}
    fixtures = suite / "fixtures"
    if fixtures.is_dir():
        errors.extend(
            f"fixtures/{path.name}: referenced by no task, so nothing runs against it"
            for path in sorted(path for path in fixtures.iterdir() if path.is_dir())
            if f"fixtures/{path.name}" not in referenced
        )


def check_assertion(task_id: str, assertion: dict[str, Any], errors: list[str]) -> None:
    """Check one assertion's kind, its graded expression, and the expectation it carries."""
    assertion_id = assertion.get("id", "<unnamed>")
    where = f"assertions.json {task_id}/{assertion_id}"
    kind = assertion.get("kind")
    if not assertion.get("source"):
        errors.append(f"{where}: empty 'source'; an assertion names the line of the skill it tests")

    if kind == COMMAND_KIND:
        command = assertion.get("command", "")
        if not command:
            errors.append(f"{where}: no command")
        else:
            # A fixed argument list; the assertion text is passed on stdin, never as a shell word.
            parsed = subprocess.run(  # noqa: S603
                [BASH, "-n"], input=command, text=True, capture_output=True, check=False
            )
            if parsed.returncode != 0:
                errors.append(f"{where}: command does not parse: {parsed.stderr.strip()}")
        if assertion.get("expect", COMMAND_EXPECT[0]) not in COMMAND_EXPECT:
            errors.append(f"{where}: expect {assertion['expect']!r} is not one of {COMMAND_EXPECT}")
    elif kind in REGEX_KINDS:
        pattern = assertion.get("pattern")
        if not pattern:
            errors.append(f"{where}: no pattern")
        else:
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(f"{where}: pattern does not compile: {exc}")
        if assertion.get("expect", REGEX_EXPECT[0]) not in REGEX_EXPECT:
            errors.append(f"{where}: expect {assertion['expect']!r} is not one of {REGEX_EXPECT}")
    else:
        errors.append(f"{where}: unknown kind {kind!r}, which run_eval.py rejects at grading time")


def check_assertions(
    graded: dict[str, list[dict[str, Any]]], task_ids: list[str], errors: list[str]
) -> None:
    """Check that assertions cover exactly the defined tasks, and that each one is gradable."""
    if not isinstance(graded, dict):
        errors.append(f"assertions.json: 'tasks' is {type(graded).__name__}, expected an object")
        return
    errors.extend(
        f"assertions.json: no assertions for task {task_id}"
        for task_id in sorted(set(task_ids) - set(graded))
    )
    errors.extend(
        f"assertions.json: assertions for unknown task {task_id}"
        for task_id in sorted(set(graded) - set(task_ids))
    )

    for task_id, assertions in graded.items():
        seen: set[str] = set()
        where = f"assertions.json {task_id}"
        for assertion in scalar_fields(
            object_entries(assertions, where, errors), ASSERTION_FIELDS, where, errors
        ):
            assertion_id = assertion.get("id", "<unnamed>")
            if assertion_id in seen:
                errors.append(f"assertions.json {task_id}: duplicate assertion id {assertion_id}")
            seen.add(assertion_id)
            check_assertion(task_id, assertion, errors)


def check_triggers(prompts: list[dict[str, Any]], errors: list[str]) -> None:
    """Check the routing probes: count, the in-scope and out-of-scope split, and each prompt."""
    ids = [probe.get("id") for probe in prompts]
    if len(set(ids)) != len(ids):
        errors.append("trigger-eval.json: duplicate probe ids")
    if len(prompts) != PROBE_COUNT:
        errors.append(
            f"trigger-eval.json: {len(prompts)} probes, evals/README.md states {PROBE_COUNT}"
        )

    expects = [str(probe.get("expect")) for probe in prompts]
    unknown = sorted({value for value in expects if value not in {"trigger", "no-trigger"}})
    if unknown:
        errors.append(f"trigger-eval.json: invalid expect values {unknown}")
    if expects.count("trigger") != PROBE_SPLIT or expects.count("no-trigger") != PROBE_SPLIT:
        errors.append(
            f"trigger-eval.json: {expects.count('trigger')} in scope and "
            f"{expects.count('no-trigger')} out of scope, evals/README.md states "
            f"{PROBE_SPLIT} and {PROBE_SPLIT}"
        )
    errors.extend(
        f"trigger-eval.json {probe.get('id', '<unnamed>')}: empty prompt"
        for probe in prompts
        if not probe.get("prompt")
    )


def rendered_stamps(suite: Path) -> list[str]:
    """Return the dated results files the suite has rendered, oldest first."""
    results = suite / "results"
    if not results.is_dir():
        return []
    return sorted(path.stem for path in results.glob("*.md") if STAMP_NAME.match(path.stem))


# The date-comparison fallback in check_freshness is strictly weaker than the revision
# comparison beside it: it cannot see a change made later on the day of the run. Requiring the
# field keeps the weaker signal from spreading to stamps written from here on. The cutoff is
# the first stamp that recorded a revision, so every stamp that predates the field passes and
# every stamp written after it does not.
REVISION_REQUIRED_FROM = "2026-08-20"


def check_results(suite: Path, errors: list[str], *, require_rendered: bool = True) -> None:
    """Check that the suite is documented and that every graded stamp was rendered."""
    if not (suite / "README.md").is_file():
        errors.append("no README.md stating what the suite measures")
    if require_rendered and not rendered_stamps(suite):
        errors.append("results/: no rendered results file")

    raw = suite / "results" / "raw"
    if not raw.is_dir():
        return
    for stamp in sorted(path for path in raw.iterdir() if path.is_dir()):
        graded = (stamp / "task-outcomes.json").is_file()
        triggers = (stamp / "triggers" / "trigger-outcomes.json").is_file()
        if not (graded or triggers):
            continue
        if not (suite / "results" / f"{stamp.name}.md").is_file():
            errors.append(
                f"results/raw/{stamp.name}/: holds graded runs with no results/{stamp.name}.md; "
                "run `run_eval.py report` so the measurement is readable"
            )
        # Only `run_eval.py tasks` writes the file, so a trigger-only stamp cannot carry one.
        # Sliced rather than parsed, because a stamp carries an optional suffix after the
        # date, as in `2026-08-20-repeat`, and only the date orders it against the cutoff.
        if (
            graded
            and stamp.name[:10] >= REVISION_REQUIRED_FROM
            and not (stamp / "source-revision.json").is_file()
        ):
            errors.append(
                f"results/raw/{stamp.name}/: holds graded runs with no source-revision.json, so "
                "its freshness can only be compared by date; re-run `run_eval.py` so the stamp "
                "records the revision it measured"
            )


def check_coverage(suite: Path, task_ids: list[str], stale: list[str]) -> None:
    """Report every task the suite defines that no stamp has ever graded."""
    raw = suite / "results" / "raw"
    graded: set[str] = set()
    if raw.is_dir():
        for outcomes in sorted(raw.glob("*/task-outcomes.json")):
            try:
                runs = json.loads(outcomes.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(runs, list):
                continue
            graded.update(run["task"] for run in runs if isinstance(run, dict) and "task" in run)

    stale.extend(
        f"{task_id}: defined but never graded in any stamp, so the suite's coverage is "
        "smaller than its task list"
        for task_id in task_ids
        if task_id not in graded
    )


def git_output(arguments: list[str]) -> str:
    """Return the trimmed stdout of one git command, or an empty string when it fails.

    The command runs in `REPO_ROOT`, not in the working directory. The paths below are absolute
    ones under this checkout, and git rejects a path outside the repository it was asked in, so
    a run started elsewhere would turn every lookup into the empty string that reads here as
    "nothing changed" and would let the freshness check pass without having compared anything.
    """
    # A fixed argument list built from repository paths, with no shell involved.
    result = subprocess.run(  # noqa: S603
        [GIT, *arguments], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def last_commit(paths: list[Path]) -> tuple[str, str]:
    """Return the revision and date of the newest commit touching any of `paths`.

    The date is the committer date rather than the author date: an author date travels with
    a commit through a rebase or a cherry-pick, so it can be older than the day the change
    actually landed, and a check that reads it would call a stale stamp fresh.
    """
    if not paths:
        return "", ""
    log = git_output(
        ["log", "-1", "--format=%H %cd", "--date=short", "--", *[str(path) for path in paths]]
    )
    revision, _, date = log.partition(" ")
    return revision, date


def stamp_revision(suite: Path, stamp: str) -> tuple[str, bool | None]:
    """Return the revision a stamp recorded as its source, and whether the tree was modified.

    The revision is empty for a stamp written before `run_eval.py` recorded one, and for a
    stamp whose revision no longer exists after a history rewrite.

    The flag has three states rather than two, because `run_eval.py` writes three. True and
    false are the run reporting what it saw. `None` is the run reporting that it could not
    look, which is not evidence of a clean tree, and reading it as one would let a stamp of
    unknown provenance pass the checks below in silence. A stamp with no recorded source at
    all is a different case: it predates the field, the caller falls back to comparing dates,
    and saying its tree state is unknown would add nothing the missing revision does not.
    """
    recorded = suite / "results" / "raw" / stamp / "source-revision.json"
    try:
        doc = json.loads(recorded.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "", False
    if not isinstance(doc, dict):
        return "", False
    flag = doc.get("dirty")
    dirty = flag if isinstance(flag, bool) else None
    revision = doc.get("revision")
    if not isinstance(revision, str) or not revision:
        return "", dirty
    # `--is-ancestor` treats an unknown revision as an error rather than as a false, which
    # would read as staleness. Confirm the object is present before asking about it.
    if git_output(["cat-file", "-t", revision]) != "commit":
        return "", dirty
    return revision, dirty


def contains(revision: str, ancestor: str) -> bool:
    """Report whether `revision` already includes `ancestor`."""
    # A fixed argument list built from resolved revisions, with no shell involved.
    result = subprocess.run(  # noqa: S603
        [GIT, "merge-base", "--is-ancestor", ancestor, revision],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def check_freshness(
    suite: Path,
    skill_dir: Path | None,
    stale: list[str],
    subject: tuple[str, list[Path]] | None = None,
) -> None:
    """Report a stamp older than the skill or the specification it was measured against.

    `subject` replaces the skill as the thing measured, for an agent-template suite, whose
    run depends on the template and on the skill the template reads.
    """
    stamps = rendered_stamps(suite)
    if subject is None:
        if skill_dir is None:
            return
        subject = ("the skill", [skill_dir])
    if not stamps:
        return
    latest = stamps[-1]
    measured, dirty = stamp_revision(suite, latest)

    if dirty is None:
        # The run wrote the stamp without being able to read the tree it measured. Everything
        # below still applies, but none of it can rule out uncommitted edits, so the stamp
        # carries no more provenance than the dirty case does.
        stale.append(
            f"latest stamp {latest} records no readable working-tree state, so whether it "
            "measured uncommitted edits on top of "
            f"{measured[:12] or 'an unrecorded revision'} is unknown; a freshness result "
            "below that reports no change is not evidence that the stamp is current"
        )
    elif dirty:
        # The run recorded a revision, but it measured that revision plus uncommitted edits,
        # and those edits are in no commit for the checks below to read. The ancestor test can
        # still prove a change came after the run; it cannot prove the run included one, since
        # the skill it actually read is not the skill any revision holds.
        stale.append(
            f"latest stamp {latest} was measured against a modified working tree at "
            f"{measured[:12] or 'an unrecorded revision'}, so the source it graded is in no "
            "commit; the measurement cannot be reproduced and a freshness result below that "
            "reports no change is not evidence that the stamp is current"
        )

    for label, paths in (
        subject,
        ("the specification", [suite / "tasks.json", suite / "assertions.json"]),
    ):
        changed_revision, changed = last_commit([path for path in paths if path.exists()])
        if not changed:
            continue
        if measured and changed_revision:
            # The stamp is fresh when the source it ran against already contained the change.
            # This sees a change made later on the day of the run, which comparing the dates
            # cannot, because both sides are the same date.
            outdated = not contains(measured, changed_revision)
            evidence = (
                f"{changed_revision[:12]} of {changed}, which the measured source "
                f"{measured[:12]} does not contain"
            )
        else:
            # No usable revision, so fall back to the dates. A change made after the run on
            # the day of the run reads as fresh here, which is the limit of what a date shows.
            outdated = changed > latest[:10]
            evidence = f"{changed}, by date, since the stamp records no revision to compare"
        if outdated:
            stale.append(
                f"latest stamp {latest} predates a change to {label} in {evidence}; "
                "README.md states that the stamp does not carry forward across it"
            )


def check_suite(suite: Path, skills: dict[str, Path]) -> tuple[list[str], list[str]]:
    """Check one suite, returning its structural errors and its staleness findings."""
    errors: list[str] = []
    stale: list[str] = []

    if suite.name not in skills:
        errors.append("no skills/<category>/<name>/SKILL.md matches this suite directory")

    docs: dict[str, dict[str, Any]] = {}
    for name in SPEC_FILES:
        doc = load_json(suite / name, errors)
        if doc is None:
            return errors, stale
        docs[name] = doc

    check_spec_headers(suite, docs, errors)
    tasks = scalar_fields(
        object_entries(docs["tasks.json"].get("tasks", []), "tasks.json 'tasks'", errors),
        TASK_FIELDS,
        "tasks.json 'tasks'",
        errors,
    )
    task_ids = [task.get("id", "<unnamed>") for task in tasks]
    check_tasks(suite, tasks, errors)
    check_assertions(docs["assertions.json"].get("tasks", {}), task_ids, errors)
    check_triggers(
        scalar_fields(
            object_entries(
                docs["trigger-eval.json"].get("prompts", []), "trigger-eval.json 'prompts'", errors
            ),
            PROBE_FIELDS,
            "trigger-eval.json 'prompts'",
            errors,
        ),
        errors,
    )
    check_results(suite, errors)
    check_coverage(suite, task_ids, stale)
    check_freshness(suite, skills.get(suite.name), stale)
    return errors, stale


def check_agent_tasks(suite: Path, tasks: list[dict[str, Any]], errors: list[str]) -> None:
    """Check an agent suite's tasks: count, fields, and the fixture and patch each starts from."""
    ids = [task.get("id") for task in tasks]
    if len(set(ids)) != len(ids):
        errors.append("tasks.json: duplicate task ids")
    if not MIN_TASKS <= len(tasks) <= MAX_TASKS:
        errors.append(
            f"tasks.json: {len(tasks)} tasks, evals/README.md states {MIN_TASKS} to {MAX_TASKS}"
        )
    for task in tasks:
        task_id = task.get("id", "<unnamed>")
        missing = [field for field in AGENT_TASK_FIELDS if not task.get(field)]
        if missing:
            errors.append(f"tasks.json {task_id}: missing {', '.join(missing)}")
        for field, expected, exists in (
            ("fixture", f"fixtures/{task_id}", Path.is_dir),
            ("patch", f"patches/{task_id}.patch", Path.is_file),
        ):
            if task.get(field) != expected:
                errors.append(
                    f"tasks.json {task_id}: {field} is {task.get(field)!r}, expected {expected!r}"
                )
            elif not exists(suite / expected):
                errors.append(f"tasks.json {task_id}: {expected} does not exist")

    referenced = {task.get("fixture") for task in tasks} | {task.get("patch") for task in tasks}
    for directory, pattern in (("fixtures", "*/"), ("patches", "*.patch")):
        errors.extend(
            f"{directory}/{path.name}: referenced by no task, so nothing runs against it"
            for path in sorted((suite / directory).glob(pattern))
            if f"{directory}/{path.name}" not in referenced
        )


def template_skill(template: Path) -> Path | None:
    """Return the skill directory a template's submodule row names, when it names one."""
    found = re.search(
        r"`<submodule>/(skills/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+)/SKILL\.md`",
        template.read_text(encoding="utf-8"),
    )
    return REPO_ROOT / found.group(1) if found else None


def check_agent_suite(suite: Path, templates: dict[str, Path]) -> tuple[list[str], list[str]]:
    """Check one agent-template suite, returning its structural errors and its findings."""
    errors: list[str] = []
    stale: list[str] = []
    template = templates.get(suite.name)
    if template is None:
        errors.append("no agent-templates/<name>.md matches this suite directory")

    docs: dict[str, dict[str, Any]] = {}
    for name in AGENT_SPEC_FILES:
        doc = load_json(suite / name, errors)
        if doc is None:
            return errors, stale
        if doc.get("template") != suite.name:
            errors.append(f"{name}: 'template' is {doc.get('template')!r}, expected {suite.name!r}")
        if not doc.get("notes"):
            errors.append(f"{name}: no 'notes' block explaining what the suite measures")
        docs[name] = doc

    tasks = scalar_fields(
        object_entries(docs["tasks.json"].get("tasks", []), "tasks.json 'tasks'", errors),
        AGENT_TASK_FIELDS,
        "tasks.json 'tasks'",
        errors,
    )
    task_ids = [task.get("id", "<unnamed>") for task in tasks]
    check_agent_tasks(suite, tasks, errors)
    check_assertions(docs["assertions.json"].get("tasks", {}), task_ids, errors)
    # A rendered results file needs a paid run, so its absence is the unmeasured finding
    # main() reports, as for a skill with no suite, rather than a structural error.
    check_results(suite, errors, require_rendered=False)
    if not rendered_stamps(suite):
        return errors, stale
    check_coverage(suite, task_ids, stale)
    if template is not None:
        skill = template_skill(template)
        paths = [template] + ([skill] if skill is not None else [])
        check_freshness(suite, None, stale, ("the template or the skill it reads", paths))
    return errors, stale


def main() -> int:
    """Check every eval suite and report structural errors and staleness separately."""
    # stdout is block-buffered when it is not a terminal, and stderr is line-buffered
    # always, so under a pipe or a CI log every finding would print before the pass lines
    # it belongs after. Line buffering puts the two streams back in the order they were
    # written, without merging them into one.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail on unmeasured skills and staleness as well, not only on structural errors",
    )
    args = parser.parse_args()

    skills = {path.parent.name: path.parent for path in sorted(REPO_ROOT.glob(SKILL_GLOB))}
    suites = sorted(
        path
        for path in (REPO_ROOT / EVALS_DIR).iterdir()
        if path.is_dir() and path.name not in NOT_A_SUITE
    )
    if not suites:
        print(f"error: no suites found under {EVALS_DIR}/", file=sys.stderr)
        return 1

    templates = {path.stem: path for path in sorted(REPO_ROOT.glob(AGENT_TEMPLATE_GLOB))}
    agents_root = REPO_ROOT / EVALS_DIR / AGENTS_DIR
    agent_suites = sorted(
        path for path in (agents_root.iterdir() if agents_root.is_dir() else []) if path.is_dir()
    )
    checks = [(suite, check_suite(suite, skills)) for suite in suites] + [
        (suite, check_agent_suite(suite, templates)) for suite in agent_suites
    ]

    failed = 0
    stale_total: list[str] = []
    for suite, (errors, stale) in checks:
        relative = suite.relative_to(REPO_ROOT)
        if errors:
            failed += 1
            for error in errors:
                print(f"{relative}: {error}", file=sys.stderr)
        else:
            print(f"{relative}: ok")
        stale_total += [f"{relative}: {finding}" for finding in stale]

    # A skill nothing measures is weaker evidence than a skill measured by a stale stamp, so
    # it is reported on the same footing rather than a quieter one, and --strict fails on it.
    # It is not a structural error because check_results requires a rendered results file,
    # which only a paid run produces.
    unmeasured = (
        [
            f"{EVALS_DIR}/{skill}: no suite, so nothing measures this skill"
            for skill in sorted(set(skills) - {suite.name for suite in suites})
        ]
        + [
            f"{EVALS_DIR}/{AGENTS_DIR}/{template}: no suite, so nothing measures this template"
            for template in sorted(set(templates) - {suite.name for suite in agent_suites})
        ]
        + [
            f"{suite.relative_to(REPO_ROOT)}: never run, so nothing has measured this template"
            for suite in agent_suites
            if not rendered_stamps(suite)
        ]
    )
    for finding in unmeasured:
        print(f"unmeasured: {finding}", file=sys.stderr)

    for finding in stale_total:
        print(f"stale: {finding}", file=sys.stderr)

    counts = (
        f"{len(unmeasured)} unmeasured skill(s) or template(s), "
        f"{len(stale_total)} staleness finding(s)"
    )
    if failed or (args.strict and (unmeasured or stale_total)):
        strict_only = "; --strict fails on the findings above" if not failed else ""
        print(
            f"\n{failed} of {len(checks)} suite(s) failed, {counts}{strict_only}",
            file=sys.stderr,
        )
        return 1

    print(f"\nall {len(checks)} suite(s) passed, {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
