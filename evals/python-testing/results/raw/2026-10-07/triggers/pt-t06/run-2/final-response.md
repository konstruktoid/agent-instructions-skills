I haven't changed anything, because I couldn't find a pytest job or a ten-minute timeout in this repo.

- **Workflow files:** `.github/workflows/deploy.yml` is the only one. Its single `deploy` job checks out the code and echoes the PR title. It never runs pytest and sets no `timeout-minutes`.
- **Other mentions:** a search of the whole repo for "pytest" or "timeout" found nothing, including in other CI configs.
- **Default timeout:** GitHub Actions allows 360 minutes per job by default, so a ten-minute limit has to be set somewhere else.

The pytest job may be in a different repo or branch. It could also be on another CI system, or in a workflow file that isn't checked in here. Can you tell me which file or repo it's in? If you want me to add a pytest job to `deploy.yml`, I can do that too. In that case, what timeout do you want?

Separately, `deploy.yml` has two security problems:
- `permissions: write-all` gives the job far more access than it needs.
- `${{ github.event.pull_request.title }}` is interpolated straight into a shell command, so a crafted PR title can inject commands. Passing it through an `env:` variable avoids that.

I can fix both if you want.
