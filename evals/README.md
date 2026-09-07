# Evals

Measurements of whether the skills in this repository change what an agent produces, and
whether their `description` fields route the right tasks to them. A skill that is
structurally correct is not necessarily a skill that does anything; this directory exists to
tell the difference.

## Current state, 2026-08-30

Nothing measured here is current. `scripts/check_evals.py` reports every one of the six suites
as older than the skill or the specification it measured, so the results files below describe
the content as it stood at each stamp rather than as it stands now. Two skills have no suite at
all, `github-repository-security` and `github-organization-governance`, so nothing measures
either. Both states are reported by the checker and neither is answerable by an edit: each needs
a paid re-run, and in the second case a run has to happen before the suite can even be complete,
since a suite with no rendered results file is a structural error.

## Layout

```text
evals/
  run_eval.py            The harness: tasks, triggers, and report subcommands
  probe-sandbox/         A mixed repository the trigger probes run against
  <skill>/
    tasks.json           4 to 7 realistic multi-step task prompts
    assertions.json      Objective pass/fail checks per task, derived from the skill
    trigger-eval.json    10 routing probes, 5 in scope and 5 adjacent but out of scope
    fixtures/<task-id>/  The starting repository for one task
    results/<date>.md    The rendered results
    results/raw/<date>/  Transcripts, workspaces, and per-run grades
```

## How a task eval works

Each task runs twice against an identical copy of its fixture. The only difference between
the two runs is a single-skill plugin passed with `--plugin-dir`, built from the skill under
test plus `instructions/`, exactly as a real plugin install would resolve. Both runs load
`--setting-sources project` so the user's own settings and installed plugins stay out of
both arms. The result is that any difference is attributable to the skill, and `skills_used`
in each `grade.json` records whether it actually fired.

Assertions are of two kinds, and neither asks for a judgment: a `workspace_command` runs in
the finished workspace and passes on exit 0, and a regex kind matches against the run's
transcript, its Bash commands, or its final message. Each carries a `source` field naming the
line of the skill it comes from. `$EVAL_BASE_SHA` is exported to every grading command as the
commit the fixture started at, so "which files did this run change" is answerable.

A task run acts on its workspace without a permission prompt, because `claude -p` cannot
answer one and a denied call would be recorded as a skill that did not act. What bounds the
run is therefore the tool list rather than the permission mode: `TASK_TOOLS` in
`run_eval.py` allows Bash, the file tools, and `Skill`, and nothing else. A fixture is
attacker-shaped input by construction, since every one of them plants the flaw its eval
measures, and the allowlist keeps a run that reads one from reaching the rest of the tool
surface. Pass `--all-tools` to measure a task against every tool the CLI offers instead.

## Running them

```sh
# Tools the fixtures need, kept out of the caller's own PATH
export UV_TOOL_BIN_DIR=/tmp/eval-bin UV_TOOL_DIR=/tmp/eval-tools
uv tool install ansible-lint && uv tool install zizmor
export EVAL_TOOL_BIN=/tmp/eval-bin

# The bash skills grade with shellcheck, and bash-testing's bt-02 with bats. Both come
# from the system package manager rather than uv; without shellcheck the bash assertions
# fail in both arms, and bt-02's suite assertion passes vacuously without bats.

# ansible-verification-loop's avl-07 grades by building the collection, which needs
# ansible-galaxy. `uv tool install ansible-lint` does not expose it, since it publishes
# only its own entry point, so ansible-core is installed as a tool of its own.
uv tool install ansible-core

python3 evals/run_eval.py tasks    --skill python-secure-coding --model sonnet --parallel 5
python3 evals/run_eval.py triggers --skill python-secure-coding --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill python-secure-coding
```

`report` regenerates `results/<date>.md` from the graded runs, so the checked-in results file
is never written by hand.

### The grader review gate

An assertion of kind `workspace_command` is handed to a shell by `run_grader`, in a process whose
HOME holds a symlink to the credentials that authenticate the run. Whoever writes that string
chooses what runs on this machine. `tasks` and `regrade`, the two subcommands that execute one,
therefore refuse to start when a suite's `assertions.json` or `run_eval.py` differs from
`origin/main`, falling back to `main`:

```sh
python3 evals/run_eval.py tasks --skill python-testing
# refusing to grade python-testing: evals/python-testing/assertions.json differs from origin/main
```

The refusal lists the `workspace_command` strings that are new or changed against the baseline,
which is what a review of them consists of. Read those, then pass `--graders-reviewed` to proceed.
The comparison is against the working tree rather than `HEAD`, so it covers a contributor's branch
and a patch applied locally alike, and it fires on uncommitted edits to a suite of one's own. That
is the intended cost: the flag is an assertion that a human read the commands, and it is recorded
in the run's output when it is used.

### What gets committed, and what is stripped from it

A transcript records the absolute paths, `ls -l` owner columns and hostname of whichever
machine the run happened on, none of which is a property of the skill under test. Transcripts,
diffs and final responses are therefore scrubbed as they are written, and `scrub` re-applies
the same substitutions to anything already stored:

```sh
python3 evals/run_eval.py scrub                 # whole results tree
python3 evals/run_eval.py scrub --skill python-secure-coding
```

The substitutions are derived from the environment rather than hardcoded, so they work for any
contributor, and they are deliberately not a single blanket redaction. The repository checkout
becomes `/repo` and everything else under the real home becomes `/home/user`, because the
difference between those two is the evidence: a path under `/repo` stayed inside the run's own
directory, and one under `/home/user` reached out into the home the run was supposed to be
isolated from. Collapsing both to one token would erase exactly what the isolation results are
there to show. Sibling checkouts become `/home/user/other-checkout`, since naming what else
happens to be cloned on the machine proves nothing.

`scrub` is idempotent, so running it over an already-scrubbed tree reports zero changes, which
is what makes it usable as a check before committing results.

A finished workspace is a git repository carrying build artifacts, a `.venv` among them, so it
is gitignored rather than committed. `snapshot` reduces each one to a diff against the fixture's
baseline commit, which is the form the evidence is committed in:

```sh
python3 evals/run_eval.py snapshot --skill python-secure-coding
```

### Correcting a grade without re-running

`regrade` re-scores stored runs against the current `assertions.json` and calls no model, so
fixing a faulty assertion costs nothing and leaves the transcripts untouched:

```sh
python3 evals/run_eval.py regrade --skill python-secure-coding
```

It re-runs the assertion commands only where the workspace is still on disk. In a fresh clone
it is not, and the run is then reclassified from its transcript alone, which is how a stamp
graded before the truncation policy existed comes to report its truncated runs. Follow a
regrade with `report` to rewrite the results file.

### Repeating a measurement

Both measuring subcommands take `--runs N`. A single run cannot separate a skill's effect from
the variance of the model, so anything meant to be read as a difference should be repeated.

```sh
python3 evals/run_eval.py tasks    --skill python-secure-coding --runs 3 --parallel 6
python3 evals/run_eval.py triggers --skill python-secure-coding --runs 3 --parallel 6
```

Each run gets its own directory, `results/raw/<date>/<task>/<condition>/run-<n>/` for tasks and
`results/raw/<date>/triggers/<probe>/run-<n>/` for probes, its own copy of the fixture, and its
own grading. Nothing is shared between them. With `--runs 1` the layout is the flat one it has
always been, so an existing stamp regrades and reports unchanged.

The report then gives each condition as a median with the observed range behind it, and the
delta between the two medians. A delta whose two ranges overlap is marked *no reliable
difference*: at least one pairing of runs shows no difference at all, so the medians are not
separated by the runs that were done. A probe counts correct when it routes correctly in more
than half of its passes.

## Validating a suite

`scripts/check_evals.py` checks every suite in this directory without calling a model:

```sh
python3 scripts/check_evals.py           # structural problems fail, staleness is reported
python3 scripts/check_evals.py --strict  # unmeasured skills and staleness fail as well
```

Structural checks cover what an edit can break: the three specification files parse and name
their own skill, the suite defines 4 to 7 tasks, each fixture exists at `fixtures/<task-id>`
and is referenced, the assertions cover exactly the defined tasks with unique ids and a known
kind, each one carries the `source` line it comes from, each `workspace_command` parses under
`bash -n` and each regex compiles, the probes number 10 in a 5 and 5 split, and every stamp
under `results/raw/` that holds graded runs has a rendered `results/<stamp>.md` beside it.

The last of those exists because a graded stamp with no results file is invisible to every
reader of the repository. `github-actions-security/results/raw/2026-07-28/` held five tasks at
three runs per condition for three weeks before anything reported it.

Four findings are reported separately, and none of them fails the run by default, because an
edit cannot fix any of them:

- A skill under `skills/` with no directory here, so nothing measures it. It is reported rather
  than failed because the structural rules above require a rendered results file, which means the
  suite that would answer the finding cannot be authored complete before a run is paid for.
- A task defined in `tasks.json` that no stamp has ever graded. The suite's coverage is then
  smaller than its task list, which the results file has no way to say.
- A stamp older than the skill directory, `tasks.json`, or `assertions.json` it measured.
  README.md states that such a stamp does not carry forward, and the check is what makes that
  rule visible rather than remembered.
- A stamp that graded a modified working tree, described below. It measured source that is in
  no commit, so nothing can reproduce it and the comparison above cannot certify it.

The freshness check compares revisions rather than dates. A run writes the commit it measured
to `results/raw/<stamp>/source-revision.json`, and the check asks `git merge-base
--is-ancestor` whether that commit already contained the change. A date cannot answer this: a
change committed later on the day of the run carries the same date as the stamp, and a commit
rebased or cherry-picked forward carries an author date older than the day it landed. Stamps
written before the run recorded a revision, and stamps whose revision a history rewrite
removed, fall back to comparing the committer date against the stamp name, and the finding
says which comparison produced it.

The same file records whether the working tree was modified when the run started. A stamp
that graded a modified tree is reported on its own, because the source it measured is in no
commit: the revision it recorded is a lower bound rather than a record, and the comparison
above can still prove a change came afterwards but cannot prove the run included one. Commit
before measuring, and the finding does not arise.

A stamp whose `assertions.json` has changed cannot be repaired by `regrade` once the finished
workspaces are gone, which they are in any clone, since they are gitignored. Re-running the
tasks is the only way to recover the measurement.

Nothing else validates the numbers themselves, because nothing needs to: `report` reads them
from the `grade.json` files and rewrites the results file, so a results file that has been
edited by hand shows up as a diff after a re-render:

```sh
python3 evals/run_eval.py report --skill <skill> --stamp <stamp>
git diff --stat evals/<skill>/results/
```

## Reading the results

The task table gives each run's passed-assertion count in both conditions and the delta
between them. A delta of zero means the skill changed nothing measurable on that task, which
is a result and is reported as one. Because the baseline agent is competent, a task where
both arms score full marks measures task difficulty rather than skill effect, and should be
made harder rather than read as success. The failed-assertion list under each table names
exactly which checks each run missed, and every one of those traces to a `grade.json` holding
the command that was run and the output it produced.

## What a suite is for after the first measurement

The first run answers whether a skill changes anything. What the suite is worth afterwards is
different: it is the only check in this repository that notices when an edit to a skill removes
the behavior the skill was written to produce. Nothing else does. `check_skills.py` confirms the
file is well formed, `markdownlint` confirms it is formatted, and both pass on a skill whose steps
have been gutted.

That makes a suite the gate on a configuration change rather than a one-time measurement. A change
to a `SKILL.md`, to a `description`, or to a hook that backs one alters what every session in
every consuming project does, and it ships without a single failing test. Where a project can
afford the runs, they belong in the pull request that makes the change, with the pass rate as the
merge condition. This repository cannot afford that per pull request: a task eval costs real money
per task per condition, and the cost multiples are in the table in `README.md`. What it does
instead is report staleness, which is `check_evals.py` naming every stamp older than the skill it
measured, so an unmeasured edit is visible rather than prevented.

Each failure a skill was supposed to prevent, and did not, belongs in the suite as a task. A rule
added to a skill after an incident is exactly the kind of rule a later edit removes without anyone
noticing, and a task derived from that incident is what makes the removal fail rather than pass
quietly. Write it the same way as any other: a prompt that reproduces the starting condition, a
fixture that carries the defect, and assertions whose `source` field names the skill lines that
address it.

## Limitations that apply to every result here

- Everything under `results/2026-07-25.md` is one run per condition. Single-run variance is
  uncontrolled there, so a delta of one assertion is not a reliable signal; only larger
  differences are. `--runs N` exists to remove this limitation from later measurements, and the
  3-pass trigger re-run in `github-actions-security/results/2026-07-27.md` shows what it
  catches: a probe recorded as the one routing defect turned out to fire one pass in three,
  while a probe recorded as correct fired every time.
- Task runs used Sonnet, chosen because it leaves room to observe a difference. A stronger
  baseline model does more of the right thing unprompted and compresses the measurement.
- Trigger probes used Sonnet for cost reasons. Routing is model-dependent, so these numbers
  do not transfer directly to a session running a different model.
- The graded workspace is what the run left behind, and a run can stop before it has
  finished saying what it did. Under non-interactive `claude -p` there is no later turn, so
  a scheduled wakeup never fires and a command moved to the background may still be running
  when the process returns. Such a run is now marked `truncated` in its `grade.json`, on two
  signals read from the transcript: a scheduled wakeup, which is by definition unfired here,
  and a background command whose completion the transcript never records. Truncated runs are
  excluded from the medians, the delta, and the failed-assertion list, and are counted and
  named in a "truncated runs" line under the task table, so they are never folded into
  pass or fail. Two measures reduce how often it happens: every task prompt is prefixed with
  a preamble stating that no wakeup will fire and that long-running verification must be
  awaited in the foreground, identically in both conditions so it cannot bias the
  comparison, and a task may raise its own time budget with `timeout_seconds` in
  `tasks.json`, which `avl-05-collection-review` does.
- A run can also fail outright rather than stop early, which is what the five-hour rate
  limit rejecting a request looks like from inside the harness. A run whose process exited
  non-zero, or whose transcript ends in an error result, is marked `aborted` in its
  `grade.json`. Like a truncated run it is excluded from the medians, the delta, and the
  failed-assertion list, and is counted and named in an "aborted runs" line under the task
  table; a condition whose every run aborted is reported as `aborted` rather than given a
  tally. The distinction from `truncated` is worth keeping: a truncated run did the work and
  stopped before saying so, an aborted one never got that far, so re-running it is the only
  way to recover the measurement.
