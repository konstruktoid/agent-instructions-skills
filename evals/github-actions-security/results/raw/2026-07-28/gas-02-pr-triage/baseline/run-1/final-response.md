Added a triage workflow and README section. Summary:

**`.github/workflows/triage.yml`** — triggers on `pull_request_target` (`opened`), which works correctly for fork PRs since `pull_request` alone only grants a read-only token for forked contributions. Key safety property: it never checks out or runs any code from the fork — it only reads event metadata (`author`, `title`, `number`) and calls the GitHub API via `gh`. Values that could contain shell metacharacters (title, author) are passed through `env:` and referenced as `$VAR` inside `run:`, not interpolated directly via `${{ }}` in the script body, avoiding script-injection risk. Permissions are scoped to just `pull-requests: write` and `issues: write`. It creates the `needs-triage` label if missing (`--force`), posts the welcome comment, then applies the label.

Validated the YAML with `python3 -c "yaml.safe_load(...)"` and with `actionlint`, both clean.

**README.md** — added a "Workflows" section documenting both `ci` and `triage`, explaining the fork-safety rationale for `pull_request_target`.
