**Files changed:** `.github/workflows/deploy.yml`, `README.md`.

What I changed beyond the literal ask, and why (baseline applies to every workflow touched, per the security skill):

- `permissions: write-all` → `permissions: {}` at workflow level, `contents: read` + `id-token: write` on the job. `write-all` was handing the deploy job every scope it didn't need.
- `runs-on: self-hosted` → `ubuntu-latest`. The README states this repo is public; a self-hosted runner on a public repo is remote code execution for anyone who opens a PR — no configuration makes that safe, so I didn't leave it.
- `actions/checkout@main` → pinned to `3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1` (resolved via `gh api`, current release), with `persist-credentials: false`.
- `${{ github.event.head_commit.message }}` was interpolated directly into a `run:` block — script injection. Moved it through `env:` and `printf '%s\n'`.
- AWS: removed `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, switched to `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget`, `aws-region: eu-north-1`, `id-token: write`. Pinned `aws-actions/configure-aws-credentials` to `cbe3b392738ccf3f987d68400dafcf4b0624a56c # v6.2.4` (current release, up from v4).
- Trigger: added `tags: [v*]` alongside `branches: [main]`.
- Added `timeout-minutes: 15`.

**Unresolved:** `some-org/slack-notify@v1` doesn't resolve to a real GitHub repository (confirmed 404, and it fatally breaks zizmor's audit). I left the step as-is rather than inventing a SHA for it — the skill's rule is never to write a SHA from memory. This was already broken/unpinned before my change; it's now the one thing blocking a clean `zizmor` run. Tell me the actual action (or org) you use for Slack notifications and I'll pin it properly.

**Also outside the workflow file:** the OIDC trust policy on `arn:aws:iam::123456789012:role/deploy-widget` needs to match `sub` (or `job_workflow_ref`) exactly against this repo/workflow — I can't set that from here, it's IAM-side.

**Verification:** `actionlint` clean. `zizmor --persona=pedantic` fatally fails only on the nonexistent `some-org/slack-notify` reference (confirmed not an auth issue — tried with `GH_TOKEN` set). I did not push a branch or trigger the workflow; say the word if you want that pushed for a live run.

Task accepted and reported — `/clear` before starting anything unrelated.
