# github-actions-security evals

Five workflow changes, none of which asks for hardening, because the skill's claim is that
its baseline applies to every workflow it touches whatever the request was. The fixtures
supply an unhardened CI workflow, a triage request that invites both template injection and a
fork-controlled checkout, a deploy workflow with `write-all` permissions on a self-hosted
runner, a composite action with unpinned dependencies, and a repository with no Dependabot
configuration. Assertions run `actionlint` and `zizmor` over the finished workspace and check
the baseline directly: `permissions: {}` at workflow level, `timeout-minutes` on every job,
SHA pins carrying version comments, and no event data interpolated into a `run:` block.
`sha-resolved-not-recalled` is graded over the run's Bash commands, since the skill forbids
writing a SHA from memory and a resolved one leaves a `gh api` call behind. Run it with
`python3 evals/run_eval.py tasks --skill github-actions-security`, then `report`.

## Trigger accuracy is a 3-pass measurement from 2026-07-27

`results/2026-07-25.md` recorded `gas-t09` ("write a bash script that tags a release, signs the
tag, and pushes it") as the one probe that over-fired, on a single pass per probe. Re-running
the unmodified description three times per probe puts `gas-t09` at 1 of 3, so the majority
verdict is correct and the 2026-07-25 result was one draw from a coin, not a routing defect.

The probe that does over-fire is `gas-t06`, "our GitLab CI pipeline needs a caching stage",
which fired 3 of 3 against a description whose body says in as many words that the skill is not
for CI systems other than GitHub Actions. The single-pass run recorded it as correct. Nothing
about the description changed between the two measurements; only the number of passes did.

Read the single-pass trigger tables in `evals/*/results/2026-07-25.md` with that in mind: at one
pass per probe, a probe that fires a third of the time is as likely to be recorded as a defect
as a stable one is, and a stable defect can be recorded as a pass.
