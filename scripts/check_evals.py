#!/usr/bin/env python3
"""Check this repository's eval suites against the rules README.md and evals/README.md state.

For every evals/<skill>/ suite, the structural rules are:

- `tasks.json`, `assertions.json`, and `trigger-eval.json` parse, and each names the skill
  its directory is named after.
- The suite defines 4 to 6 tasks, each with an id, a title, a prompt, and a fixture at
  `fixtures/<task-id>` that exists and is not empty. No fixture directory is unreferenced.
- `assertions.json` covers exactly the tasks `tasks.json` defines. Every assertion carries a
  unique id, a known kind, and a `source` naming the line of the skill it comes from. Every
  `workspace_command` parses under `bash -n`, every regex compiles, and every `expect` value
  is one the harness understands.
- `trigger-eval.json` holds 10 probes, 5 expecting a trigger and 5 expecting none.
- The suite has a README and at least one rendered results file, and every raw stamp holding
  graded runs has a rendered `results/<stamp>.md` beside it. A measurement that was run and
  never reported is invisible to every reader of the repository.

Two further checks are reported as staleness rather than as structural errors, because the
fix for each is a paid re-run rather than an edit:

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

It reports on the checkout it lives in and can be run from anywhere:

    python3 scripts/check_evals.py           # structural errors fail, staleness is reported
    python3 scripts/check_evals.py --strict  # staleness fails as well

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

# Directories under evals/ that are harness material rather than a suite.
NOT_A_SUITE = {"probe-sandbox", "__pycache__"}

SPEC_FILES = ("tasks.json", "assertions.json", "trigger-eval.json")

# evals/README.md: "4 to 6 realistic multi-step task prompts".
MIN_TASKS = 4
MAX_TASKS = 6

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


def check_results(suite: Path, errors: list[str]) -> None:
    """Check that the suite is documented and that every graded stamp was rendered."""
    if not (suite / "README.md").is_file():
        errors.append("no README.md stating what the suite measures")
    if not rendered_stamps(suite):
        errors.append("results/: no rendered results file")

    raw = suite / "results" / "raw"
    if not raw.is_dir():
        return
    for stamp in sorted(path for path in raw.iterdir() if path.is_dir()):
        graded = (stamp / "task-outcomes.json").is_file()
        triggers = (stamp / "triggers" / "trigger-outcomes.json").is_file()
        if (graded or triggers) and not (suite / "results" / f"{stamp.name}.md").is_file():
            errors.append(
                f"results/raw/{stamp.name}/: holds graded runs with no results/{stamp.name}.md; "
                "run `run_eval.py report` so the measurement is readable"
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


def check_freshness(suite: Path, skill_dir: Path | None, stale: list[str]) -> None:
    """Report a stamp older than the skill or the specification it was measured against."""
    stamps = rendered_stamps(suite)
    if not stamps or skill_dir is None:
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
        ("the skill", [skill_dir]),
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
        help="fail on staleness as well, not only on structural errors",
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

    failed = 0
    stale_total: list[str] = []
    for suite in suites:
        errors, stale = check_suite(suite, skills)
        relative = suite.relative_to(REPO_ROOT)
        if errors:
            failed += 1
            for error in errors:
                print(f"{relative}: {error}", file=sys.stderr)
        else:
            print(f"{relative}: ok")
        stale_total += [f"{relative}: {finding}" for finding in stale]

    for skill in sorted(set(skills) - {suite.name for suite in suites}):
        print(f"{EVALS_DIR}/{skill}: no suite, so nothing measures this skill")

    for finding in stale_total:
        print(f"stale: {finding}", file=sys.stderr)

    if failed or (args.strict and stale_total):
        print(
            f"\n{failed} of {len(suites)} suite(s) failed, {len(stale_total)} staleness finding(s)",
            file=sys.stderr,
        )
        return 1

    print(f"\nall {len(suites)} suite(s) passed, {len(stale_total)} staleness finding(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
