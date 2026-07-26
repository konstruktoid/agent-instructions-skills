This all looks correct and complete. Summary of what was done:

**`.github/workflows/pr-triage.yml`** (new): triggers on `pull_request_target` with `types: [opened]` — required (not `pull_request`) because fork PRs get a read-only token otherwise. The job holds only `pull-requests: write`, sets `timeout-minutes`, never checks out any code (so fork-controlled code never executes), and uses `actions/github-script` (pinned to a resolved commit SHA, v9.0.0) with the PR title/author passed through `env:`/`process.env` rather than interpolated into a script string. It posts a welcome comment naming the contributor and quoting the PR title, then creates (if needed) and applies the `needs-triage` label.

**`README.md`**: added a "Workflows" section documenting the triage workflow's behavior and why `pull_request_target` is safe here.

Verification: `actionlint` clean; `zizmor --persona=pedantic` clean except the one deliberate, commented `pull_request_target` finding, which is the documented trade-off needed to support fork PRs.
