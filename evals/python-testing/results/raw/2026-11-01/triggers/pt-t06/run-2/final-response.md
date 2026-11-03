I didn't change anything, because no workflow in this repository runs pytest or sets a timeout.

**What's there:** the only workflow file is `.github/workflows/deploy.yml`. It has one job, `deploy`, which checks out the code and echoes the pull request title. It doesn't run pytest and has no `timeout-minutes` setting. I also searched every YAML, TOML, CFG and INI file for `pytest` or `timeout` and found nothing.

**Why the ten minutes might not come from here:**
- The pytest job may be defined in another repository, a reusable workflow, or a different CI system (Jenkins, GitLab, etc.).
- A ten-minute limit could come from a pytest plugin setting or from the runner, not from this workflow.
- You may be on the wrong branch. Git shows a detached `HEAD` here, not the main branch `tsi-03-validate-grader`.

**What I need from you:** either tell me where the pytest job is defined, or confirm that you want a new pytest job in this repo with a higher timeout. If it's the second, tell me how long the timeout should be (for example 30 minutes) and how the tests should be run.

**Two security problems in `deploy.yml`:**
- **Line 14:** the PR title goes straight into a shell command (`${{ github.event.pull_request.title }}`). Anyone who opens a PR can pick a title that runs their own commands. The fix is to pass the title through an `env:` variable and use `"$TITLE"` in the command.
- **Line 7:** `permissions: write-all` gives the job far more access than it needs. `contents: read` would be enough.

I can fix these if you'd like.
