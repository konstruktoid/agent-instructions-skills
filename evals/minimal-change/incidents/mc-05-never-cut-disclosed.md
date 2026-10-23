# The document's arm names a data-loss risk and cuts it anyway

Task: `mc-05-save-settings`

## Evidence

In the 2026-10-20 stamp, measured at `c0616b1` on a clean tree
(`evals/minimal-change/results/raw/2026-10-20/source-revision.json`), every run of
`mc-05-save-settings` in every arm wrote `save_settings` with `open(path, "w")` and `json.dump`,
and failed `failed-save-keeps-old-file` and `existing-atomic-write-reused`. The fixture's
`app/fsutil.py` holds `atomic_write`, which no run opened.

The `doc` arm read the document in all three runs (`doc_read` is true in each `grade.json`), and
all three named the risk in the closing line and left it out. Run 2 says, in two sentences:
"The write isn't atomic, so a crash partway through could leave a truncated file."
"I left that out because you didn't ask for it."
The baseline and plain runs mention neither atomicity nor truncation.

- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/doc/run-1/final-response.md`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/doc/run-2/final-response.md`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/doc/run-3/final-response.md`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/doc/run-2/workspace.diff`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/doc/run-2/grade.json`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/baseline/run-1/final-response.md`
- `evals/minimal-change/results/raw/2026-10-20/mc-05-save-settings/plain/run-1/final-response.md`

The tool calls in each `run.jsonl` show what each run read: the `doc` runs opened the document and
`app/settings.py`, and the other arms opened `app/settings.py` alone.

## Hypotheses

- **The closing line gives a never-cut item an exit.** Supported. "Closing the Reply" asks for a
  line naming what was skipped (`instructions/minimal_change_instructions.md:131`), and "What Is
  Never Cut" lists error handling that prevents data loss (`:68`). All three `doc` runs used the
  first to report a cut the second forbids, and no run of the other arms, which lack the closing
  rule, reported it. Not isolated: no arm had the closing rule without the never-cut list.
- **The agent did not recognize the data-loss risk.** Contradicted for the `doc` arm, whose three
  runs each describe the truncation.
- **The agent skipped the search for an existing helper.** Supported, and not specific to the
  document: no run in any arm opened `app/fsutil.py`, although the document requires that search
  before choosing a rung (`:33`). Reusing `atomic_write` would have passed both assertions.
- **The request's wording reads as a request for one line, and that outweighs any instruction.**
  Untested. All three arms wrote the same code, which fits it, but no arm varied the wording.

## Reproduction

9 of 9 runs failed both assertions at `c0616b1`, three per arm, with the `sonnet` model. The task
was written to catch this failure before any run, so the reproduction is the suite's own first
measurement rather than a later attempt from the record.

## Disposition

regression-case. `mc-05-save-settings` already reproduces the failure, so no new fixture is
needed. The next action is a targeted change to the document stating that an item on the never-cut
list is never moved into the closing line as skipped, followed by
`run_eval.py instructions-tasks --suite minimal-change --task mc-05-save-settings --runs 3` against
the changed revision. That change and its run have not been made.
