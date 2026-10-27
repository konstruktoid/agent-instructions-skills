# Baseline runs read this repository's instructions from outside their workspace

## Evidence

In the 2026-10-20 stamp, four of the eighteen `baseline` runs reached into the checkout the harness
ran from, which the arm is meant to know nothing about. Transcripts are scrubbed, so `/repo` below
is the placeholder for that checkout's root. Each run's working directory was
`/repo/evals/minimal-change/results/raw/2026-10-20/<task>/<arm>/run-<n>/workspace`, inside it.

- `mc-02-parse-when` run 1 ran `ls /repo/instructions` as its second tool call, naming the
  directory before any call had listed it.
- `mc-02-parse-when` run 3 ran `ls /repo/instructions` in its first tool call.
- `mc-03-export-rows` run 2 read `/repo/instructions/python_coding_instructions.md`.
- `mc-05-save-settings` run 2 ran `cd /repo` and read the same file.

No `doc` or `plain` run referred to a path under `/repo` outside its workspace. The init event of
every run in the stamp, in all three arms, lists the builtin plugin `cc-plugin-agents-md`, on
Claude Code 2.1.305.

- `evals/minimal-change/results/raw/2026-10-20/mc-02-parse-when/baseline/run-1/run.jsonl`
- `evals/minimal-change/results/raw/2026-10-20/mc-02-parse-when/baseline/run-3/run.jsonl`
- `evals/minimal-change/results/raw/2026-10-20/mc-03-export-rows/baseline/run-2/run.jsonl`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/baseline/run-2/run.jsonl`

`claude plugin details cc-plugin-agents-md@builtin` describes the plugin as "AGENTS.md as project
instructions: by default loaded where the project has no CLAUDE.md". The `baseline` arm is the only
one whose workspace has no `CLAUDE.md`.

A probe on 2026-10-23, with Claude Code 2.1.309, placed a codeword in a file above a nested git
workspace and ran `claude -p` from the workspace with the harness's flags as of `4247742`, a
private `HOME` and `CLAUDE_CONFIG_DIR`, the `sonnet` model, and `--tools ""`, so the codeword could
only come from context loaded at start. It asked for the codeword, or UNKNOWN. The probe's output
is not committed; the description here is enough to repeat it for about $0.11.

| Files around the workspace | Answer |
|---|---|
| None | UNKNOWN, 3 of 3 runs |
| `AGENTS.md` above it, no `CLAUDE.md` in it, as in the `baseline` arm | The codeword, 3 of 3 runs |
| `AGENTS.md` above it and a `CLAUDE.md` in it, as in the `doc` and `plain` arms | UNKNOWN, 3 of 3 runs |
| `CLAUDE.md` above it, the case the harness already refuses | The codeword, 3 of 3 runs |
| `AGENTS.md` above it, with `--settings` disabling `cc-plugin-agents-md@builtin` | UNKNOWN, 3 of 3 runs |

The same layout driven through `claude_command` and `invoke_claude` in `evals/run_eval.py`, after
the change described under Disposition, answered UNKNOWN in 3 of 3 runs. With the setting removed,
`invoke_claude` stopped the run.

## Hypotheses

- **The checkout's `AGENTS.md` reached the baseline as instructions, through
  `cc-plugin-agents-md`.** Supported by the probe, which reproduces the baseline's exposure and
  the other two arms' immunity. It names `instructions/python_coding_instructions.md`, the file two
  of the runs read. The harness's ancestor check looks only for the `CLAUDE.md` names.
- **Every baseline run had it loaded, not only the four that acted on it.** Supported by the
  probe, since the condition does not depend on the task, and not directly observable, because a
  transcript does not record the system prompt.
- **The run found the checkout by walking up from its working directory.** Contradicted for
  `mc-02-parse-when` runs 1 and 3, which named `/repo/instructions` before listing any directory
  above their workspace, run 3 in its first tool call. The path was in their context from the
  start.
- **Earlier stamps were affected too.** Contradicted for this repository's `AGENTS.md`, which was
  added in `7e4a686` on 2026-10-19. The plugin appears in every stamp from 2026-10-06 on, and
  2026-10-20 is the only stamp after that commit. A file above the operator's checkout at the
  time cannot be ruled out from the transcripts.

## Reproduction

3 of 3 runs loaded the `AGENTS.md` above a baseline-shaped workspace, with the harness flags as of
`4247742`. 0 of 3 did once each run disabled the plugin.

In the suite itself, 0 of 54 runs loaded the plugin at `56262a6`, which carries the fix, in the
2026-10-24 stamp (`evals/minimal-change/results/2026-10-24.md`), and 0 of its 18 `baseline` runs
read anything outside their workspace.

## Disposition

fixed. The cause was in the harness, not in anything a suite task can reproduce, and it is fixed
there: `claude_command` in `evals/run_eval.py` disables `cc-plugin-agents-md@builtin` for every
run, and `invoke_claude` stops a measurement whose transcript shows the plugin loaded, or shows no
plugin list at all.

The 2026-10-24 stamp, without the exposure, repeats the 2026-10-20 result. Every task has the same
median in every arm, the same assertions fail, and the order of the arms by lines of non-test
source added is unchanged: the document 49 and 50, the sentence 56 and 55, the baseline 62 and 67.
At three runs per arm the exposure moved nothing the suite can detect, and the claim in
`instructions/minimal_change_instructions.md` stands. Counting lines outside test files is this
record's split, not a column of the report, which counts tests in its lines added.
