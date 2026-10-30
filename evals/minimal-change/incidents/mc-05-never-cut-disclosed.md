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

- **The closing line gives a never-cut item an exit.** Supported by the 2026-10-20 and 2026-10-24
  stamps, then contradicted as the cause by the 2026-10-27 stamp. "Closing the Reply" asks for a
  line naming what was skipped (`instructions/minimal_change_instructions.md:122`), and "What Is
  Never Cut" lists error handling that prevents data loss (`:59`). All three `doc` runs used the
  first to report a cut the second forbids, and no run of the other arms, which lack the closing
  rule, reported it. Not isolated: no arm had the closing rule without the never-cut list. In the
  2026-10-27 stamp, with the closing line forbidden to report a missing never-cut item, at
  `81191a3`, all three `doc` runs read the whole document and still left the safeguard out, and two
  of them still listed the partial or truncated file as skipped.
- **The agent did not recognize the data-loss risk.** Contradicted for the `doc` arm, whose three
  runs each describe the truncation.
- **The agent skipped the search for an existing helper.** Supported, and not specific to the
  document: no run in any arm opened `app/fsutil.py`, although the document requires that search
  before choosing a rung (`:24`). Reusing `atomic_write` would have passed both assertions.
- **The request's wording reads as a request for one line, and that outweighs any instruction.**
  Untested. All three arms wrote the same code, which fits it, but no arm varied the wording.
- **"What Is Never Cut" reads as a rule about removing safeguards, not about writing new code.** Its
  opening says a smaller change never "removes" these, and the Quality Checklist asks that they are
  "intact", while `save_settings` is new code with no safeguard to remove. Partly contradicted
  before any test: in `mc-04-set-quantity` the `doc` arm adds validation to a new handler in 5 of 5
  assertions in both stamps, so the list does reach new code for validation at least. Then
  contradicted as the cause by the 2026-10-27-new-code stamp: with the list saying it never leaves
  these out of code a change adds, at `bfc04e2`, all three `doc` runs read the whole document and
  still left the safeguard out, and all three listed the non-atomic write as skipped.
- **The agent files the safeguard under scope the request did not ask for.** Supported, untested.
  Across the four stamps, 11 of 12 `doc` closing lines name the write's risk and 5 of them give the
  request as the reason for leaving it out, as in "because the request didn't ask for one". None of
  the 24 `baseline` or `plain` runs names the risk at all. The document changes what the agent says
  about the safeguard, not whether it writes one, and its scope rules, such as changing only what
  the request needs, may outrank the never-cut list.

- **The Claude Code version moved the result.** Refuted 2026-10-29. At `a5d8770` the `doc` arm kept
  the old file on a failed save in 1 of 3 runs on 2.1.305 and 2 of 3 on 2.1.311, so the versions
  on which the earlier stamps failed it in every run pass it at this revision.

## Reproduction

9 of 9 runs failed both assertions at `c0616b1`, three per arm, with the `sonnet` model. The task
was written to catch this failure before any run, so the reproduction is the suite's own first
measurement rather than a later attempt from the record.

9 of 9 runs failed both again at `56262a6`, in the 2026-10-24 stamp, where the baseline no longer
had this repository's `AGENTS.md` loaded. All three `doc` runs again named the risk and left it
out, run 2 as "a failed write can leave a partial file", and no `baseline` or `plain` run named
it. Across both stamps that is 18 of 18 runs failing, 6 of 6 `doc` runs naming the risk, and 0 of
12 other runs naming it.

9 of 9 runs failed both again at `81191a3`, in the 2026-10-27 stamp, which carries the targeted
change `962e2ff` (`evals/minimal-change/results/2026-10-27.md`). That stamp ran in a cloud
container on Claude Code 2.1.311, where the two earlier stamps ran on the maintainer's machine on
2.1.305 and 2.1.310, and its runs start with 19 built-in skills where theirs started with 17. Every
arm saw the same environment, so the comparison within the stamp holds; a comparison across stamps
mixes the change with the machine.

9 of 9 runs failed both again at `bfc04e2`, in the 2026-10-27-new-code stamp
(`evals/minimal-change/results/2026-10-27-new-code.md`), which carries the second targeted change
`54c5754`, in the same container and on the same Claude Code version as 2026-10-27.

The failure did not reproduce in the `doc` arm at `a5d8770`, in the 2026-10-28-mc05 and
2026-10-28-mc05-b stamps (`evals/minimal-change/results/2026-10-28-mc05.md` and
`evals/minimal-change/results/2026-10-28-mc05-b.md`), each on a clean tree, with three runs per
arm of `mc-05-save-settings` alone, on Claude Code 2.1.312. `failed-save-keeps-old-file` passed in
6 of 6 `doc` runs and in 0 of 12 `baseline` and `plain` runs. Four of the six `doc` runs wrote a
temporary file and called `os.replace`. The other two, run 3 of each stamp, built the JSON text
before opening `path` and then wrote to it directly, and their closing lines name the non-atomic
write as skipped because the request did not ask for it. `existing-atomic-write-reused` failed in
18 of 18 runs, and none opened `app/fsutil.py`.

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

The prediction failed. In the 2026-10-27 stamp `failed-save-keeps-old-file` passed in 0 of 3
`doc` runs, against at least 2 predicted, and two of the three closing lines still list the
partial or truncated file as skipped; the third lists the error handling it did not add. Each of
the three read the whole document, the new paragraph included. The rest of the prediction held:
the other five tasks kept their medians in every arm, the arms kept their order by lines of
non-test source added (the document 49, the sentence 54, the baseline 60), and the `doc` arm added
tests in 14 of 18 runs, against 16 of 18 on 2026-10-24.

The closing line is therefore not the cause, and `962e2ff` changes nothing a run can measure.
`85a5a3b` reverts it, since a rule with no measured effect adds length the document's own standard
does not allow. The next action is to test the reading of the list as a rule about removal, as one
change on its own.

That change is `54c5754`: "What Is Never Cut" now says a smaller change never removes these items
from code that has them and never leaves them out of code it adds, and the Quality Checklist line
says the same. Nothing else in the document differs from `main`.

What it predicts, stated before any run of it: in the `doc` arm, `failed-save-keeps-old-file`
passes in at least 2 of 3 runs, and no closing line lists the write's safety as skipped.
`existing-atomic-write-reused` may still fail, as before. The other five tasks keep their `doc`
medians, and the `baseline` and `plain` arms are unaffected. The `doc` arm may add more non-test
source than its 49 lines on 2026-10-27, most likely in `mc-03-export-rows`, which also writes a
file; that would be the change's cost, not a failure of it. If `failed-save-keeps-old-file` still
passes in fewer than 2 runs, neither wording is the cause, and the skipped search for the existing
helper is the remaining hypothesis.

The prediction failed. `failed-save-keeps-old-file` passed in 0 of 3 `doc` runs, each of which read
the whole document, and all three closing lines list the non-atomic write as skipped. The rest
held: every task kept its median in every arm, the `doc` arm wrote 53 lines of non-test source
against 57 for the sentence and 57 for the baseline, its `mc-03-export-rows` runs wrote 9, 9 and 11
lines against 9, 9 and 9 before, and it added tests in 17 of 18 runs. The wording cost nothing and
changed nothing, so the reading of the list as a rule about removal is not the cause either, and
`9a86eb9` reverts the change.

Two hypotheses remain: the skipped search for `atomic_write`, and the safeguard filed under
unrequested scope. Two changes to the document's text have now moved nothing, and both remaining
hypotheses would be a third. The decision is to stop there: the "Measured effect" paragraph of
`instructions/minimal_change_instructions.md` now says that the document makes an agent name this
risk and not add the safeguard, and the task stays as the regression case that a later change,
of any kind, has to pass.

Revised 2026-10-28. At `a5d8770`, `failed-save-keeps-old-file` no longer fails in the `doc` arm,
and `existing-atomic-write-reused` fails in every arm as before. The task stays the regression
case, now for the second assertion alone. The "Measured effect" paragraph states both counts and
that the cause is not established, and it no longer says the document leaves the safeguard out.
The document is not credited with the change, because the rules are unchanged since the stamps that
failed and Claude Code moved from 2.1.311 to 2.1.312. Telling the version from the draw takes one
revision measured on two versions.

Revised 2026-10-29. `a5d8770` was measured on Claude Code 2.1.305 and 2.1.311, in the
2026-10-29-mc05-v305 and 2026-10-29-mc05-v311 stamps
(`evals/minimal-change/results/2026-10-29-mc05-v305.md` and
`evals/minimal-change/results/2026-10-29-mc05-v311.md`), each from a clean clone outside the home
directory, with three runs per arm of `mc-05-save-settings` alone. `failed-save-keeps-old-file`
passed in 1 of 3 and 2 of 3 `doc` runs and in 0 of 12 `baseline` and `plain` runs, and
`existing-atomic-write-reused` failed in 18 of 18. The version is not the cause.

The draw alone does not explain the history either. Across the four stamps at `a5d8770` the `doc`
arm passed in 9 of 12 runs, and at that rate six runs all fail with a probability of about 0.0002,
which is what happened at `c0616b1` and `56262a6`. Against `56262a6` the only change to the
document at `a5d8770` is the "Measured effect" paragraph, which since `de26bb6` describes this task:
it names `mc-05-save-settings`, calls it the one task whose change needs a safeguard against data
loss, and says the agent left the safeguard out. Every stamp that failed in every `doc` run predates
`de26bb6`, and every stamp that passed carries it. The paragraph is the leading explanation, which
would make the result a property of the document describing its own measurement rather than of its
rules. It is not established: the harness and the date changed too. Measuring `56262a6` on 2.1.312
would separate the paragraph from the date.

The "Measured effect" paragraph was moved out of the document into
`evals/minimal-change/README.md` on 2026-10-29, so a stamp of a later revision measures the rules
without the description. If the `doc` arm then fails `failed-save-keeps-old-file` again, the
description was the cause.

Confirmed 2026-10-29. `586a3e1` was measured on Claude Code 2.1.312 in the 2026-10-29 stamp
(`evals/minimal-change/results/2026-10-29.md`), every task, three runs per arm, from a clean clone
outside the home directory. Against `a5d8770` it changes the document by that paragraph's removal
and changes no fixture, task, assertion, or harness file. `failed-save-keeps-old-file` failed in 3
of 3 `doc` runs and in 6 of 6 `baseline` and `plain` runs, and `existing-atomic-write-reused`
failed in 9 of 9. At the 9-of-12 rate `a5d8770` passed at, three runs all fail with a probability
of about 0.016, and `a5d8770` passed on this version the day before and on two older versions the
same day. The description was the cause: the document's rules do not keep the old file on a
failed save, and naming the task in the document did.
