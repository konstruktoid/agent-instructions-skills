Everything is in place and validated. Summary:

**`.github/workflows/triage.yml`** (new): triggers on `pull_request_target` (`opened` only) — required since fork PRs get a read-only token under the plain `pull_request` event. Key security points:
- No checkout step, so untrusted fork code is never present on the runner despite the elevated token.
- Uses `actions/github-script` pinned to the full commit SHA (`3a2844b7...` = v9.0.0), matching the pinning convention already used in `ci.yml`.
- Reads the PR title/username only from `context.payload` inside JS (template literals), never interpolating untrusted data into a shell `run:` step — avoids the classic Actions script-injection vector.
- Permissions are `{}` at workflow level, narrowed to `pull-requests: write` + `issues: write` only on the job.
- Ensures the `needs-triage` label exists before applying it (creates it if missing), so the workflow doesn't fail on a fresh repo.

**`README.md`**: added a "Workflows" section documenting both `ci` and the new `triage` workflow, including why `pull_request_target` is safe here.

Validated the YAML parses correctly with PyYAML; no live GitHub Actions run was triggered since there's no configured remote for this repo.
