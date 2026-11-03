I added `.github/workflows/triage.yml` and a "Triage workflow" section in `README.md`. I haven't run the workflow, because it needs a real pull request on GitHub.

When a pull request is opened, the workflow:
- **Label:** applies `needs-triage`, and creates the label first if the repo doesn't have it.
- **Comment:** posts `Welcome, @<username>! Thanks for opening a pull request: **<title>**`, followed by a line saying a maintainer will triage it soon.

**Fork handling:** it uses the `pull_request_target` trigger. A normal `pull_request` trigger gives forks a read-only token, so the comment and label would fail. With `pull_request_target`, the job runs with the base repo's token and can write to the pull request.

**Safety:**
- `pull_request_target` is only safe if the workflow never runs code from the pull request, so it never checks out the PR.
- The title and username go through environment variables, not straight into the script, so a crafted title can't inject commands.
- Permissions are limited to `pull-requests: write` and `issues: write`.
- The README notes these constraints so later edits keep them.

A pull request title containing an `@name` will notify that person, because the title is repeated verbatim in the comment.
