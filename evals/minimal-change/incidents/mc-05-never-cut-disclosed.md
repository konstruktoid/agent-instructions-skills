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
  line naming what was skipped (`instructions/minimal_change_instructions.md:130`), and "What Is
  Never Cut" lists error handling that prevents data loss (`:67`). All three `doc` runs used the
  first to report a cut the second forbids, and no run of the other arms, which lack the closing
  rule, reported it. Not isolated: no arm had the closing rule without the never-cut list.
- **The agent did not recognize the data-loss risk.** Contradicted for the `doc` arm, whose three
  runs each describe the truncation.
- **The agent skipped the search for an existing helper.** Supported, and not specific to the
  document: no run in any arm opened `app/fsutil.py`, although the document requires that search
  before choosing a rung (`:32`). Reusing `atomic_write` would have passed both assertions.
- **The request's wording reads as a request for one line, and that outweighs any instruction.**
  Untested. All three arms wrote the same code, which fits it, but no arm varied the wording.
- **"What Is Never Cut" reads as a rule about removing safeguards, not about writing new code.** Its
  opening says a smaller change never "removes" these, and the Quality Checklist asks that they
  are "intact", while `save_settings` is new code with no safeguard to remove. Untested, and partly
  contradicted: in `mc-04-set-quantity` the `doc` arm adds validation to a new handler in 5 of 5
  assertions in both stamps, so the list does reach new code for validation at least.

## Reproduction

9 of 9 runs failed both assertions at `c0616b1`, three per arm, with the `sonnet` model. The task
was written to catch this failure before any run, so the reproduction is the suite's own first
measurement rather than a later attempt from the record.

9 of 9 runs failed both again at `56262a6`, in the 2026-10-24 stamp, where the baseline no longer
had this repository's `AGENTS.md` loaded. All three `doc` runs again named the risk and left it
out, run 2 as "a failed write can leave a partial file", and no `baseline` or `plain` run named
it. Across both stamps that is 18 of 18 runs failing, 6 of 6 `doc` runs naming the risk, and 0 of
12 other runs naming it.

## Disposition

regression-case. `mc-05-save-settings` already reproduces the failure, so no new fixture is
needed. The targeted change is `962e2ff`, which tests the first hypothesis alone: "Closing the
Reply" and the Quality Checklist now say the closing line never reports a missing never-cut item,
which is unfinished work. Nothing else in the document changed, so the skipped search, the
request's wording, and the reading of the list as a rule about removal stay untested, and a result
can be attributed to this rule.

What the change predicts, stated before any run of it: in the `doc` arm, `failed-save-keeps-old-file`
passes in at least 2 of 3 runs, and no closing line lists the write's safety as skipped.
`existing-atomic-write-reused` may still fail, since an agent that never opens `app/fsutil.py` can
only write its own temporary file, which that assertion rejects; the search hypothesis is a
separate change. The other five tasks keep their `doc` medians, and the `baseline` and `plain` arms,
which never see the document, are unaffected.

The next action is a full run of the suite at the revision that carries `962e2ff`, three runs per
arm, so the stamp covers every task in every arm. If the prediction fails, the closing line was
not the cause, and the reading of the list as a rule about removal is the next change to test.
