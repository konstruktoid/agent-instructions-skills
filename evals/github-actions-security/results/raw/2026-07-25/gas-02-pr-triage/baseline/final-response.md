Added `.github/workflows/triage.yml` and updated the README. Summary:

- **Workflow** (`.github/workflows/triage.yml`): triggers on `pull_request_target` (`opened`), with `permissions: {}` at the top and `pull-requests: write` scoped to the job only. It uses `actions/github-script`, pinned to a real commit SHA for v9.0.0, to post a welcome comment (`@username` + PR title) and apply the `needs-triage` label.
- **Fork safety**: `pull_request` runs from forks always get a read-only `GITHUB_TOKEN`, regardless of the `permissions:` block, so commenting/labeling would silently fail. `pull_request_target` runs with base-repo permissions instead — the workflow never checks out or executes the fork's code (it only reads `context.payload.pull_request` from the trusted event payload), avoiding the "pwn request" risk that normally comes with `pull_request_target`.
- **README**: added a "Workflows" section documenting both `ci.yml` and the new `triage.yml`, explaining the fork-safety rationale.
