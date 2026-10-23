# Baseline runs read this repository's instructions from outside their workspace

## Evidence

In the 2026-10-20 stamp, four of the eighteen `baseline` runs reached into the checkout the harness
ran from, which the arm is meant to know nothing about. Each run's working directory was
`/repo/evals/minimal-change/results/raw/2026-10-20/<task>/<arm>/run-<n>/workspace`, inside that
checkout.

- `mc-02-parse-when` run 1 ran `ls /repo/instructions` as its second tool call, naming the
  directory before any call had listed it.
- `mc-02-parse-when` run 3 ran `ls /repo/instructions` in its first tool call.
- `mc-03-export-rows` run 2 read `/repo/instructions/python_coding_instructions.md`.
- `mc-05-save-settings` run 2 ran `cd /repo` and read the same file.

No `doc` or `plain` run referred to a path under `/repo` outside its workspace.

- `evals/minimal-change/results/raw/2026-10-20/mc-02-parse-when/baseline/run-1/run.jsonl`
- `evals/minimal-change/results/raw/2026-10-20/mc-02-parse-when/baseline/run-3/run.jsonl`
- `evals/minimal-change/results/raw/2026-10-20/mc-03-export-rows/baseline/run-2/run.jsonl`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/baseline/run-2/run.jsonl`

## Hypotheses

- **The checkout's `AGENTS.md` reached the baseline as an ancestor instruction file.** Untested.
  It names `instructions/python_coding_instructions.md`, the file two of the runs read, and the
  harness refuses to start only for the ancestor names in `ANCESTOR_INSTRUCTION_FILES` in
  `evals/run_eval.py`, which are `CLAUDE.md`, `CLAUDE.local.md`, and `.claude/CLAUDE.md`. The
  transcripts do not record the system prompt, so they cannot show what was loaded.
- **The run found the checkout by walking up from its working directory.** Contradicted for
  `mc-02-parse-when` runs 1 and 3, which named `/repo/instructions` before listing any directory
  above their workspace, run 3 in its first tool call. The path was in their context from the
  start.

## Reproduction

Not attempted. The count above comes from the one stamp, and no other suite's transcripts have
been searched for the same pattern.

## Disposition

open. Two questions decide it: whether Claude Code loads an ancestor `AGENTS.md`, and whether the
2026-10-20 baseline numbers moved because of it. A run with `AGENTS.md` absent from the checkout
answers the first. If it is the cause, the fix is in the harness rather than in a suite: refuse to
start while an `AGENTS.md` sits above the workspace, or place the workspaces outside the checkout.
