Created `.github/workflows/triage.yml` (fires on `pull_request_target: opened`, permissions restricted to `pull-requests: write`, no checkout of PR code so fork contributions can't run arbitrary code with the write-scoped token) and updated `README.md` with a Workflows section documenting it.

Files changed:
- `.github/workflows/triage.yml` (new)
- `README.md`

Note on the fork-safety design: I used `pull_request_target` instead of `pull_request` because the default `GITHUB_TOKEN` for `pull_request` events from forks is read-only and can't post comments or add labels. `pull_request_target` runs with a write-scoped token in the base repo's context, which is safe here specifically because the job never checks out or executes the fork's code — it only reads `context.payload.pull_request` fields (title, username) inside the trusted `github-script` step, so there's no way for a malicious PR title/branch to inject into a shell command or get executed.
