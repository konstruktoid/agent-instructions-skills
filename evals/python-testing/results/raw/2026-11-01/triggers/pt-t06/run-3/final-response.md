I didn't change anything, because no workflow in this repo runs pytest.

There are two CI config files:

- **`.github/workflows/deploy.yml`** has one job, `deploy`, which checks out the code and echoes the PR title. It has no test step and no `timeout-minutes`.
- **`.gitlab-ci.yml`** defines a `test` stage, but no job uses it. The only job is `build`, which runs `npm ci` and `npm run build`.

The ten-minute timeout is probably set somewhere outside this repo:

- **In another repo or on another branch**, if the pytest workflow lives there.
- **In GitLab project settings** (Settings → CI/CD → General pipelines → Timeout). GitLab's default is 60 minutes, but it may have been lowered to 10, or set on the runner.
- **In a reusable workflow or template** included from elsewhere.

Also, I can only read files in this session, so I couldn't edit even if I'd found the job. The fix is one line on the job. Set `timeout-minutes: 30` for GitHub Actions or `timeout: 30m` for GitLab, using whatever limit you need. If you point me to the right file, I'll tell you exactly where it goes.

Separately, `deploy.yml` has two security problems:

- **Line 14** puts `${{ github.event.pull_request.title }}` straight into a shell command, so anyone who opens a PR can run commands through its title. Pass it in through an `env:` variable instead.
- **Line 7** sets `permissions: write-all`, which gives the job far more access than it needs.
