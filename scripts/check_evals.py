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

Run it from the repository root:

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

# A rendered stamp is named for its date; a hand-written analysis beside it, such as
# ansible-verification-loop's avl-05 autopsy, is not and is not treated as one.
STAMP_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}")


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    """Read one JSON file, appending to `errors` and returning None when it does not parse."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: {exc}")
        return None


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
        missing = [field for field in ("id", "title", "fixture", "prompt") if not task.get(field)]
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
        for assertion in assertions:
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
            graded.update(run["task"] for run in runs if "task" in run)

    stale.extend(
        f"{task_id}: defined but never graded in any stamp, so the suite's coverage is "
        "smaller than its task list"
        for task_id in task_ids
        if task_id not in graded
    )


def last_commit_date(paths: list[Path]) -> str:
    """Return the date of the newest commit touching any of `paths`, or an empty string."""
    if not paths:
        return ""
    # A fixed argument list built from repository paths, with no shell involved.
    log = subprocess.run(  # noqa: S603
        [GIT, "log", "-1", "--format=%ad", "--date=short", "--", *[str(path) for path in paths]],
        capture_output=True,
        text=True,
        check=False,
    )
    return log.stdout.strip() if log.returncode == 0 else ""


def check_freshness(suite: Path, skill_dir: Path | None, stale: list[str]) -> None:
    """Report a stamp older than the skill or the specification it was measured against."""
    stamps = rendered_stamps(suite)
    if not stamps or skill_dir is None:
        return
    latest = stamps[-1]

    for label, paths in (
        ("the skill", [skill_dir]),
        ("the specification", [suite / "tasks.json", suite / "assertions.json"]),
    ):
        changed = last_commit_date([path for path in paths if path.exists()])
        if changed and changed > latest[:10]:
            stale.append(
                f"latest stamp {latest} predates a change to {label} on {changed}; "
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
    tasks = docs["tasks.json"].get("tasks", [])
    task_ids = [task.get("id", "<unnamed>") for task in tasks]
    check_tasks(suite, tasks, errors)
    check_assertions(docs["assertions.json"].get("tasks", {}), task_ids, errors)
    check_triggers(docs["trigger-eval.json"].get("prompts", []), errors)
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

    repo_root = Path(__file__).resolve().parent.parent
    skills = {path.parent.name: path.parent for path in sorted(repo_root.glob(SKILL_GLOB))}
    suites = sorted(
        path
        for path in (repo_root / EVALS_DIR).iterdir()
        if path.is_dir() and path.name not in NOT_A_SUITE
    )
    if not suites:
        print(f"error: no suites found under {EVALS_DIR}/", file=sys.stderr)
        return 1

    failed = 0
    stale_total: list[str] = []
    for suite in suites:
        errors, stale = check_suite(suite, skills)
        relative = suite.relative_to(repo_root)
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
