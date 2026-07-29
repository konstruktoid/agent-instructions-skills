Done. Changes to `.github/workflows/deploy.yml`:

- **Trigger**: added `tags: ['v*']` alongside the existing `push: branches: [main]`, so pushing a `v*` tag now also deploys.
- **Auth**: replaced the `aws-access-key-id`/`aws-secret-access-key` static credentials with `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget`, keeping `aws-region: eu-north-1`. This uses OIDC role assumption via `aws-actions/configure-aws-credentials@v4`, which auto-detects OIDC when no static keys are given.
- **Permissions**: narrowed `permissions: write-all` down to just `id-token: write` (required for OIDC) and `contents: read` (required for checkout). OIDC role assumption doesn't work without `id-token: write`, and `write-all` was unnecessarily broad for what this job does.
- **Slack notify** step is untouched and still runs after deploy.

I also updated `README.md` to describe the tag-triggered deploys and the OIDC-based auth (no more long-lived keys).

One thing worth flagging: this repo's IAM side isn't in scope here — you'll still need to configure the trust policy on `arn:aws:iam::123456789012:role/deploy-widget` in the new account to trust GitHub's OIDC provider (`token.actions.githubusercontent.com`) scoped to this repo, or the workflow will fail at the "Configure AWS" step with an access-denied error.
