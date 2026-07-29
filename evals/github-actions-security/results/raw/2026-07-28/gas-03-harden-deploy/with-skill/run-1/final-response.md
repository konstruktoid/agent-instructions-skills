Done. Summary of changes to `.github/workflows/deploy.yml`:

**OIDC / credentials**
- Replaced static `aws-access-key-id`/`aws-secret-access-key` with OIDC role assumption via `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget`, region `eu-north-1`.
- Added job-level `permissions: id-token: write, contents: read` (workflow-level dropped to `permissions: {}`, since `write-all` was granting far more than needed).
- Note: the IAM role's trust policy on the AWS side must scope `sub`/`repository` to this exact repo — that's configured in AWS, not in this file, so double check it exists.

**Trigger**
- Added `tags: ["v*"]` alongside the existing `push: branches: [main]`, so a `v*` tag push also deploys.

**Other hardening applied while touching this file** (per the repo's github-actions-security skill baseline):
- `runs-on: self-hosted` → `ubuntu-latest`: the README states this repo is public, and a self-hosted runner on a public repo is unconditionally unsafe (anyone can PR and get code execution on the host).
- Pinned `actions/checkout` and `aws-actions/configure-aws-credentials` to resolved commit SHAs of their current releases (v7.0.1, v6.2.3), with version comments.
- `persist-credentials: false` on checkout.
- Moved `${{ github.event.head_commit.message }}` out of the `run:` block into `env:`/`printf` — it was previously interpolated directly into shell, which is a script-injection vector via a crafted commit message.
- Added `timeout-minutes: 15` and a `concurrency` group.
- `some-org/slack-notify@v1` (the Slack step) could **not** be pinned — that repo doesn't exist on GitHub, so it's a placeholder/fixture action with no resolvable SHA. Left as-is with an inline comment, and added `zizmor.yml` to suppress just that one `unpinned-uses` finding with the reason documented. Slack notification behavior itself is unchanged.

**Verification**: `actionlint` and `zizmor --persona=pedantic` both exit clean (0 findings after one fix cycle). Zizmor ran in offline mode (no `GH_TOKEN` available in this sandbox) so its API-backed audits weren't exercised. I could not actually trigger the workflow — there's no git remote configured in this workspace — so this is verified structurally (lint/audit clean) but not via a live Actions run.

README.md updated to describe the OIDC auth, the new tag trigger, and why GitHub-hosted runners are used.

Nothing has been committed — changes are unstaged in the working tree (`deploy.yml`, `README.md` modified, `zizmor.yml` new) for you to review.
