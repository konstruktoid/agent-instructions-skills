I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run the workflow, so it's untested.

- **Trigger:** it runs on `pull_request_target` when a pull request is opened. A plain `pull_request` trigger gives forks a read-only token, so it couldn't comment or label there.
- **Comment and label:** the comment reads "Welcome, @<username>! … Summary: <PR title>", and the workflow applies `needs-triage`. Both use the `gh` CLI that's already on the runner, so there's no third-party action to pin.
- **Safety:** with `pull_request_target` the token has write access, so the workflow never checks out or runs the pull request's code. It passes the title and username through environment variables instead of putting them directly in the script. That stops a crafted title from injecting shell commands.
- **Permissions:** it asks only for `pull-requests: write` and `issues: write`, scoped to the one job.
- **Label:** the `needs-triage` label has to exist in the repository first, or the labeling step will fail. The README says so.
