# Evals

Measurements of whether the skills in this repository change what an agent produces, and
whether their `description` fields route the right tasks to them. A skill that is
structurally correct is not necessarily a skill that does anything; this directory exists to
tell the difference.

## Layout

```text
evals/
  run_eval.py            The harness: tasks, triggers, and report subcommands
  probe-sandbox/         A mixed repository the trigger probes run against
  STRUCTURE.md           Report on collapsing instructions/ into skill references/
  <skill>/
    tasks.json           4 to 6 realistic multi-step task prompts
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

## Running them

```sh
# Tools the fixtures need, kept out of your own PATH
export UV_TOOL_BIN_DIR=/tmp/eval-bin UV_TOOL_DIR=/tmp/eval-tools
uv tool install ansible-lint && uv tool install zizmor
export EVAL_TOOL_BIN=/tmp/eval-bin

python3 evals/run_eval.py tasks    --skill python-secure-coding --model sonnet --parallel 5
python3 evals/run_eval.py triggers --skill python-secure-coding --model sonnet --parallel 5
python3 evals/run_eval.py report   --skill python-secure-coding
```

`report` regenerates `results/<date>.md` from the graded runs, so the checked-in results file
is never written by hand.

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

## Reading the results

The task table gives each run's passed-assertion count in both conditions and the delta
between them. A delta of zero means the skill changed nothing measurable on that task, which
is a result and is reported as one. Because the baseline agent is competent, a task where
both arms score full marks measures task difficulty rather than skill effect, and should be
made harder rather than read as success. The failed-assertion list under each table names
exactly which checks each run missed, and every one of those traces to a `grade.json` holding
the command that was run and the output it produced.

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
