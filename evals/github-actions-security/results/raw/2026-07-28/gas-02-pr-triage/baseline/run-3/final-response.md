actionlint validates both workflows with no errors. Everything checks out — I'll summarize.

## Summary

Added `.github/workflows/triage.yml`:
- Triggers on `pull_request_target` (types: `opened`) rather than `pull_request`, since fork-originated `pull_request` events get a read-only token that can't post comments or apply labels.
- Grants only `pull-requests: write`, no other permissions, and never checks out the PR's code — since `pull_request_target` runs with base-repo privileges, that avoids executing untrusted fork code with an elevated token.
- Uses `actions/github-script` (pinned to commit SHA for v9.0.0) to post a welcome comment (`@<login>` + the PR title) and apply `needs-triage`, creating the label first if it doesn't already exist (idempotent, handles 422 "already exists").
- The contributor username/title are read as JS values inside the sandboxed script, not interpolated into shell commands, so a malicious PR title can't be used for command injection.

Documented the new workflow in `README.md` alongside the existing CI workflow, explaining why `pull_request_target` is used and the safeguards in place.

Verified with `actionlint` (via `python3 -c yaml.safe_load` for syntax and `actionlint` for the Actions-specific check) — both workflows pass with no errors.
