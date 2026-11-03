I didn't make any changes, because this repo has no CI job that runs pytest and no timeout setting to raise.

The CI-related files I checked:

- **`.github/workflows/deploy.yml`**: one `deploy` job that checks out the code and echoes the PR title. It doesn't run pytest and has no `timeout-minutes` (GitHub's default is 360 minutes, not 10).
- **`.gitlab-ci.yml`**: one `build` job running `npm ci` and `npm run build`. A `test` stage is declared, but nothing is in it.
- **`Jenkinsfile`**: one `build` stage running `make build`.

None of them mention pytest, `tests/`, or a 10-minute limit. The job that's timing out is probably defined somewhere else, like another branch, another repo, or CI settings outside this repo. A 10-minute cap is often set at that level, for example as a GitLab project or runner timeout.

How do you want to proceed?
1. Tell me where the real pytest job lives, and I'll raise its timeout there.
2. Or I can add a new pytest job to one of these files with a longer timeout, such as `timeout-minutes: 30` in GitHub Actions or `timeout: 30m` in GitLab. That creates a new job rather than fixing an existing one, so I'd want your go-ahead first.

Separately, `deploy.yml` has two security problems:
- It puts `${{ github.event.pull_request.title }}` straight into a `run:` step. Anyone who opens a PR can use the title to inject shell commands.
- It sets `permissions: write-all`, which gives the workflow more access than it needs.

I can fix both if you want.
