#!/usr/bin/env python3
"""Run this repository's skill evaluations and grade the results.

Two measurements, one per subcommand:

- `tasks` runs every prompt in a skill's `tasks.json` twice, once with the skill
  available and once without, then grades both runs against `assertions.json`.
  The only difference between the two conditions is a single-skill plugin passed
  with `--plugin-dir`, so any delta is attributable to the skill.
- `triggers` runs every prompt in a skill's `trigger-eval.json` with the skill
  available and records whether the agent invoked it, which measures the
  `description` field rather than the skill body.

`report` renders the graded runs as the Markdown table checked in under
`evals/<skill>/results/`.

Run from the repository root:

    python3 evals/run_eval.py tasks --skill python-secure-coding
    python3 evals/run_eval.py triggers --skill python-secure-coding --model opus
    python3 evals/run_eval.py report --skill python-secure-coding

Exits 0 when every run completed, 1 when a run failed to execute. A failing
assertion is a result, not a harness error, and does not change the exit code.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

EVALS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVALS_DIR.parent

RUN_TIMEOUT_SECONDS = 1800
GRADE_TIMEOUT_SECONDS = 600
DEFAULT_TASK_MODEL = "sonnet"
DEFAULT_TRIGGER_MODEL = "opus"

# A trigger probe only has to reveal the routing decision, so it gets read-only tools
# plus Skill, which is the tool whose use is being measured. Omitting Skill here makes
# every probe report "did not fire" no matter what the description says.
TRIGGER_TOOLS = "Skill,Read,Glob,Grep"
TRIGGER_BUDGET_USD = 0.35
TASK_BUDGET_USD = 2.0

# Probes run against a small mixed repository rather than an empty directory. An empty
# directory makes an agent stop and report that there is nothing to work on, which
# suppresses the routing decision the probe exists to observe.
PROBE_SANDBOX = EVALS_DIR / "probe-sandbox"

CONDITIONS = ("baseline", "with-skill")

# Resolved once, so the fixture's git calls do not depend on a partial path.
GIT = shutil.which("git") or "git"


def skill_source(name: str) -> Path:
    """Return the directory holding the named skill's SKILL.md."""
    matches = sorted(REPO_ROOT.glob(f"skills/*/{name}/SKILL.md"))
    if len(matches) != 1:
        message = f"expected exactly one skills/*/{name}/SKILL.md, found {len(matches)}"
        raise SystemExit(message)
    return matches[0].parent


def build_plugin(name: str, workdir: Path) -> Path:
    """Materialize a single-skill Claude Code plugin for the with-skill condition.

    The plugin carries `instructions/` as well, because the skills reference that
    directory through `${CLAUDE_PLUGIN_ROOT}`, exactly as a real plugin install does.
    """
    plugin_dir = workdir / f"plugin-{name}"
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / "skills").mkdir()
    shutil.copytree(skill_source(name), plugin_dir / "skills" / name)
    shutil.copytree(REPO_ROOT / "instructions", plugin_dir / "instructions")
    manifest = {
        "name": f"eval-{name}",
        "description": f"Single-skill plugin isolating {name} for the eval harness.",
        "version": "0.0.1",
    }
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return plugin_dir


def run_environment() -> dict[str, str]:
    """Return the environment for a run, with any harness tool directory on PATH.

    `EVAL_TOOL_BIN` lets the caller provision `ansible-lint`, `zizmor`, or
    `actionlint` outside the user's own PATH and still have runs find them.
    """
    env = dict(os.environ)
    tool_bin = env.get("EVAL_TOOL_BIN")
    if tool_bin:
        env["PATH"] = f"{tool_bin}{os.pathsep}{env['PATH']}"
    return env


def claude_command(
    prompt: str,
    model: str,
    plugin_dir: Path | None,
    tools: str | None,
    budget: float,
) -> list[str]:
    """Build the `claude -p` argument list for one run.

    `--setting-sources project` keeps the user's own settings, and the plugins
    enabled there, out of both conditions, so the with-skill plugin is the only
    difference between them.
    """
    command = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--setting-sources",
        "project",
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--max-budget-usd",
        str(budget),
    ]
    if plugin_dir is not None:
        command += ["--plugin-dir", str(plugin_dir)]
    if tools is not None:
        command += ["--tools", tools]
    else:
        command += ["--permission-mode", "bypassPermissions"]
    return command


def invoke_claude(command: Sequence[str], cwd: Path, stream_path: Path) -> dict[str, Any]:
    """Run one `claude -p` subprocess, storing its stream, and return a run record."""
    started = datetime.now(tz=timezone.utc)
    try:
        # The command is built by claude_command from checked-in eval data, and
        # runs with shell=False, so no shell metacharacter reaches an interpreter.
        completed = subprocess.run(  # noqa: S603
            command,
            cwd=cwd,
            env=run_environment(),
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_SECONDS,
            check=False,
        )
        stdout, stderr, returncode, timed_out = (
            completed.stdout,
            completed.stderr,
            completed.returncode,
            False,
        )
    except subprocess.TimeoutExpired as expired:
        stdout = expired.stdout.decode() if isinstance(expired.stdout, bytes) else expired.stdout
        stderr = expired.stderr.decode() if isinstance(expired.stderr, bytes) else expired.stderr
        stdout, stderr, returncode, timed_out = stdout or "", stderr or "", -1, True

    stream_path.write_text(stdout, encoding="utf-8")
    if stderr.strip():
        stream_path.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")

    return {
        "returncode": returncode,
        "timed_out": timed_out,
        "started": started.isoformat(),
        "seconds": round((datetime.now(tz=timezone.utc) - started).total_seconds(), 1),
    }


def stream_events(stream_path: Path) -> Iterator[dict[str, Any]]:
    """Yield each JSON event from a stream-json transcript, skipping unparsable lines."""
    if not stream_path.is_file():
        return
    for line in stream_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            yield json.loads(stripped)
        except json.JSONDecodeError:
            continue


def tool_uses(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return every tool_use block in the transcript, in order."""
    uses: list[dict[str, Any]] = []
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        uses.extend(
            block
            for block in content
            if isinstance(block, dict) and block.get("type") == "tool_use"
        )
    return uses


def assistant_text(events: Iterable[dict[str, Any]]) -> str:
    """Return the concatenated assistant prose from a transcript."""
    parts: list[str] = []
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or event.get("type") != "assistant":
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        parts.extend(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return "\n".join(parts)


def result_event(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return the terminal result event, or an empty mapping when the run produced none."""
    for event in events:
        if event.get("type") == "result":
            return event
    return {}


def transcript_facts(stream_path: Path) -> dict[str, Any]:
    """Reduce a transcript to the facts the graders assert against."""
    events = list(stream_events(stream_path))
    uses = tool_uses(events)
    result = result_event(events)
    bash_commands = [
        str(use.get("input", {}).get("command", "")) for use in uses if use.get("name") == "Bash"
    ]
    skills_used = [
        str(use.get("input", {}).get("skill") or use.get("input", {}).get("command", ""))
        for use in uses
        if use.get("name") in {"Skill", "SlashCommand"}
    ]
    files_read = [
        str(use.get("input", {}).get("file_path", "")) for use in uses if use.get("name") == "Read"
    ]
    return {
        "assistant_text": assistant_text(events),
        "final_text": str(result.get("result", "")),
        "bash_commands": bash_commands,
        "skills_used": skills_used,
        "files_read": files_read,
        "num_turns": result.get("num_turns"),
        "cost_usd": result.get("total_cost_usd"),
        "is_error": result.get("is_error"),
    }


def run_grader(command: str, workspace: Path, base_sha: str) -> tuple[int, str]:
    """Run one assertion command in the finished workspace and return its exit code and output."""
    env = run_environment()
    env["EVAL_BASE_SHA"] = base_sha
    # The command comes from a checked-in assertions.json in this repository, and
    # a shell is what an assertion such as `! grep -r ...` is written against.
    completed = subprocess.run(  # noqa: S602
        command,
        shell=True,
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        timeout=GRADE_TIMEOUT_SECONDS,
        check=False,
    )
    return completed.returncode, (completed.stdout + completed.stderr)[-4000:]


def grade_assertion(
    assertion: dict[str, Any], workspace: Path, facts: dict[str, Any], base_sha: str
) -> dict[str, Any]:
    """Grade one assertion, returning its verdict and the evidence behind it."""
    kind = assertion["kind"]
    evidence = ""
    if kind == "workspace_command":
        code, output = run_grader(assertion["command"], workspace, base_sha)
        passed = (code == 0) if assertion.get("expect", "exit_zero") == "exit_zero" else code != 0
        evidence = f"exit {code}\n{output}"
    elif kind in {"transcript_regex", "final_regex", "bash_regex", "skill_used"}:
        pattern = re.compile(assertion.get("pattern", ""), re.IGNORECASE | re.MULTILINE)
        if kind == "transcript_regex":
            haystack = facts["assistant_text"]
        elif kind == "final_regex":
            haystack = facts["final_text"]
        elif kind == "bash_regex":
            haystack = "\n".join(facts["bash_commands"])
        else:
            haystack = "\n".join(facts["skills_used"])
        match = pattern.search(haystack)
        passed = bool(match) if assertion.get("expect", "match") == "match" else not match
        evidence = f"match: {match.group(0)[:200]!r}" if match else "no match"
    else:
        message = f"unknown assertion kind {kind!r}"
        raise SystemExit(message)

    return {
        "id": assertion["id"],
        "kind": kind,
        "source": assertion.get("source", ""),
        "passed": passed,
        "evidence": evidence.strip()[:4000],
    }


def prepare_workspace(fixture: Path, destination: Path) -> str:
    """Copy a fixture into a fresh git repository and return the baseline commit SHA.

    The commit gives assertions a fixed point to diff against, so "no unrelated
    files changed" is measurable rather than asserted.
    """
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(fixture, destination)
    git_env = run_environment()
    git_env.update(
        {
            "GIT_AUTHOR_NAME": "eval-harness",
            "GIT_AUTHOR_EMAIL": "eval@localhost",
            "GIT_COMMITTER_NAME": "eval-harness",
            "GIT_COMMITTER_EMAIL": "eval@localhost",
        }
    )
    for args in (
        [GIT, "init", "-q", "-b", "main"],
        [GIT, "add", "-A"],
        [GIT, "commit", "-qm", "fixture baseline"],
    ):
        # Fixed argument lists, shell=False, run inside the freshly copied workspace.
        subprocess.run(args, cwd=destination, env=git_env, check=True, capture_output=True)  # noqa: S603
    revision = subprocess.run(  # noqa: S603
        [GIT, "rev-parse", "HEAD"],
        cwd=destination,
        env=git_env,
        check=True,
        capture_output=True,
        text=True,
    )
    return revision.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    """Read one JSON file, failing with the path when it does not parse."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        message = f"{path}: {exc}"
        raise SystemExit(message) from exc


def run_one_task(job: dict[str, Any]) -> dict[str, Any]:
    """Run and grade one (task, condition) pair, writing every artifact under raw/."""
    task, condition = job["task"], job["condition"]
    run_dir: Path = job["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace = run_dir / "workspace"
    base_sha = prepare_workspace(job["fixture"], workspace)

    command = claude_command(
        prompt=task["prompt"],
        model=job["model"],
        plugin_dir=job["plugin_dir"] if condition == "with-skill" else None,
        tools=None,
        budget=TASK_BUDGET_USD,
    )
    record = invoke_claude(command, workspace, run_dir / "run.jsonl")
    facts = transcript_facts(run_dir / "run.jsonl")
    # Written before grading, because an assertion encoding the skill's "clean, or
    # reported" rule reads ../final-response.md from inside the workspace.
    (run_dir / "final-response.md").write_text(facts["final_text"] + "\n", encoding="utf-8")
    graded = [
        grade_assertion(assertion, workspace, facts, base_sha) for assertion in job["assertions"]
    ]

    outcome = {
        "task": task["id"],
        "condition": condition,
        "model": job["model"],
        "run": record,
        "skills_used": facts["skills_used"],
        "num_turns": facts["num_turns"],
        "cost_usd": facts["cost_usd"],
        "assertions": graded,
        "passed": sum(1 for item in graded if item["passed"]),
        "total": len(graded),
    }
    (run_dir / "grade.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    print(f"{task['id']} [{condition}] {outcome['passed']}/{outcome['total']}")
    return outcome


def run_one_trigger(job: dict[str, Any]) -> dict[str, Any]:
    """Run one trigger probe and record whether the skill under test was invoked."""
    probe = job["probe"]
    run_dir: Path = job["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace = run_dir / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(PROBE_SANDBOX, workspace)
    command = claude_command(
        prompt=probe["prompt"],
        model=job["model"],
        plugin_dir=job["plugin_dir"],
        tools=TRIGGER_TOOLS,
        budget=TRIGGER_BUDGET_USD,
    )
    record = invoke_claude(command, workspace, run_dir / "run.jsonl")
    facts = transcript_facts(run_dir / "run.jsonl")
    fired = any(job["skill"] in used for used in facts["skills_used"])
    outcome = {
        "id": probe["id"],
        "expect": probe["expect"],
        "fired": fired,
        "correct": fired == (probe["expect"] == "trigger"),
        "skills_used": facts["skills_used"],
        "cost_usd": facts["cost_usd"],
        "run": record,
    }
    (run_dir / "outcome.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    (run_dir / "final-response.md").write_text(facts["final_text"] + "\n", encoding="utf-8")
    verdict = "ok" if outcome["correct"] else "WRONG"
    print(f"{probe['id']} expect={probe['expect']} fired={fired} {verdict}")
    return outcome


def results_root(skill: str, stamp: str) -> Path:
    """Return the raw-artifact directory for one dated run of one skill."""
    return EVALS_DIR / skill / "results" / "raw" / stamp


def today() -> str:
    """Return the current UTC date as YYYY-MM-DD, used to name a results file."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def execute(jobs: list[dict[str, Any]], worker: Any, parallel: int) -> list[dict[str, Any]]:  # noqa: ANN401
    """Run jobs through a bounded thread pool, preserving input order in the results."""
    if parallel <= 1:
        return [worker(job) for job in jobs]
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        return list(pool.map(worker, jobs))


def cmd_tasks(args: argparse.Namespace) -> int:
    """Run every task for one skill in both conditions and grade the runs."""
    skill_dir = EVALS_DIR / args.skill
    tasks = load_json(skill_dir / "tasks.json")["tasks"]
    assertions = load_json(skill_dir / "assertions.json")["tasks"]
    if args.task:
        tasks = [task for task in tasks if task["id"] in args.task]
    stamp = args.stamp or today()
    root = results_root(args.skill, stamp)
    plugin_dir = build_plugin(args.skill, root)

    jobs = [
        {
            "task": task,
            "condition": condition,
            "model": args.model,
            "plugin_dir": plugin_dir,
            "fixture": skill_dir / task["fixture"],
            "assertions": assertions[task["id"]],
            "run_dir": root / task["id"] / condition,
        }
        for task in tasks
        for condition in CONDITIONS
    ]
    outcomes = execute(jobs, run_one_task, args.parallel)

    # Merge rather than overwrite: --task runs one subset at a time, and a later batch must
    # not discard the graded runs an earlier one already produced under the same stamp.
    outcomes_path = root / "task-outcomes.json"
    if outcomes_path.is_file():
        fresh = {(outcome["task"], outcome["condition"]) for outcome in outcomes}
        previous = json.loads(outcomes_path.read_text(encoding="utf-8"))
        outcomes += [
            outcome for outcome in previous if (outcome["task"], outcome["condition"]) not in fresh
        ]
    outcomes.sort(key=lambda outcome: (outcome["task"], outcome["condition"]))
    outcomes_path.write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")
    return 0


def majority_outcome(probe: dict[str, Any], passes: list[dict[str, Any]]) -> dict[str, Any]:
    """Reduce repeated passes of one probe to a single verdict by majority.

    Routing is a coin the model tosses each time, so one pass cannot distinguish a
    description that routes a prompt from one that routes it half the time. A probe counts
    correct when it routes correctly in more than half of its passes.
    """
    fired_count = sum(1 for item in passes if item["fired"])
    fired = fired_count * 2 > len(passes)
    return {
        "id": probe["id"],
        "expect": probe["expect"],
        "fired": fired,
        "fired_count": fired_count,
        "runs": len(passes),
        "correct": fired == (probe["expect"] == "trigger"),
        "passes": passes,
        "cost_usd": sum(item["cost_usd"] or 0 for item in passes),
    }


def cmd_triggers(args: argparse.Namespace) -> int:
    """Run every trigger probe for one skill and record the routing decisions."""
    skill_dir = EVALS_DIR / args.skill
    probes = load_json(skill_dir / "trigger-eval.json")["prompts"]
    stamp = args.stamp or today()
    root = results_root(args.skill, stamp) / "triggers"
    plugin_dir = build_plugin(args.skill, root)
    runs = max(1, args.runs)

    # One pass keeps the flat per-probe directory the single-run layout has always used;
    # more than one nests each pass, so the passes stay separately readable.
    jobs = [
        {
            "probe": probe,
            "skill": args.skill,
            "model": args.model,
            "plugin_dir": plugin_dir,
            "run_dir": root / probe["id"] if runs == 1 else root / probe["id"] / f"run-{index}",
        }
        for probe in probes
        for index in range(1, runs + 1)
    ]
    results = execute(jobs, run_one_trigger, args.parallel)

    by_probe: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_probe.setdefault(result["id"], []).append(result)
    outcomes = [majority_outcome(probe, by_probe[probe["id"]]) for probe in probes]

    correct = sum(1 for outcome in outcomes if outcome["correct"])
    print(f"trigger accuracy: {correct}/{len(outcomes)} over {runs} pass(es) per probe")
    (root / "trigger-outcomes.json").write_text(
        json.dumps(outcomes, indent=2) + "\n", encoding="utf-8"
    )
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Write each run's workspace diff, so the evidence is committable.

    A finished workspace is its own git repository and carries build artifacts, a `.venv`
    among them, which together run to gigabytes. What a reader actually needs is the change
    the run made, so each workspace is reduced to a diff against the fixture's baseline
    commit. The workspaces stay on disk, ignored by git, so `regrade` still works.
    """
    root = results_root(args.skill, args.stamp or today())
    written = 0
    for workspace in sorted(root.glob("*/*/workspace")):
        env = run_environment()
        # Only task workspaces are git repositories; trigger probes copy the sandbox
        # without initialising one. Without this guard git walks up to the enclosing
        # repository and stages and diffs that instead, which is not what is wanted.
        if not (workspace / ".git" / "HEAD").is_file():
            continue
        base = subprocess.run(  # noqa: S603
            [GIT, "rev-list", "--max-parents=0", "HEAD"],
            cwd=workspace,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.split()[0]
        # Keep tool output out of the diff and out of the staging cost. A `.venv` alone
        # runs to 160 MB, which `git add -A` would otherwise hash on every snapshot.
        (workspace / ".git" / "info").mkdir(parents=True, exist_ok=True)
        (workspace / ".git" / "info" / "exclude").write_text(
            ".venv/\n.ansible/\n__pycache__/\n.pytest_cache/\n.ruff_cache/\nuv.lock\n",
            encoding="utf-8",
        )
        # Stage everything else, so files the run created appear in the diff too.
        subprocess.run([GIT, "add", "-A"], cwd=workspace, env=env, check=True, capture_output=True)  # noqa: S603
        diff = subprocess.run(  # noqa: S603
            [GIT, "diff", "--cached", base],
            cwd=workspace,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        (workspace.parent / "workspace.diff").write_text(diff.stdout, encoding="utf-8")
        written += 1
    print(f"wrote {written} workspace diffs under {root.relative_to(REPO_ROOT)}")
    return 0


def cmd_regrade(args: argparse.Namespace) -> int:
    """Re-grade stored runs against the current assertions, without calling any model.

    Every input a grader needs was kept: the finished workspace, the transcript, and the
    fixture's baseline commit, which is the workspace repository's root commit. Correcting
    a faulty assertion therefore costs nothing and leaves the run artifacts untouched.
    """
    skill_dir = EVALS_DIR / args.skill
    assertions = load_json(skill_dir / "assertions.json")["tasks"]
    root = results_root(args.skill, args.stamp or today())

    outcomes: list[dict[str, Any]] = []
    for task_dir in sorted(path for path in root.iterdir() if path.name in assertions):
        for condition in CONDITIONS:
            run_dir = task_dir / condition
            workspace = run_dir / "workspace"
            if not (run_dir / "grade.json").is_file() or not workspace.is_dir():
                continue
            revision = subprocess.run(  # noqa: S603
                [GIT, "rev-list", "--max-parents=0", "HEAD"],
                cwd=workspace,
                env=run_environment(),
                check=True,
                capture_output=True,
                text=True,
            )
            base_sha = revision.stdout.split()[0]
            facts = transcript_facts(run_dir / "run.jsonl")
            graded = [
                grade_assertion(assertion, workspace, facts, base_sha)
                for assertion in assertions[task_dir.name]
            ]
            outcome = json.loads((run_dir / "grade.json").read_text(encoding="utf-8"))
            outcome["assertions"] = graded
            outcome["passed"] = sum(1 for item in graded if item["passed"])
            outcome["total"] = len(graded)
            (run_dir / "grade.json").write_text(
                json.dumps(outcome, indent=2) + "\n", encoding="utf-8"
            )
            outcomes.append(outcome)
            print(f"{task_dir.name} [{condition}] {outcome['passed']}/{outcome['total']}")

    (root / "task-outcomes.json").write_text(
        json.dumps(outcomes, indent=2) + "\n", encoding="utf-8"
    )
    return 0


def verdict(outcome: dict[str, Any] | None) -> str:
    """Render one run's assertion tally for the results table."""
    if outcome is None:
        return "not run"
    return f"{outcome['passed']}/{outcome['total']}"


def failed_ids(outcome: dict[str, Any] | None) -> list[str]:
    """Return the ids of the assertions one run failed."""
    if outcome is None:
        return []
    return [item["id"] for item in outcome["assertions"] if not item["passed"]]


def trigger_section(skill: str, stamp: str) -> list[str]:
    """Render the trigger-accuracy table, or a note when no probes were run."""
    path = results_root(skill, stamp) / "triggers" / "trigger-outcomes.json"
    if not path.is_file():
        return ["## Trigger accuracy", "", "Not measured in this run.", ""]

    outcomes = json.loads(path.read_text(encoding="utf-8"))
    correct = sum(1 for outcome in outcomes if outcome["correct"])
    passes = max(outcome.get("runs", 1) for outcome in outcomes)
    lines = [
        "## Trigger accuracy",
        "",
        f"**{correct}/{len(outcomes)}** probes routed correctly.",
        "",
    ]
    if passes > 1:
        lines += [
            f"Each probe ran {passes} times. A probe counts correct when it routes correctly in",
            "more than half of its passes, and the fired column gives the count of passes in",
            "which the skill loaded.",
            "",
        ]
    lines += [
        "| Probe | Expected | Fired | Correct |",
        "|-------|----------|-------|---------|",
    ]
    for outcome in outcomes:
        count = outcome.get("fired_count", int(outcome["fired"]))
        fired = f"{count}/{passes}" if passes > 1 else str(outcome["fired"])
        correct_cell = "yes" if outcome["correct"] else "NO"
        lines.append(f"| `{outcome['id']}` | {outcome['expect']} | {fired} | {correct_cell} |")
    lines.append("")
    return lines


def render_report(skill: str, stamp: str) -> str:
    """Render the Markdown results file for one dated run of one skill."""
    root = results_root(skill, stamp)
    outcomes_path = root / "task-outcomes.json"
    outcomes = (
        json.loads(outcomes_path.read_text(encoding="utf-8")) if outcomes_path.is_file() else []
    )
    by_task: dict[str, dict[str, dict[str, Any]]] = {}
    for outcome in outcomes:
        by_task.setdefault(outcome["task"], {})[outcome["condition"]] = outcome

    lines = [
        f"# {skill} eval results, {stamp}",
        "",
        "Generated by `evals/run_eval.py report`. Every number below is read from a",
        f"`grade.json` under `results/raw/{stamp}/`, and every assertion is a command run in",
        "the finished workspace or a regex over the run transcript.",
        "",
    ]
    # A stamp can hold trigger probes alone, as when only a description is under test. Emit
    # the task sections only when there are graded task runs, rather than a table of zeroes
    # that reads as a measured result.
    if not by_task:
        lines += [
            "No task runs were graded under this stamp; the trigger measurement below stands",
            "on its own.",
            "",
        ]
        return "\n".join(lines + trigger_section(skill, stamp))

    lines += [
        "## Task results",
        "",
        "| Task | Baseline | With skill | Delta | Skill fired |",
        "|------|----------|------------|-------|-------------|",
    ]
    total_delta = 0
    for task_id, conditions in by_task.items():
        baseline, with_skill = conditions.get("baseline"), conditions.get("with-skill")
        delta = ""
        if baseline and with_skill:
            difference = with_skill["passed"] - baseline["passed"]
            total_delta += difference
            delta = f"{difference:+d}"
        fired = "yes" if with_skill and with_skill["skills_used"] else "no"
        lines.append(
            f"| `{task_id}` | {verdict(baseline)} | {verdict(with_skill)} | {delta} | {fired} |"
        )

    lines += ["", f"Net delta across {len(by_task)} tasks: **{total_delta:+d}** assertions.", ""]
    if total_delta == 0 and by_task:
        lines += [
            "The skill produced no net measurable improvement on these tasks.",
            "",
        ]

    lines += ["## Assertions failed, by run", ""]
    for task_id, conditions in by_task.items():
        for condition in CONDITIONS:
            failures = failed_ids(conditions.get(condition))
            rendered = ", ".join(f"`{name}`" for name in failures) if failures else "none"
            # Wrapped to the repository's 100-column Markdown rule, which applies to this
            # generated file as much as to a hand-written one.
            lines.append(
                textwrap.fill(
                    f"- `{task_id}` [{condition}]: {rendered}",
                    width=100,
                    subsequent_indent="  ",
                    break_long_words=False,
                )
            )
    lines.append("")

    lines += [
        "## Run cost and length",
        "",
        "| Task | Condition | Turns | Cost (USD) |",
        "|---|---|---|---|",
    ]
    for task_id, conditions in by_task.items():
        for condition in CONDITIONS:
            outcome = conditions.get(condition)
            if outcome is None:
                continue
            cost = outcome["cost_usd"] or 0
            lines.append(f"| `{task_id}` | {condition} | {outcome['num_turns']} | {cost:.2f} |")
    lines.append("")

    lines += trigger_section(skill, stamp)
    return "\n".join(lines)


def cmd_report(args: argparse.Namespace) -> int:
    """Write the Markdown results file for one dated run of one skill."""
    stamp = args.stamp or today()
    destination = EVALS_DIR / args.skill / "results" / f"{stamp}.md"
    destination.write_text(render_report(args.skill, stamp), encoding="utf-8")
    print(f"wrote {destination.relative_to(REPO_ROOT)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the three subcommands."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, handler, model in (
        ("tasks", cmd_tasks, DEFAULT_TASK_MODEL),
        ("triggers", cmd_triggers, DEFAULT_TRIGGER_MODEL),
        ("report", cmd_report, ""),
        ("regrade", cmd_regrade, ""),
        ("snapshot", cmd_snapshot, ""),
    ):
        sub = subparsers.add_parser(name, help=handler.__doc__)
        sub.add_argument("--skill", required=True, help="skill directory name under evals/")
        sub.add_argument("--stamp", default="", help="results date stamp, defaults to today (UTC)")
        sub.set_defaults(handler=handler)
        if name in {"report", "regrade", "snapshot"}:
            continue
        sub.add_argument("--model", default=model, help=f"model for each run (default: {model})")
        sub.add_argument("--parallel", type=int, default=4, help="concurrent runs (default: 4)")
        if name == "tasks":
            sub.add_argument("--task", action="append", help="run only this task id, repeatable")
        if name == "triggers":
            sub.add_argument(
                "--runs", type=int, default=1, help="passes per probe, majority wins (default: 1)"
            )

    return parser


def main() -> int:
    """Parse arguments and dispatch to the selected subcommand."""
    args = build_parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
