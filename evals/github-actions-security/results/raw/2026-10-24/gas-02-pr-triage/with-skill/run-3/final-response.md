I added `.github/workflows/triage.yml`, but it hasn't run. It needs a real pull request opened from a fork, and I didn't push anything.

`actionlint` is clean. `zizmor` (pedantic) reports one low finding: `ci.yml` has no concurrency setting. That file is unchanged, so I left it alone.

- **Trigger:** it uses `pull_request_target` on `opened`, because a plain `pull_request` from a fork gets a read-only token and can't comment or label. It never checks out or runs pull request code, so the fork's code can't use the write token.
- **Comment:** it welcomes `@<username>` and repeats the title in quotes. The username and title go in through `env:`, never straight into the script, so a hostile title can't inject shell commands.
- **Label:** it applies `needs-triage` and creates the label first if it doesn't exist.
- **Permissions:** the only permission is `pull-requests: write`, granted to the one job. It uses the `gh` CLI that's already on the runner, so there are no third-party actions to pin.
- **Suppression:** I added `zizmor.yml` to ignore zizmor's `dangerous-triggers` finding for `triage.yml`, with the reason written in a comment.
- **README:** it now has a "Triage workflow" section covering the behavior and a warning not to add a checkout or build step to this workflow.

I'd also turn on the repository setting that requires approval before workflows run for outside contributors. I didn't change any settings.
