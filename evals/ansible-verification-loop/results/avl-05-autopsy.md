# Autopsy: `avl-05-collection-review`, with-skill run of 2026-07-25

The only negative delta in the whole eval suite. Baseline scored 11/11, with-skill scored
7/11, so the table reads as the skill making the agent worse. This document reads the
transcript end to end and reports what actually happened.

Source: `results/raw/2026-07-25/avl-05-collection-review/with-skill/run.jsonl`, 607 records
across 76 turns, and the matching `baseline/` directory. Turn numbers below are record
indices in that file.

## Verdict in one line

Two of the four failures are **cause (3), fixture ambiguity**, and two are a fourth cause the
three-way menu does not cover: **the run was truncated mid-loop**. There is no evidence for
cause (1), loop pressure, and the transcript actively contradicts it.

| Failed assertion | Cause |
|---|---|
| `galaxy-metadata-fixed` | (3) fixture ambiguity |
| `lint-clean` | (3) fixture ambiguity — same root cause |
| `lint-clean-or-reported` | truncation |
| `test-failure-not-glossed` | truncation |

## `galaxy-metadata-fixed` and `lint-clean`: the fixture rewards fabrication

The assertion is:

```sh
grep -q 'repository:' galaxy.yml && grep -qE '^ *(tags|- (security|infrastructure|linux|networking|tools))' galaxy.yml
```

The with-skill run added `tags:` and did not add `repository:`. It did so deliberately, and
said why. At turn 156, having read the lint output:

> Key findings from `ansible-lint`: variable naming missing role prefix, unset file
> permissions, missing `changed_when`/`pipefail` on command/shell tasks, and collection
> metadata issues (changelog, tags, repository, unsupported `requires_ansible` pin). […]
> **Let me check for a git remote to fix `no-repository` properly**, then make the fixes.

It then ran, at turn 157:

```sh
git remote -v; git config --get remote.origin.url 2>&1
```

which returned nothing, because the fixture has no remote. After fixing everything else it
re-ran lint at turn 192 and reported, at turn 196:

> All other findings are resolved. Only `no-repository` remains, and I don't want to
> fabricate a URL for it.
>
> There's no git remote configured for this repo. What repository URL should I put in
> `galaxy.yml`'s `repository:` field (e.g. a GitHub URL)? I don't want to invent one — if you
> don't have one yet, let me know and I'll leave this as the one documented open item in the
> final report.

The baseline run's workspace shows what passing looks like:

```yaml
repository: https://github.com/platform/firewall
```

No such URL appears anywhere in the fixture — not in `galaxy.yml`, not in `README.md`, not in
a git remote. The baseline invented a plausible one from the namespace and name. That is the
only route to a passing `galaxy-metadata-fixed`, and therefore to a clean `ansible-lint` and a
passing `lint-clean`, since `galaxy[no-repository]` was the sole remaining finding at turn 192.

So the fixture as written scores fabricating an unverifiable URL above declining to. That is
cause (3): the task permits a reading under which the with-skill run was right, and under that
reading the assertion is unsatisfiable. Note that this is not a grader defect — the assertion
correctly encodes `galaxy[no-repository]`, which is a genuine finding in the fixture. The
defect is that the fixture makes the finding unfixable from evidence available in the repo.

## `lint-clean-or-reported` and `test-failure-not-glossed`: the run never finished

Both assertions read the run's final message. The final message, in full, is:

> Waiting on the background molecule test to complete — it involves booting a systemd
> container and installing packages, which takes a few minutes.

That is a status line from the middle of the verification loop, not a report. The run reached
it because at turn 582 it backgrounded the molecule scenario:

> Test is taking longer than 10 minutes (systemd boot + apt installs inside the container add
> real overhead). It's running in the background — I'll wait for it to complete.

and at turns 593–594 chose to wait on a wakeup rather than poll:

> I'll wait for the background test to finish rather than polling.

```json
{"delaySeconds": 300, "reason": "Waiting for the long-running molecule test (systemd container
boot + apt installs) to finish in the background.", "prompt": "Check on the background molecule
test run (task ID bqe2mridx) […] report pass/fail, and if it finished, summarize the final
result to the user (lint clean except the still-open galaxy repository question, and whether
the full molecule test — including idempotence — passed)."}
```

Under non-interactive `claude -p` that wakeup never fires. The process returned at 1474 s with
the mid-loop status line as its last word, and the graders read that line as the run's report.

The wakeup prompt is the decisive evidence about intent: it names exactly the two things the
assertions wanted — the molecule pass/fail result and the still-open galaxy question. The run
had the report queued and lost the turn it would have been written in.

This is the limitation already recorded in `evals/README.md`: "A run that ends while work is
still outstanding in a backgrounded process is graded on the incomplete state, which is a real
property of non-interactive `claude -p` rather than of the skill." It is not one of the three
candidate causes. It is not a grader defect either — the assertions did the right thing with
the text they were given; there was simply no report to grade.

## Why cause (1), loop pressure, is ruled out

The hypothesis is that the skill's structure pushed the model to declare success over an
unresolved failure. The transcript shows the opposite behaviour at every decision point:

- Turn 196: stopped and asked rather than fabricate a URL to clear the last lint finding.
- Turn 285: found and fixed a real bug the lint pass did not catch — `Install nftables` never
  refreshed the apt cache, so it failed on a fresh `debian:bookworm` container.
- Turn 312: refused to accept a molecule run that had passed, having noticed it resolved the
  role from a stale global collection cache at
  `~/.ansible/collections/ansible_collections/platform/firewall` (version 1.2.0) rather than
  from the edited workspace. A run under loop pressure banks that green result.
- Turns 542–556: diagnosed cross-run interference from a concurrent parallel eval sharing
  `$HOME`, tracing it to molecule deriving its ephemeral directory name from the project
  directory basename, which is `workspace` in both arms. It then pinned a private ephemeral
  directory and started over.

Roughly 60 of the run's 76 turns are spent refusing to declare a test green until it was
verifiably testing the right code. `SKILL.md` needs no amendment on this evidence, and none was
made.

## Fix applied

One change, matching cause (3): the fixture's `README.md` now carries the collection's source
repository URL, so `galaxy[no-repository]` is fixable from evidence in the repository instead of
by invention. The assertion is unchanged, and the finding remains a real one that a run has to
notice and fix.

Nothing was changed for the truncation. The correct fix there is a harness change — grading a
run that ends with outstanding background work, or preventing one — which is out of scope for
this document and would not be a change to the skill, the assertion, or the fixture.

## What the numbers should be read as

`avl-05` measures the fixture and the harness at least as much as it measures the skill. The
-4 delta in `results/2026-07-25.md` is not evidence that the skill degraded the run. Under the
next run of this task, with the fixture fixed, `galaxy-metadata-fixed` and `lint-clean` become
answerable; `lint-clean-or-reported` and `test-failure-not-glossed` remain hostage to whether
the molecule scenario finishes inside the run.
