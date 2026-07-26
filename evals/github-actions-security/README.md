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
