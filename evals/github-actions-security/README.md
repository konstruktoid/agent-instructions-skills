# github-actions-security evals

Six workflow changes, none of which asks for hardening, because the skill's claim is that
its baseline applies to every workflow it touches whatever the request was. The fixtures
supply an unhardened CI workflow, a triage request that invites both template injection and a
fork-controlled checkout, a deploy workflow with `write-all` permissions on a self-hosted
runner, a composite action with unpinned dependencies, a repository with no Dependabot
configuration, and a hardened workflow failing on a blocked outbound connection. Assertions run
`actionlint` and `zizmor` over the finished workspace and check the baseline directly:
`permissions: {}` at workflow level, `timeout-minutes` on every job, SHA pins carrying version
comments, and no event data interpolated into a `run:` block.
`sha-resolved-not-recalled` is graded over the run's Bash commands, since the skill forbids
writing a SHA from memory and a resolved one leaves a `gh api` call behind. Run it with
`python3 evals/run_eval.py tasks --skill github-actions-security`, then `report`.

## gas-06 is graded on refusing the fix it was asked for

`gas-06-blocked-egress` is the only task whose prompt states a diagnosis, asks for the repair
that follows from it, and is wrong on both counts. The failing step logs `fetch failed` and
nothing else, and the prompt blames the `step-security/harden-runner` bump in the same diff.
The cause is in the hardening action's post-step output in the saved log, `domain not allowed:
api.deps.dev.`, reached for the first time because this pull request is the first to change a
dependency manifest. The second saved log settles the version hypothesis: the passing run
contacted only `github.com` and `api.github.com` and never reached the endpoint at all.

Complying scores zero on `pin-not-reverted`, and dropping the policy to `audit` scores zero on
`egress-policy-still-block`, so the two obvious ways to make the check green both fail. The
fixture starts `actionlint` and `zizmor` clean, which means every finding at the end was
introduced by the run.

## What each stamp covers

`results/2026-07-28.md` is the latest task measurement: five tasks at three runs per condition,
a net gain of 29 assertions over the four with comparable runs. `gas-05-dependabot-pinning`
aborted in all three with-skill runs, so it has no delta, and the fix for that is a re-run rather
than a regrade. `results/2026-07-25.md` is the earlier single-run stamp over three tasks, and
`results/2026-07-27.md` measured routing only.

`gas-06-blocked-egress` postdates every stamp here and has never been graded. Until it runs, the
claim the task exists to test, that the skill refuses the fix it was asked for when the diagnosis
in the prompt is wrong, is a design intention rather than a measurement.

## Trigger accuracy is a 3-pass measurement from 2026-07-27

`results/2026-07-25.md` recorded `gas-t09` ("write a bash script that tags a release, signs the
tag, and pushes it") as the one probe that over-fired, on a single pass per probe. Re-running
the unmodified description three times per probe puts `gas-t09` at 1 of 3, so the majority
verdict is correct. The 2026-07-25 entry recorded the minority outcome of an unstable probe
rather than a routing defect.

The probe that does over-fire is `gas-t06`, "our GitLab CI pipeline needs a caching stage",
which fired 3 of 3 against a description whose body says in as many words that the skill is not
for CI systems other than GitHub Actions. The single-pass run recorded it as correct. Nothing
about the description changed between the two measurements; only the number of passes did.

Read the single-pass trigger tables in `evals/*/results/2026-07-25.md` with that in mind: at one
pass per probe, a probe that fires a third of the time is as likely to be recorded as a defect
as a stable one is, and a stable defect can be recorded as a pass.
