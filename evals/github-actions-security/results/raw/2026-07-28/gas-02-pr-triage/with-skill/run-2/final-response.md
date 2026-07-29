Everything is in order. Summary of the verification checklist:

- **actionlint**: clean (exit 0)
- **zizmor** (pedantic): clean except one pre-existing `concurrency-limits` suggestion on `ci.yml`, a file this task didn't touch — out of scope
- `permissions: {}` at workflow level, job grants only `pull-requests: write`, with an explanatory comment
- `actions/github-script` pinned to a resolved commit SHA (`3a2844b...` = `v9.0.0`, the current latest release, verified via the GitHub API)
- No `${{ }}` interpolation of event data into the script — PR title/username are read via the `context` object at runtime, not templated into the YAML
- `pull_request_target` is used deliberately (required so triage works on fork PRs, which get a read-only token under plain `pull_request`), documented with a comment on the trigger, a suppression with rationale in `zizmor.yml`, and no fork code is ever checked out
- Every job has `timeout-minutes`
- **Not verified live**: this workspace has no git remote and no authenticated `gh`, so I could not push a branch and watch the workflow actually run against a real fork PR. This is a structural-only verification — actionlint/zizmor pass, but the workflow has not executed on GitHub.

Files changed:
- `.github/workflows/triage.yml` (new)
- `zizmor.yml` (new — suppression + reason for the `pull_request_target` finding)
- `README.md` (documents both workflows)
