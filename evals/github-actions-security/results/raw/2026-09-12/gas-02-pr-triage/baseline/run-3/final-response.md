Files changed: `.github/workflows/pr-triage.yml` (new), `README.md`.

Notable choice: used `pull_request_target` rather than `pull_request`, since fork PRs get a read-only `GITHUB_TOKEN` under `pull_request` and can't post comments or labels no matter what permissions you request. `pull_request_target` runs the workflow file from the base branch (not attacker-controlled) and gets a write-scoped token, but the job never checks out or executes PR code — it only reads `title`/`user.login` from the trusted event payload and passes them into `github-script` API calls, not into a shell string, avoiding script-injection risk. `actions/github-script` is pinned to v9.0.0's commit SHA I resolved via `gh api`.

I did not verify against a live repo/runner (none available here) — that remains the real test: open a PR from a fork and confirm the comment and `needs-triage` label appear.
