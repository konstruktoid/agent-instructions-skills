I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run it, because it only triggers on a real pull request.

**What it does:** when a pull request is opened, it comments "Welcome, @username! Thanks for opening a pull request: **title**" and applies the `needs-triage` label. It creates the label first if the repo doesn't have it.

**Forks:** the workflow uses the `pull_request_target` trigger. A plain `pull_request` trigger gives fork PRs a read-only token, so the comment and label would fail. Because that trigger runs with write access, the workflow never checks out or runs the PR's code. The PR title and username go in through environment variables instead of being written into the script, so a hostile title can't inject commands. Its permissions are limited to `pull-requests: write` and `issues: write`.

**Implementation:** it uses the `gh` CLI that comes with the runner rather than a third-party action, so there is nothing extra to pin. The README explains why `pull_request_target` is used and warns against adding a checkout of the PR head to this workflow.

I haven't committed anything.
