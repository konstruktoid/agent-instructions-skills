I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run it, because it only fires on a real pull request opened on GitHub.

- **Trigger:** it runs when a pull request is opened.
- **Comment:** it posts "Welcome, @username!" followed by "Summary: **<PR title>**" and a note that a maintainer will triage soon.
- **Label:** it applies `needs-triage`, and creates the label first if the repo doesn't have it.
- **Forks:** the workflow uses `pull_request_target`, because the normal `pull_request` trigger gives forks a read-only token that can't comment or label. The workflow never checks out or runs the pull request's code, which is what makes `pull_request_target` safe here. Keep it that way if you edit it.
- **Untrusted input:** the title and username are passed in as environment variables, not interpolated into the shell script, so a crafted title can't inject commands.
- **Permissions:** the job gets only `pull-requests: write` and `issues: write`. It uses the preinstalled `gh` CLI, so there are no third-party actions.

A title containing `@someone` will notify that person when the comment posts. I left that as is.
