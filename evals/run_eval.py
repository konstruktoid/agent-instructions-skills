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

Both take `--runs N`, which repeats each run and reports the spread rather than
one draw: tasks report the median with the observed range and flag overlapping
ranges as no reliable difference, and probes take the majority verdict.

`report` renders the graded runs as the Markdown table checked in under
`evals/<skill>/results/`.

Run from the repository root:

    python3 evals/run_eval.py tasks --skill python-secure-coding --runs 3
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
import socket
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence

    # One unit of work handed to `execute`: a task or probe plus everything its runner
    # needs, assembled by the subcommand that schedules it.
    Job = dict[str, Any]
    Worker = Callable[[Job], dict[str, Any]]

EVALS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVALS_DIR.parent

RUN_TIMEOUT_SECONDS = 1800
GRADE_TIMEOUT_SECONDS = 600
DEFAULT_TASK_MODEL = "sonnet"
DEFAULT_TRIGGER_MODEL = "opus"

# Prepended to every task prompt, in both conditions, so it cannot bias the comparison.
# It states a property of the harness the agent cannot otherwise discover: there is no
# interactive turn after this one, so a wakeup scheduled for later never arrives. The
# avl-05 run of 2026-07-25 backgrounded a molecule scenario, scheduled a wakeup to
# collect it, and ended on a mid-loop status line that two assertions were then graded
# against.
TASK_PREAMBLE = (
    "This is a single non-interactive run: no scheduled wakeup will fire and there is no "
    "later turn, so any long-running verification must be awaited in the foreground and "
    "its result reported before you finish.\n\n"
)

# A command that outlives its tool timeout is moved to the background and reported with
# this marker, which is the only handle a finished transcript gives on it.
BACKGROUND_MARKER = re.compile(r"moved to the background \(ID: ([A-Za-z0-9_-]+)\)")

# A later tool result naming that id alongside one of these words is the run observing
# that the work finished. Without one, the background task is still outstanding when the
# transcript ends.
COMPLETION_MARKER = re.compile(r"\b(completed|exited|finished|exit code)\b", re.IGNORECASE)

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

# Written as an escape rather than the literal character, which ruff flags as ambiguous.
RANGE_DASH = "\u2013"

# Resolved once, so the fixture's git calls do not depend on a partial path.
GIT = shutil.which("git") or "git"

# Placeholders the scrubber writes in place of anything that identifies the machine a run
# happened on. Two of them rather than one, because the difference between them is itself
# the evidence: a path under the first stayed inside the run's own directory, and one under
# the second reached out into the real home the run was supposed to be isolated from. A
# single blanket redaction would erase exactly the distinction the isolation results rest on.
REPO_PLACEHOLDER = "/repo"
HOME_PLACEHOLDER = "/home/user"
# Other checkouts on the same machine are named only to say "outside the eval", so the name
# itself is dropped; publishing what else someone has cloned is not evidence of anything.
OTHER_CHECKOUT_PLACEHOLDER = f"{HOME_PLACEHOLDER}/other-checkout"

# Linked into each run's private Claude config directory. Everything else Claude Code
# keeps there is per-run state that the run is free to create for itself.
CREDENTIALS_FILE = ".credentials.json"


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


def isolated_environment(home: Path) -> dict[str, str]:
    """Return the environment overlay confining one run's tool state to `home`.

    Every tool a fixture invokes keeps a cache or an ephemeral directory under `$HOME`,
    so two runs sharing one `$HOME` can see each other's state. The avl-05 autopsy
    records the two paths that actually bit: molecule derives its ephemeral directory
    from the project basename, which is `workspace` in every run and therefore identical
    across them, and role resolution reached a stale `~/.ansible/collections` cache
    instead of the workspace under test. Redirecting only those two would leave every
    other tool sharing state, so each directory the tools consult is redirected here.
    """
    cache = home / ".cache"
    return {
        "HOME": str(home),
        "XDG_CACHE_HOME": str(cache),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_DATA_HOME": str(home / ".local" / "share"),
        "XDG_STATE_HOME": str(home / ".local" / "state"),
        # The autopsy's stale collection cache. ANSIBLE_HOME moves ~/.ansible wholesale;
        # the collections path is set as well because a role resolved from a global cache
        # rather than the workspace is the specific defect that was observed.
        "ANSIBLE_HOME": str(home / ".ansible"),
        "ANSIBLE_COLLECTIONS_PATH": str(home / ".ansible" / "collections"),
        # The autopsy's colliding ephemeral directory. A per-run HOME already separates
        # molecule's default location; setting it explicitly keeps the separation even if
        # that default changes.
        "MOLECULE_EPHEMERAL_DIRECTORY": str(cache / "molecule"),
        "UV_CACHE_DIR": str(cache / "uv"),
        "PIP_CACHE_DIR": str(cache / "pip"),
        "npm_config_cache": str(cache / "npm"),
        # A run must not read the user's global git config, whose hooks and aliases would
        # otherwise apply inside the fixture repository.
        "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
        "TMPDIR": str(home / "tmp"),
        # Claude Code's own config directory is per-run state too: it writes sessions and
        # project records on every invocation. Without this, concurrent runs write the
        # user's real ~/.claude at the same time.
        "CLAUDE_CONFIG_DIR": str(home / ".claude"),
    }


def prepare_run_home(run_dir: Path) -> Path:
    """Create the run's private HOME under its run directory and return it.

    The credentials file is symlinked rather than copied, so a run authenticates without
    a secret being written into the results tree.
    """
    home = run_dir / "home"
    for relative in (
        ".ansible",
        ".cache",
        ".claude",
        ".config",
        ".local/share",
        ".local/state",
        "tmp",
    ):
        (home / relative).mkdir(parents=True, exist_ok=True)
    source = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / CREDENTIALS_FILE
    link = home / ".claude" / CREDENTIALS_FILE
    if source.is_file() and not link.is_symlink():
        link.symlink_to(source)
    return home


def run_environment(home: Path | None = None) -> dict[str, str]:
    """Return the environment for a run, with any harness tool directory on PATH.

    `EVAL_TOOL_BIN` lets the caller provision `ansible-lint`, `zizmor`, or
    `actionlint` outside the user's own PATH and still have runs find them. Passing
    `home` confines the run's tool state to that directory; omitting it leaves the
    ambient environment alone, which is what the harness's own git calls want.
    """
    env = dict(os.environ)
    tool_bin = env.get("EVAL_TOOL_BIN")
    if tool_bin:
        env["PATH"] = f"{tool_bin}{os.pathsep}{env['PATH']}"
    if home is not None:
        env.update(isolated_environment(home))
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


def scrub_rules() -> list[tuple[re.Pattern[str], str]]:
    """Build the ordered substitutions that make run evidence machine-agnostic.

    A transcript records absolute paths, `ls -l` owner columns and hostnames from whichever
    machine the run happened on, none of which is a property of the skill under test. The
    rules are derived from the running environment rather than hardcoded, so they work for
    any contributor, and they are ordered longest-match-first: the repository prefix has to
    go before the bare home directory, and both dash-encoded forms have to go before the
    bare username, whose word boundaries would otherwise match inside them.
    """
    home = str(Path.home())
    repo = str(REPO_ROOT)
    user = Path.home().name
    host = socket.gethostname()

    def dashed(text: str) -> str:
        """Encode a path as Claude Code names its project directory, separators as dashes.

        Every path below therefore appears in a second form that needs the same care.
        """
        return text.replace("/", "-")

    def bounded(text: str) -> str:
        r"""Match a bare name, including where a JSON escape sequence precedes it.

        A transcript is JSON, so a name that starts a captured line appears as `\n<name>`,
        where the character before the name is the `n` of the escape sequence rather than a
        separator. `\b` finds no boundary there and the name survives a scrub that reports
        nothing left to do, so the escapes are spelled out rather than relying on the word
        boundary alone.
        """
        return rf"(?:(?<=\\n)|(?<=\\t)|(?<=\\r)|(?<![0-9A-Za-z_])){re.escape(text)}(?![0-9A-Za-z_])"

    rules = [
        (re.escape(repo), REPO_PLACEHOLDER),
        (re.escape(dashed(repo)), dashed(REPO_PLACEHOLDER)),
        # Any sibling checkout of this repository, named only to say "outside the eval".
        (re.escape(f"{Path(repo).parent}/") + r"[A-Za-z0-9_.-]+", OTHER_CHECKOUT_PLACEHOLDER),
        (re.escape(home), HOME_PLACEHOLDER),
        (re.escape(dashed(home)), dashed(HOME_PLACEHOLDER)),
        # The uid in the scratchpad path Claude Code derives from os.getuid(). Anchored to
        # the path so it cannot reach a model id such as claude-3-5-sonnet.
        (r"/tmp/claude-\d+", "/tmp/claude-uid"),  # noqa: S108
        (bounded(user), "user"),
        (bounded(host), "host"),
        # GitHub echoes the caller's own public address back in this error, so an unauthenticated
        # run that hits the rate limit records the network the machine sits behind. It is the one
        # piece of machine identity that arrives in a response body rather than in a path, which
        # is why no path or name rule above catches it.
        (
            # The v6 branch has to require a colon rather than accept a run of hex digits, or it
            # would match the leading `add` of the placeholder this rule writes and re-expand it
            # on every later pass, costing the scrubber the idempotence that makes it a check.
            (
                r"(API rate limit exceeded for )"
                r"(?:[0-9]{1,3}(?:\.[0-9]{1,3}){3}|[0-9A-Fa-f:]*:[0-9A-Fa-f:]+)"
            ),
            r"\g<1>address",
        ),
    ]
    return [(re.compile(pattern), replacement) for pattern, replacement in rules]


def scrub(text: str, rules: list[tuple[re.Pattern[str], str]] | None = None) -> str:
    """Apply the machine-agnostic substitutions to one blob of run evidence."""
    for pattern, replacement in rules if rules is not None else scrub_rules():
        text = pattern.sub(replacement, text)
    return text


def cmd_scrub(args: argparse.Namespace) -> int:
    """Rewrite stored run evidence so it names no user, host or checkout path.

    Applied to the transcripts, diffs and final responses already committed. It is
    idempotent, so re-running it over a scrubbed tree is a no-op, which is what makes it
    safe to use as a check that nothing unscrubbed has been added.
    """
    root = EVALS_DIR / args.skill / "results" if args.skill else EVALS_DIR
    rules = scrub_rules()
    changed = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".jsonl", ".diff", ".json", ".md", ".txt"}:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        cleaned = scrub(original, rules)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            print(f"scrubbed {path.relative_to(REPO_ROOT)}")
            changed += 1
    print(f"scrubbed {changed} files")
    return 0


def as_text(stream: str | bytes | None) -> str:
    """Return one captured subprocess stream as text, whatever form it arrived in."""
    if isinstance(stream, bytes):
        # A killed run can leave a multibyte character split across the capture boundary,
        # and replacing that one character keeps the rest of the partial transcript.
        return stream.decode("utf-8", errors="replace")
    return stream or ""


def invoke_claude(
    command: Sequence[str],
    cwd: Path,
    stream_path: Path,
    home: Path,
    timeout: int = RUN_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run one `claude -p` subprocess, storing its stream, and return a run record."""
    started = datetime.now(tz=UTC)
    try:
        # The command is built by claude_command from checked-in eval data, and
        # runs with shell=False, so no shell metacharacter reaches an interpreter.
        completed = subprocess.run(  # noqa: S603
            command,
            cwd=cwd,
            env=run_environment(home),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        stdout, stderr = completed.stdout, completed.stderr
        returncode, timed_out = completed.returncode, False
    except subprocess.TimeoutExpired as expired:
        # A timeout hands back whatever had been captured so far, as bytes or as text
        # depending on how far the run got, and the partial transcript is worth keeping.
        stdout, stderr = as_text(expired.stdout), as_text(expired.stderr)
        returncode, timed_out = -1, True

    # Scrubbed on the way to disk, so a transcript is machine-agnostic from the moment it
    # is written and no separate step has to remember to clean it before it is committed.
    stream_path.write_text(scrub(stdout), encoding="utf-8")
    if stderr.strip():
        stream_path.with_suffix(".stderr.txt").write_text(scrub(stderr), encoding="utf-8")

    return {
        "returncode": returncode,
        "timed_out": timed_out,
        "started": started.isoformat(),
        "seconds": round((datetime.now(tz=UTC) - started).total_seconds(), 1),
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


def truncation(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Report whether a run ended with work still outstanding.

    Two states mean the run stopped before it could report: a scheduled wakeup, which
    never fires under non-interactive `claude -p` and so is always unfired, and a
    background command whose completion the transcript never records. A run in either
    state was graded on whatever it had said by then, which for avl-05 on 2026-07-25 was
    a mid-loop status line. Both are read from the transcript alone, so a stored run can
    be classified after the fact.
    """
    wakeups = 0
    started: list[str] = []
    resolved: set[str] = set()
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        for block in message.get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                inputs = block.get("input") or {}
                if block.get("name") == "ScheduleWakeup" or "delaySeconds" in inputs:
                    wakeups += 1
                if block.get("name") == "Bash" and inputs.get("run_in_background"):
                    started.append(f"bash-{len(started)}")
                continue
            if block.get("type") != "tool_result":
                continue
            text = json.dumps(block.get("content", ""))
            started += BACKGROUND_MARKER.findall(text)
            if COMPLETION_MARKER.search(text):
                resolved.update(identifier for identifier in started if identifier in text)

    outstanding = [identifier for identifier in started if identifier not in resolved]
    return {
        "truncated": bool(wakeups or outstanding),
        "scheduled_wakeups": wakeups,
        "outstanding_background": outstanding,
    }


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
        **truncation(events),
    }


def run_grader(command: str, workspace: Path, base_sha: str, home: Path) -> tuple[int, str]:
    """Run one assertion command in the finished workspace and return its exit code and output.

    Graders run under the same private HOME as the run they grade, so an assertion that
    invokes ansible-lint or pytest sees the run's own caches rather than the user's.
    """
    env = run_environment(home)
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
    assertion: dict[str, Any], workspace: Path, facts: dict[str, Any], base_sha: str, home: Path
) -> dict[str, Any]:
    """Grade one assertion, returning its verdict and the evidence behind it."""
    kind = assertion["kind"]
    evidence = ""
    if kind == "workspace_command":
        code, output = run_grader(assertion["command"], workspace, base_sha, home)
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


def prepare_workspace(fixture: Path, destination: Path, home: Path) -> str:
    """Copy a fixture into a fresh git repository and return the baseline commit SHA.

    The commit gives assertions a fixed point to diff against, so "no unrelated
    files changed" is measurable rather than asserted.
    """
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(fixture, destination)
    git_env = run_environment(home)
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


def run_one_task(job: Job) -> dict[str, Any]:
    """Run and grade one (task, condition) pair, writing every artifact under raw/."""
    task, condition = job["task"], job["condition"]
    run_dir: Path = job["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)
    home = prepare_run_home(run_dir)
    workspace = run_dir / "workspace"
    base_sha = prepare_workspace(job["fixture"], workspace, home)

    command = claude_command(
        prompt=TASK_PREAMBLE + task["prompt"],
        model=job["model"],
        plugin_dir=job["plugin_dir"] if condition == "with-skill" else None,
        tools=None,
        budget=TASK_BUDGET_USD,
    )
    # A task may raise its own ceiling. avl-05 boots a systemd container and installs
    # packages inside it, which is what pushed the 2026-07-25 run past the default.
    timeout = int(task.get("timeout_seconds", RUN_TIMEOUT_SECONDS))
    record = invoke_claude(command, workspace, run_dir / "run.jsonl", home, timeout)
    facts = transcript_facts(run_dir / "run.jsonl")
    # Written before grading, because an assertion encoding the skill's "clean, or
    # reported" rule reads ../final-response.md from inside the workspace.
    (run_dir / "final-response.md").write_text(scrub(facts["final_text"]) + "\n", encoding="utf-8")
    graded = [
        grade_assertion(assertion, workspace, facts, base_sha, home)
        for assertion in job["assertions"]
    ]

    outcome = {
        "task": task["id"],
        "condition": condition,
        "run_index": job.get("run_index", 1),
        "model": job["model"],
        "run": record,
        "skills_used": facts["skills_used"],
        "num_turns": facts["num_turns"],
        "cost_usd": facts["cost_usd"],
        "truncated": facts["truncated"],
        "scheduled_wakeups": facts["scheduled_wakeups"],
        "outstanding_background": facts["outstanding_background"],
        # A run the process itself reported as failed. The rate limit rejecting a request
        # mid-run ends `claude -p` with a synthetic message, a non-zero exit and an error
        # result event, having produced a partial transcript that grades like a real run
        # and scores badly. That is a measurement of the quota, not of the skill.
        "aborted": bool(record["returncode"] != 0 or facts["is_error"]),
        "assertions": graded,
        "passed": sum(1 for item in graded if item["passed"]),
        "total": len(graded),
    }
    (run_dir / "grade.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    state = " TRUNCATED" if outcome["truncated"] else ""
    print(f"{task['id']} [{condition}] {outcome['passed']}/{outcome['total']}{state}")
    return outcome


def run_one_trigger(job: Job) -> dict[str, Any]:
    """Run one trigger probe and record whether the skill under test was invoked."""
    probe = job["probe"]
    run_dir: Path = job["run_dir"]
    run_dir.mkdir(parents=True, exist_ok=True)
    home = prepare_run_home(run_dir)
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
    record = invoke_claude(command, workspace, run_dir / "run.jsonl", home)
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
    (run_dir / "final-response.md").write_text(scrub(facts["final_text"]) + "\n", encoding="utf-8")
    verdict = "ok" if outcome["correct"] else "WRONG"
    print(f"{probe['id']} expect={probe['expect']} fired={fired} {verdict}")
    return outcome


def results_root(skill: str, stamp: str) -> Path:
    """Return the raw-artifact directory for one dated run of one skill."""
    return EVALS_DIR / skill / "results" / "raw" / stamp


def today() -> str:
    """Return the current UTC date as YYYY-MM-DD, used to name a results file."""
    return datetime.now(tz=UTC).strftime("%Y-%m-%d")


def record_source_revision(root: Path) -> None:
    """Record the commit the stamp was measured against, beside the runs it graded.

    The date in a stamp's name says when the measurement happened, not what it measured.
    A commit landing later the same day, or an older commit rebased forward, both leave the
    date unchanged, so `check_evals.py` compares revisions instead and needs one written down.

    Both commands run in `REPO_ROOT` rather than wherever the harness was invoked from. The
    subject is the skills this run measures, and a run started from another checkout, or from
    inside one of the workspace repositories this harness builds, would otherwise record a
    revision belonging to something else. A stamp with the wrong revision is worse than one
    with none, because the freshness check has no way to tell the two apart, so a lookup that
    fails stops the run here rather than leaving the provenance to be guessed at later.
    """
    # A fixed argument list, with no shell involved.
    head = subprocess.run(  # noqa: S603
        [GIT, "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if head.returncode != 0:
        message = f"cannot read the revision of {REPO_ROOT}: {head.stderr.strip()}"
        raise SystemExit(message)
    # Unlike the revision, a failure here is recordable: `dirty` below carries the difference
    # between a clean tree, a dirty one, and a state that could not be read.
    status = subprocess.run(  # noqa: S603
        [GIT, "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    root.mkdir(parents=True, exist_ok=True)
    (root / "source-revision.json").write_text(
        json.dumps(
            {
                "revision": head.stdout.strip(),
                # An uncommitted tree means the measured source is in no commit at all, so the
                # revision above is a lower bound on what ran rather than a record of it.
                "dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def execute(jobs: list[Job], worker: Worker, parallel: int) -> list[dict[str, Any]]:
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
    record_source_revision(root)
    plugin_dir = build_plugin(args.skill, root)

    runs = max(1, args.runs)

    # One run keeps the flat <task>/<condition>/ directory the single-run layout has always
    # used, so an existing stamp regrades and reports unchanged. More than one nests each run,
    # and each is graded on its own workspace with no state shared between them.
    jobs = [
        {
            "task": task,
            "condition": condition,
            "model": args.model,
            "plugin_dir": plugin_dir,
            "fixture": skill_dir / task["fixture"],
            "assertions": assertions[task["id"]],
            "run_dir": (
                root / task["id"] / condition
                if runs == 1
                else root / task["id"] / condition / f"run-{index}"
            ),
            "run_index": index,
        }
        for task in tasks
        for condition in CONDITIONS
        for index in range(1, runs + 1)
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
    outcomes.sort(
        key=lambda outcome: (outcome["task"], outcome["condition"], outcome.get("run_index", 1))
    )
    outcomes_path.write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")
    # The documented contract: a failing assertion is a result, but a run that did not
    # execute is a harness failure and must not be mistaken for a completed measurement.
    aborted = [outcome for outcome in outcomes if outcome.get("aborted")]
    if aborted:
        for outcome in aborted:
            print(
                f"ABORTED {outcome['task']} [{outcome['condition']}] "
                f"run {outcome.get('run_index', 1)}",
                file=sys.stderr,
            )
        return 1
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
    # Both layouts: <task>/<condition>/workspace for a single run, and the run-<n> level
    # a repeated measurement adds. Globbing only the first silently wrote no diffs at all
    # for a `--runs N` stamp, which is the evidence those runs exist to leave behind.
    workspaces = set(root.glob("*/*/workspace")) | set(root.glob("*/*/run-*/workspace"))
    for workspace in sorted(workspaces):
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
        # Scrubbed like the transcript: a diff carries absolute paths in its headers.
        (workspace.parent / "workspace.diff").write_text(scrub(diff.stdout), encoding="utf-8")
        written += 1
    print(f"wrote {written} workspace diffs under {root.relative_to(REPO_ROOT)}")
    return 0


def cmd_regrade(args: argparse.Namespace) -> int:
    """Re-grade stored runs against the current assertions, without calling any model.

    Every input a grader needs was kept for as long as the run directory survives: the
    finished workspace, the transcript, and the fixture's baseline commit, which is the
    workspace repository's root commit. Correcting a faulty assertion therefore costs
    nothing and leaves the run artifacts untouched. The workspace is gitignored, so a
    clone regrades from the transcript alone; see `regrade_one`.
    """
    skill_dir = EVALS_DIR / args.skill
    assertions = load_json(skill_dir / "assertions.json")["tasks"]
    root = results_root(args.skill, args.stamp or today())

    outcomes: list[dict[str, Any]] = []
    for task_dir in sorted(path for path in root.iterdir() if path.name in assertions):
        for condition in CONDITIONS:
            # A single-run stamp keeps the workspace directly under the condition; a
            # multi-run one nests it under run-<n>. Regrade whichever layout is on disk.
            condition_dir = task_dir / condition
            run_dirs = sorted(condition_dir.glob("run-*")) or [condition_dir]
            for run_dir in run_dirs:
                outcome = regrade_one(run_dir, task_dir.name, assertions[task_dir.name])
                if outcome is not None:
                    outcomes.append(outcome)

    # Merge rather than overwrite, on the same reasoning as `tasks`: a regrade reaches only
    # the runs still on disk, and one that reached none of them must not silently replace a
    # committed results file with an empty list.
    outcomes_path = root / "task-outcomes.json"
    if outcomes_path.is_file():
        fresh = {
            (outcome["task"], outcome["condition"], outcome.get("run_index", 1))
            for outcome in outcomes
        }
        previous = json.loads(outcomes_path.read_text(encoding="utf-8"))
        outcomes += [
            outcome
            for outcome in previous
            if (outcome["task"], outcome["condition"], outcome.get("run_index", 1)) not in fresh
        ]
    outcomes.sort(
        key=lambda outcome: (outcome["task"], outcome["condition"], outcome.get("run_index", 1))
    )
    outcomes_path.write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")
    return 0


def regrade_one(
    run_dir: Path, task_id: str, assertions: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Regrade one stored run in place and return its outcome, or None when it is absent.

    The assertions are re-run only when the finished workspace is still on disk. It is
    gitignored, so in a fresh clone it never is, and the run is then reclassified from its
    transcript alone: `truncated` and `aborted` are read from `run.jsonl` and the recorded
    return code, neither of which needs the workspace. That backfill is the only way a
    stamp graded before the truncation policy existed can ever report its truncated runs,
    since the workspaces those runs left behind were never committed.
    """
    if not (run_dir / "grade.json").is_file():
        return None
    workspace = run_dir / "workspace"
    facts = transcript_facts(run_dir / "run.jsonl")
    outcome = json.loads((run_dir / "grade.json").read_text(encoding="utf-8"))
    if workspace.is_dir():
        # Recreated when absent: a stamp graded before per-run isolation existed has no
        # home/ directory, and regrading it must not fall back to the user's own.
        home = prepare_run_home(run_dir)
        revision = subprocess.run(  # noqa: S603
            [GIT, "rev-list", "--max-parents=0", "HEAD"],
            cwd=workspace,
            env=run_environment(home),
            check=True,
            capture_output=True,
            text=True,
        )
        base_sha = revision.stdout.split()[0]
        graded = [
            grade_assertion(assertion, workspace, facts, base_sha, home) for assertion in assertions
        ]
        outcome["assertions"] = graded
        outcome["passed"] = sum(1 for item in graded if item["passed"])
        outcome["total"] = len(graded)
    # Classified here as well as at run time, so a stamp graded before this policy
    # existed reports its truncated runs once it is regraded.
    outcome.update(
        {key: facts[key] for key in ("truncated", "scheduled_wakeups", "outstanding_background")}
    )
    outcome["aborted"] = bool(outcome.get("run", {}).get("returncode", 0) != 0 or facts["is_error"])
    (run_dir / "grade.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    state = " TRUNCATED" if outcome["truncated"] else ""
    kept = "" if workspace.is_dir() else " (transcript only, workspace not kept)"
    print(f"{task_id} [{outcome['condition']}] {outcome['passed']}/{outcome['total']}{state}{kept}")
    return outcome


def wrap_prose(text: str, indent: str = "") -> list[str]:
    """Wrap one paragraph of generated report prose to the repository's 100-column rule.

    That rule applies to a generated Markdown file as much as to a hand-written one. Neither a
    hyphen nor a long word is a break point here: an assertion id such as `actions-pinned-by-sha`
    is a code span, and split across two lines Markdown renders the newline as a space, leaving
    a gap in the middle of the id.
    """
    return textwrap.wrap(
        text,
        width=100,
        subsequent_indent=indent,
        break_on_hyphens=False,
        break_long_words=False,
    )


def median(values: list[int]) -> float:
    """Return the median of a non-empty list, averaging the middle pair when even."""
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2


def count(number: float) -> str:
    """Render an assertion count, dropping the decimal when the median is a whole number."""
    return f"{number:g}"


def graded_runs(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the runs of one condition that finished, dropping the ones that did not.

    Two states disqualify a run from the medians. A truncated run was graded on whatever
    it had said before it stopped. An aborted run did not finish at all: the process
    reported failure, which is what the rate limit rejecting a request looks like from
    here. Neither is a measurement of the skill, and both are reported separately rather
    than averaged in.
    """
    return [run for run in runs if not run.get("truncated") and not run.get("aborted")]


def verdict(runs: list[dict[str, Any]]) -> str:
    """Render one condition's assertion tally for the results table.

    One run reads as it always has. Several read as the median with the observed
    range behind it, because the median is what the delta is computed from and the
    range is what says whether the delta means anything. A condition whose every run
    was truncated has no tally to give and says so, rather than reporting the counts
    those runs happened to reach.
    """
    if not runs:
        return "not run"
    finished = graded_runs(runs)
    if not finished:
        state = "aborted" if all(run.get("aborted") for run in runs) else "not measured"
        return f"{state} ({len(runs)} of {len(runs)})"
    total = finished[0]["total"]
    passed = [run["passed"] for run in finished]
    tally = (
        f"{passed[0]}/{total}"
        if len(finished) == 1
        else f"{count(median(passed))}/{total} ({min(passed)}{RANGE_DASH}{max(passed)})"
    )
    notes = [
        f"{sum(1 for run in runs if run.get('truncated'))} truncated",
        f"{sum(1 for run in runs if run.get('aborted'))} aborted",
    ]
    dropped = [note for note in notes if not note.startswith("0 ")]
    return f"{tally}, {', '.join(dropped)}" if dropped else tally


def ranges_overlap(left: list[int], right: list[int]) -> bool:
    """Return True when two observed ranges intersect.

    Overlapping ranges mean at least one pairing of runs shows no difference at all,
    so the difference between the medians is not one the runs support.
    """
    return min(left) <= max(right) and min(right) <= max(left)


def failed_ids(runs: list[dict[str, Any]]) -> list[str]:
    """Return the assertion ids failed by any run of one condition, in assertion order."""
    seen: list[str] = []
    for run in runs:
        for item in run["assertions"]:
            if not item["passed"] and item["id"] not in seen:
                seen.append(item["id"])
    return seen


def cost_section(
    by_task: dict[str, dict[str, list[dict[str, Any]]]], net_delta: float
) -> list[str]:
    """Render what the measured gain cost, per skill.

    A skill that improves nothing has no cost per assertion to report, and dividing by
    zero or by a negative net would manufacture a number that reads as one.
    """
    totals = {
        condition: sum(
            run["cost_usd"] or 0
            for conditions in by_task.values()
            for run in conditions.get(condition, [])
        )
        for condition in CONDITIONS
    }
    baseline, with_skill = totals["baseline"], totals["with-skill"]
    multiplier = f"{with_skill / baseline:.1f}x" if baseline else "n/a"
    if net_delta > 0:
        per_assertion = f"${(with_skill - baseline) / net_delta:.2f}"
    else:
        per_assertion = "n/a, no gain"
    return [
        "## Cost of the measured gain",
        "",
        "| Measure | Value |",
        "|---|---|",
        f"| Total baseline cost | ${baseline:.2f} |",
        f"| Total with-skill cost | ${with_skill:.2f} |",
        f"| Multiplier | {multiplier} |",
        f"| Net assertions gained | {net_delta:+g} |",
        f"| Cost per net assertion gained | {per_assertion} |",
        "",
    ]


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
        fired_count = outcome.get("fired_count", int(outcome["fired"]))
        fired = f"{fired_count}/{passes}" if passes > 1 else str(outcome["fired"])
        correct_cell = "yes" if outcome["correct"] else "NO"
        lines.append(f"| `{outcome['id']}` | {outcome['expect']} | {fired} | {correct_cell} |")
    lines.append("")
    return lines


def task_table(
    by_task: dict[str, dict[str, list[dict[str, Any]]]], runs_per_condition: int
) -> tuple[list[str], float]:
    """Render the task-results table and return it with the net delta it summed."""
    lines = ["## Task results", ""]
    if runs_per_condition > 1:
        lines += [
            f"Each task ran {runs_per_condition} times per condition, each against its own",
            "copy of the fixture and graded on its own. A cell gives the median with the",
            "observed range behind it, and the delta is between the two medians. A delta",
            "marked *no reliable difference* has the two ranges overlapping, so at least one",
            "pairing of runs shows no difference and the medians are not separated by these",
            "runs.",
            "",
        ]
    lines += [
        "| Task | Baseline | With skill | Delta | Skill fired |",
        "|------|----------|------------|-------|-------------|",
    ]
    total_delta: float = 0
    comparable = 0
    for task_id, conditions in by_task.items():
        baseline = graded_runs(conditions.get("baseline", []))
        with_skill = graded_runs(conditions.get("with-skill", []))
        delta = ""
        if baseline and with_skill:
            baseline_passed = [run["passed"] for run in baseline]
            with_skill_passed = [run["passed"] for run in with_skill]
            difference = median(with_skill_passed) - median(baseline_passed)
            total_delta += difference
            comparable += 1
            delta = f"{difference:+g}"
            if len(baseline) > 1 and ranges_overlap(baseline_passed, with_skill_passed):
                delta = f"{delta} (no reliable difference)"
        else:
            # One arm has nothing left to compare, so there is no delta to state. Saying
            # +0 here would read as "the skill changed nothing", which is not what was
            # measured.
            delta = "no comparable runs"
        # Read from every run, truncated ones included: whether the skill loaded is
        # observable however the run ended, and is not part of the delta.
        fired = (
            "yes" if any(run["skills_used"] for run in conditions.get("with-skill", [])) else "no"
        )
        lines.append(
            f"| `{task_id}` | {verdict(conditions.get('baseline', []))} | "
            f"{verdict(conditions.get('with-skill', []))} | {delta} | {fired} |"
        )
    # Only the tasks with both arms graded contributed to the sum, so those are the tasks
    # the sum is across. Counting every task the suite defines would attribute the delta to
    # runs that produced no delta at all.
    if comparable:
        summary = (
            f"Net delta across {comparable} comparable task(s): **{total_delta:+g}** assertions."
        )
    else:
        summary = "No task has both arms graded, so there is no net delta to state."
    lines += ["", summary, ""]
    return lines, total_delta


def aborted_section(by_task: dict[str, dict[str, list[dict[str, Any]]]]) -> list[str]:
    """Name every run the process reported as failed, or say nothing when there are none.

    Unlike a truncated run, an aborted one produced no usable turn at all. The case seen
    here is the five-hour rate limit rejecting a request mid-run, which ends the process
    with an error result after a handful of turns.
    """
    named = [
        f"`{task_id}` [{condition}] run {run.get('run_index', 1)}"
        for task_id, conditions in by_task.items()
        for condition in CONDITIONS
        for run in conditions.get(condition, [])
        if run.get("aborted")
    ]
    if not named:
        return []
    return [
        *wrap_prose(
            f"Aborted runs ({len(named)}): {', '.join(named)}. Each ended with a non-zero "
            "exit or an error result, so the transcript is partial and the score it would "
            "have produced measures where the run stopped. These are excluded from the "
            "medians and the delta above."
        ),
        "",
    ]


def undiscriminating(by_task: dict[str, dict[str, list[dict[str, Any]]]]) -> list[str]:
    """Name every task where both conditions scored full marks in every finished run.

    Such a task cannot show a skill effect whatever the skill does: there is no headroom
    above the baseline. evals/README.md's rule is that this measures task difficulty and
    the fixture should be made harder, so the task is named here rather than left to read
    as a success.
    """
    maxed = []
    for task_id, conditions in by_task.items():
        arms = [graded_runs(conditions.get(condition, [])) for condition in CONDITIONS]
        runs = [run for arm in arms for run in arm]
        if all(arms) and all(run["passed"] == run["total"] for run in runs):
            maxed.append(task_id)
    if not maxed:
        return []
    named = ", ".join(f"`{task_id}`" for task_id in maxed)
    return [
        *wrap_prose(
            f"Failed to discriminate: {named}. Every finished run of both conditions scored "
            "full marks, so there was no headroom for the skill to show an effect. This "
            "measures the difficulty of the fixture rather than the skill, and the fixture "
            "is what should change."
        ),
        "",
    ]


def truncated_section(by_task: dict[str, dict[str, list[dict[str, Any]]]]) -> list[str]:
    """Name every truncated run under the table, or record that there were none."""
    named = [
        f"`{task_id}` [{condition}] run {run.get('run_index', 1)}"
        for task_id, conditions in by_task.items()
        for condition in CONDITIONS
        for run in conditions.get(condition, [])
        if run.get("truncated")
    ]
    if not named:
        return ["Truncated runs: none.", ""]
    return [
        *wrap_prose(
            f"Truncated runs ({len(named)}): {', '.join(named)}. Each ended with background "
            "work outstanding or a scheduled wakeup that cannot fire under non-interactive "
            "`claude -p`, so it was graded on whatever it had said by then. These are "
            "excluded from the medians and the delta above."
        ),
        "",
    ]


def failure_section(
    by_task: dict[str, dict[str, list[dict[str, Any]]]], runs_per_condition: int
) -> list[str]:
    """Render the per-run list of failed assertion ids."""
    lines = ["## Assertions failed, by run", ""]
    if runs_per_condition > 1:
        lines += [
            "An assertion is listed when any run of that condition failed it, so this is the",
            "union across runs rather than one run's result.",
            "",
        ]
    for task_id, conditions in by_task.items():
        for condition in CONDITIONS:
            # Truncated runs are left out here too: an assertion they failed reports
            # where the run stopped, not what the skill did about it.
            runs = conditions.get(condition, [])
            finished = graded_runs(runs)
            failures = failed_ids(finished)
            if runs and not finished:
                # "none" here would read as a clean sweep. A condition with no finished run
                # has no failure list to give, the same distinction `verdict` draws.
                rendered = "not measured"
            else:
                rendered = ", ".join(f"`{name}`" for name in failures) if failures else "none"
            lines += wrap_prose(f"- `{task_id}` [{condition}]: {rendered}", indent="  ")
    lines.append("")
    return lines


def render_report(skill: str, stamp: str) -> str:
    """Render the Markdown results file for one dated run of one skill."""
    root = results_root(skill, stamp)
    outcomes_path = root / "task-outcomes.json"
    outcomes = (
        json.loads(outcomes_path.read_text(encoding="utf-8")) if outcomes_path.is_file() else []
    )
    by_task: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for outcome in outcomes:
        by_task.setdefault(outcome["task"], {}).setdefault(outcome["condition"], []).append(outcome)
    runs_per_condition = max(
        (len(runs) for conditions in by_task.values() for runs in conditions.values()), default=1
    )

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

    table, total_delta = task_table(by_task, runs_per_condition)
    lines += table
    lines += truncated_section(by_task)
    lines += aborted_section(by_task)
    lines += undiscriminating(by_task)
    if total_delta == 0:
        lines += [
            "The skill produced no net measurable improvement on these tasks.",
            "",
        ]

    lines += failure_section(by_task, runs_per_condition)

    lines += [
        "## Run cost and length",
        "",
        "| Task | Condition | Turns | Cost (USD) |",
        "|---|---|---|---|",
    ]
    for task_id, conditions in by_task.items():
        for condition in CONDITIONS:
            for outcome in conditions.get(condition, []):
                label = condition
                if runs_per_condition > 1:
                    label = f"{condition} run {outcome.get('run_index', 1)}"
                cost = outcome["cost_usd"] or 0
                lines.append(f"| `{task_id}` | {label} | {outcome['num_turns']} | {cost:.2f} |")
    lines.append("")

    lines += cost_section(by_task, total_delta)
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
    """Build the command-line parser for the subcommands."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Alone in taking no required --skill: scrubbing is a property of the whole results
    # tree, and the useful default is to sweep all of it rather than one skill at a time.
    scrub_parser = subparsers.add_parser("scrub", help=cmd_scrub.__doc__)
    scrub_parser.add_argument("--skill", default="", help="limit to one skill, default all")
    scrub_parser.set_defaults(handler=cmd_scrub)

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
            sub.add_argument(
                "--runs",
                type=int,
                default=1,
                help="runs per condition, reported as median and range (default: 1)",
            )
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
