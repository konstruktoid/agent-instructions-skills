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
- Every incident record under `incidents/` has the sections Evidence, Hypotheses,
  Reproduction, and Disposition in that order. Every repository path its Evidence names
  exists, and it names at least one. The disposition is a known one, every disposition but
  `open` states a run count and the revision it ran at, and only a `regression-case` names a
  task, which tasks.json defines.

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
held to the same rules with four differences: the specification files are `tasks.json` and
`assertions.json` and name the template; a task is either a patch task, which carries the
fixer's `patch` under `patches/<task-id>.patch`, a `request` and a `fixer_summary`, or a brief
task, which carries a `request` or a `question` and the `sources` it names under its fixture,
with the suite stating a `brief_intro` and a `final_line_request`; `tasks.json` may declare the
`comparisons` the suite is measured under, each of which must fit the suite's tasks; and a suite
with no rendered results file yet is reported as unmeasured rather than failed. A template
with no suite is reported the same way.

A suite whose `tasks.json` names an `instructions` file measures an instructions document
rather than a skill. It is held to the same rules with three differences: no skill has to match
the directory, no `trigger-eval.json` exists or is required because a document has no
description to route on, and `tasks.json` declares the `arms` it runs from baseline, doc and
plain, plus the `plain` instruction text when that arm is declared. A suite with no
rendered results file yet is reported as unmeasured rather than failed.

It reports on the checkout it lives in and can be run from anywhere:

    python3 scripts/check_evals.py           # structural errors fail, the rest is reported
    python3 scripts/check_evals.py --strict  # unmeasured skills and staleness fail as well
    python3 scripts/check_evals.py --strict-suite NAME  # the same, for the findings on NAME only

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
BRIEF_SUITE_FIELDS = ("brief_intro", "final_line_request")

# The comparisons run_eval.py can run, which must change with its AGENT_COMPARISONS table.
# `anchored-blind` withholds a fixer's summary, so it needs patch tasks; the other two do not.
COMPARISONS = ("anchored-blind", "template-vs-no-agent", "discipline-ablation")
DISCIPLINE_HEADING = "## Reasoning discipline"


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

# The arms an instructions-document suite may declare, which must change with run_eval.py's
# INSTRUCTIONS_ARM_NAMES.
INSTRUCTIONS_ARMS = ("baseline", "doc", "plain")


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


def recorded_runs(suite: Path) -> list[dict[str, Any]]:
    """Return every run any stamp of the suite recorded in its `task-outcomes.json`."""
    runs: list[dict[str, Any]] = []
    for outcomes in sorted((suite / "results" / "raw").glob("*/task-outcomes.json")):
        try:
            loaded = json.loads(outcomes.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(loaded, list):
            runs.extend(run for run in loaded if isinstance(run, dict) and "task" in run)
    return runs


def check_coverage(suite: Path, task_ids: list[str], stale: list[str]) -> None:
    """Report every task the suite defines that no stamp has ever graded to completion.

    An aborted or truncated run is recorded in `task-outcomes.json` but excluded from every
    median, so it does not count as coverage here either: a task whose every run met the usage
    limit has an entry in the file and no measurement behind it.
    """
    runs = recorded_runs(suite)
    recorded = {run["task"] for run in runs}
    graded = {run["task"] for run in runs if not run.get("aborted") and not run.get("truncated")}

    for task_id in task_ids:
        if task_id in graded:
            continue
        if task_id in recorded:
            stale.append(
                f"{task_id}: every recorded run was aborted or truncated, so no stamp has "
                "graded it to completion"
            )
        else:
            stale.append(
                f"{task_id}: defined but never graded in any stamp, so the suite's coverage is "
                "smaller than its task list"
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


def instructions_document(suite: Path) -> str | None:
    """Return the instructions file a suite's tasks.json names, or None for any other suite."""
    try:
        doc = json.loads((suite / "tasks.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    named = doc.get("instructions") if isinstance(doc, dict) else None
    return named if isinstance(named, str) else None


def check_instructions_arms(doc: dict[str, Any], errors: list[str]) -> None:
    """Check the arms an instructions suite declares and the text its plain arm needs."""
    arms = doc.get("arms")
    if (
        not isinstance(arms, list)
        or arms[:1] != ["baseline"]
        or len(set(map(str, arms))) != len(arms)
        or not set(map(str, arms)) <= set(INSTRUCTIONS_ARMS)
    ):
        errors.append(f"tasks.json: arms must start with baseline, from {INSTRUCTIONS_ARMS}")
        return
    plain = doc.get("plain")
    if "plain" not in arms:
        if plain is not None:
            errors.append("tasks.json: a 'plain' instruction, but the plain arm is not declared")
        return
    if not (isinstance(plain, str) and plain.strip()):
        errors.append("tasks.json: the plain arm needs a non-empty 'plain' instruction")


# Names a task id may take, since it becomes a path component, and the names Claude Code loads
# as instructions or settings from anywhere under a working directory.
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
FIXTURE_GUIDANCE_NAMES = frozenset({"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", ".claude"})


def instructions_task_problems(suite: Path, tasks: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Return (task id, problem) for each unsafe task id, guidance file, or symbolic link.

    A guidance file in a fixture would reach the baseline arm as well as the treatment, a
    symbolic link makes the workspace copy read outside the fixture, and an id with a separator
    leaves the results directory.
    """
    found: list[tuple[str, str]] = []
    for task in tasks:
        task_id = str(task.get("id", "<unnamed>"))
        if not SAFE_NAME.fullmatch(task_id):
            found.append((task_id, "the id is not a plain name, so it cannot be a path component"))
            continue
        fixture = suite / str(task.get("fixture", ""))
        if not fixture.is_dir():
            continue
        found.extend(
            (
                task_id,
                f"fixture holds {path.relative_to(fixture)}, which every arm would load or follow",
            )
            for path in sorted(fixture.rglob("*"))
            if path.is_symlink() or path.name in FIXTURE_GUIDANCE_NAMES
        )
    return found


# An incident record ties an observed agent failure to its evidence and to what was done about
# it, in the format evals/README.md states. The link to a task runs from the record to the task
# rather than from tasks.json to the record: editing tasks.json invalidates the suite's latest
# stamp, and recording an incident should not cost a paid re-run.
INCIDENTS_DIR = "incidents"
INCIDENT_SECTIONS = ("Evidence", "Hypotheses", "Reproduction", "Disposition")
INCIDENT_DISPOSITIONS = ("open", "regression-case", "not-reproduced", "declined")
INCIDENT_TASK = re.compile(r"^Task: `([^`]+)`$", re.MULTILINE)
# A rate without the revision it ran at cannot be compared with the next attempt, and a bare
# "reproduced" hides how often, which is what separates a one-off from a pattern.
REPRODUCTION_COUNT = re.compile(r"\b\d+ of \d+ runs\b")
REVISION = re.compile(r"`[0-9a-f]{7,40}`")
# A path under one of these directories, or a file at the repository root, either one with an
# optional `:line` suffix. A root-level name is recognized only when the root holds it, since a
# bare file name in a code span is as likely to be a fixture's file as this repository's.
EVIDENCE_PATH = re.compile(
    r"`((?:evals|scripts|instructions|skills|agent-templates|docs)/[^`\s:]+)(?::\d+)?`"
)
ROOT_EVIDENCE = re.compile(r"`([\w.-]+\.\w+)(?::\d+)?`")
FENCE = re.compile(r"^\s*(```|~~~)")


def incident_sections(text: str) -> list[tuple[str, str]]:
    """Return each `## ` section of a record as (heading, body), in order.

    A heading inside a fenced block is quoted material, such as a transcript line, not a
    section of the record.
    """
    sections: list[tuple[str, list[str]]] = []
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif sections:
            sections[-1][1].append(line)
    return [(heading, "\n".join(body)) for heading, body in sections]


def incident_problems(text: str, task_ids: list[str]) -> list[str]:
    """Return what is wrong with one incident record, or nothing when it holds the format."""
    sections = incident_sections(text)
    headings = [heading for heading, _ in sections if heading in INCIDENT_SECTIONS]
    if headings != list(INCIDENT_SECTIONS):
        return [
            f"sections are {headings}, expected each of {list(INCIDENT_SECTIONS)} once, in order"
        ]
    body = dict(sections)
    problems: list[str] = []

    paths = EVIDENCE_PATH.findall(body["Evidence"]) + [
        name for name in ROOT_EVIDENCE.findall(body["Evidence"]) if (REPO_ROOT / name).is_file()
    ]
    if not paths:
        problems.append("Evidence names no path in the repository, so the failure is a claim")
    problems.extend(
        f"Evidence path {path} is not a file or directory in the checkout"
        for path in paths
        if not (REPO_ROOT / path).resolve().is_relative_to(REPO_ROOT)
        or not (REPO_ROOT / path).exists()
    )

    words = body["Disposition"].split()
    disposition = words[0].strip("`.,") if words else ""
    if disposition not in INCIDENT_DISPOSITIONS:
        problems.append(f"Disposition {disposition!r} is not one of {INCIDENT_DISPOSITIONS}")
    if disposition != "open" and not (
        REPRODUCTION_COUNT.search(body["Reproduction"]) and REVISION.search(body["Reproduction"])
    ):
        problems.append(
            "Reproduction states no 'k of N runs' with a `revision`; only an open record may "
            "lack one"
        )

    named = INCIDENT_TASK.findall(text)
    if disposition == "regression-case" and not named:
        problems.append("a regression-case names the task that reproduces it in a 'Task:' line")
    elif disposition != "regression-case" and named:
        problems.append(f"a 'Task:' line, but only a regression-case names a task: {named}")
    problems.extend(
        f"Task {task_id} is not defined in tasks.json"
        for task_id in named
        if task_id not in task_ids
    )
    return problems


def check_incidents(suite: Path, task_ids: list[str], errors: list[str]) -> None:
    """Check every incident record under the suite's incidents/ directory."""
    directory = suite / INCIDENTS_DIR
    if not directory.is_dir():
        return
    for path in sorted(directory.iterdir()):
        where = f"{INCIDENTS_DIR}/{path.name}"
        if (
            path.is_symlink()
            or not path.is_file()
            or path.suffix != ".md"
            or not SAFE_NAME.fullmatch(path.stem)
        ):
            errors.append(f"{where}: an incident record is a plain-named .md file")
            continue
        errors.extend(
            f"{where}: {problem}"
            for problem in incident_problems(path.read_text(encoding="utf-8"), task_ids)
        )


def check_arm_coverage(suite: Path, arms: list[str], task_ids: list[str], stale: list[str]) -> None:
    """Report each task that some declared arm never graded to completion.

    A stamp with the baseline and the document but not the plain arm still renders, and its
    comparisons against the missing arm would be silently absent.
    """
    graded: dict[str, set[str]] = {}
    for run in recorded_runs(suite):
        if not run.get("aborted") and not run.get("truncated"):
            graded.setdefault(run["task"], set()).add(str(run.get("condition")))
    for task_id in task_ids:
        missing = [arm for arm in arms if arm not in graded.get(task_id, set())]
        if missing and task_id in graded:
            stale.append(f"{task_id}: no completed run in the arm(s) {', '.join(missing)}")


def check_instructions_suite(suite: Path, document: str) -> tuple[list[str], list[str]]:
    """Check one instructions-document suite, returning its structural errors and findings."""
    errors: list[str] = []
    stale: list[str] = []
    target = REPO_ROOT / document
    if not (target.is_file() and target.parent == REPO_ROOT / "instructions"):
        errors.append(f"tasks.json: 'instructions' {document!r} is not a file in instructions/")

    docs: dict[str, dict[str, Any]] = {}
    for name in AGENT_SPEC_FILES:
        doc = load_json(suite / name, errors)
        if doc is None:
            return errors, stale
        docs[name] = doc
    check_spec_headers(suite, docs, errors)
    check_instructions_arms(docs["tasks.json"], errors)

    tasks = scalar_fields(
        object_entries(docs["tasks.json"].get("tasks", []), "tasks.json 'tasks'", errors),
        TASK_FIELDS,
        "tasks.json 'tasks'",
        errors,
    )
    task_ids = [task.get("id", "<unnamed>") for task in tasks]
    check_tasks(suite, tasks, errors)
    errors.extend(
        f"tasks.json {task_id}: {problem}"
        for task_id, problem in instructions_task_problems(suite, tasks)
    )
    check_assertions(docs["assertions.json"].get("tasks", {}), task_ids, errors)
    check_incidents(suite, task_ids, errors)
    check_results(suite, errors, require_rendered=False)
    if rendered_stamps(suite):
        check_coverage(suite, task_ids, stale)
        arms = docs["tasks.json"].get("arms")
        if isinstance(arms, list):
            check_arm_coverage(suite, [str(arm) for arm in arms], task_ids, stale)
        check_freshness(suite, None, stale, ("the instructions document", [target]))
    return errors, stale


def check_suite(suite: Path, skills: dict[str, Path]) -> tuple[list[str], list[str]]:
    """Check one suite, returning its structural errors and its staleness findings."""
    document = instructions_document(suite)
    if document is not None:
        return check_instructions_suite(suite, document)

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
    check_incidents(suite, task_ids, errors)
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


def check_brief_task(suite: Path, task: dict[str, Any], errors: list[str]) -> None:
    """Check a brief task: a request or a question, and sources that exist in its fixture."""
    task_id = task.get("id", "<unnamed>")
    missing = [field for field in ("id", "title", "fixture") if not task.get(field)]
    if missing:
        errors.append(f"tasks.json {task_id}: missing {', '.join(missing)}")
    if bool(task.get("request")) == bool(task.get("question")):
        errors.append(f"tasks.json {task_id}: needs exactly one of request or question")
    sources = task.get("sources", [])
    if not isinstance(sources, list) or not all(isinstance(item, str) for item in sources):
        errors.append(f"tasks.json {task_id}: sources is not a list of paths")
        return
    errors.extend(
        f"tasks.json {task_id}: source {source} does not exist in {task.get('fixture')}"
        for source in sources
        if not (suite / str(task.get("fixture", "")) / source).is_file()
    )


def check_agent_task(suite: Path, task: dict[str, Any], errors: list[str]) -> None:
    """Check one agent task's fields, its fixture, and its patch when it is a patch task."""
    task_id = task.get("id", "<unnamed>")
    patch_task = "patch" in task
    if patch_task:
        missing = [field for field in AGENT_TASK_FIELDS if not task.get(field)]
        if missing:
            errors.append(f"tasks.json {task_id}: missing {', '.join(missing)}")
    else:
        check_brief_task(suite, task, errors)
    checks = [("fixture", f"fixtures/{task_id}", Path.is_dir)]
    if patch_task:
        checks.append(("patch", f"patches/{task_id}.patch", Path.is_file))
    for field, expected, exists in checks:
        if task.get(field) != expected:
            errors.append(
                f"tasks.json {task_id}: {field} is {task.get(field)!r}, expected {expected!r}"
            )
        elif not exists(suite / expected):
            errors.append(f"tasks.json {task_id}: {expected} does not exist")


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
        check_agent_task(suite, task, errors)

    referenced = {task.get("fixture") for task in tasks} | {task.get("patch") for task in tasks}
    for directory, pattern in (("fixtures", "*/"), ("patches", "*.patch")):
        errors.extend(
            f"{directory}/{path.name}: referenced by no task, so nothing runs against it"
            for path in sorted((suite / directory).glob(pattern))
            if f"{directory}/{path.name}" not in referenced
        )


def check_comparisons(
    doc: dict[str, Any], tasks: list[dict[str, Any]], template: Path | None, errors: list[str]
) -> None:
    """Check the comparisons tasks.json declares, and the brief fields the tasks need."""
    declared = doc.get("comparisons", [])
    if not isinstance(declared, list) or not all(isinstance(item, str) for item in declared):
        errors.append("tasks.json: comparisons is not a list of names")
        return
    errors.extend(
        f"tasks.json: comparison {name!r} is not one of {COMPARISONS}"
        for name in declared
        if name not in COMPARISONS
    )
    if len(set(declared)) != len(declared):
        errors.append("tasks.json: duplicate comparisons")
    patch_tasks = [task for task in tasks if "patch" in task]
    if patch_tasks and len(patch_tasks) != len(tasks):
        errors.append("tasks.json: a suite's tasks are all patch tasks or all brief tasks")
    if not patch_tasks:
        errors.extend(
            f"tasks.json: a suite of brief tasks needs {field}"
            for field in BRIEF_SUITE_FIELDS
            if not isinstance(doc.get(field), str) or not doc[field]
        )
        if not declared or "anchored-blind" in declared:
            errors.append(
                "tasks.json: brief tasks have no fixer summary to withhold, so the suite must "
                "declare comparisons without anchored-blind"
            )
    if (
        "discipline-ablation" in declared
        and template is not None
        and DISCIPLINE_HEADING not in template.read_text(encoding="utf-8")
    ):
        errors.append(
            f"tasks.json: discipline-ablation, but the template has no {DISCIPLINE_HEADING}"
        )


def template_skill(template: Path) -> Path | None:
    """Return the skill directory a template's submodule row names, when it names one.

    A template that wraps only an instructions document names none, and is then checked for
    freshness against the template alone.
    """
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
    check_comparisons(docs["tasks.json"], tasks, template, errors)
    check_assertions(docs["assertions.json"].get("tasks", {}), task_ids, errors)
    check_incidents(suite, task_ids, errors)
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
    parser.add_argument(
        "--strict-suite",
        action="append",
        default=[],
        metavar="NAME",
        help="fail on unmeasured and staleness findings for this suite only; repeatable",
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
        + [
            f"{suite.relative_to(REPO_ROOT)}: never run, so nothing has measured this document"
            for suite in suites
            if instructions_document(suite) is not None and not rendered_stamps(suite)
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
    # A suite's findings are prefixed with its path, so a scoped run matches on that prefix.
    scoped = [
        finding
        for finding in unmeasured + stale_total
        if any(
            finding.startswith((f"{EVALS_DIR}/{name}:", f"{EVALS_DIR}/{AGENTS_DIR}/{name}:"))
            for name in args.strict_suite
        )
    ]
    if failed or (args.strict and (unmeasured or stale_total)) or scoped:
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
