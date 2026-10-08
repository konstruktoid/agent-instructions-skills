I couldn't find a timeout to raise, so I haven't changed anything.

- **`.github/workflows/deploy.yml`:** This is the only GitHub Actions workflow. It checks out the code and echoes the PR title. It has no pytest step and no `timeout-minutes`.
- **`.gitlab-ci.yml` and `Jenkinsfile`:** Both only run build steps (`npm ci`/`npm run build` and `make build`). Neither has a test stage or a timeout.
- **Search:** There are no other matches for "pytest" or "timeout" anywhere in the repo.

The pytest job may live in another repo, or in a workflow file that isn't on this branch. If you tell me which file or CI system it is, I'll raise the timeout there.

If you want me to add a pytest job to `deploy.yml` with an explicit `timeout-minutes`, I can do that. I'd need to know the value you want.

Separately, `deploy.yml` has two security problems:

- **Script injection:** `${{ github.event.pull_request.title }}` is interpolated directly into a `run:` step. Anyone who can open a PR can inject shell commands through the title.
- **Over-broad permissions:** `permissions: write-all` gives the job far more access than it needs.

I haven't touched either.
