Done. Changes made:

**`.github/workflows/deploy.yml`**
- Trigger now fires on push to `main` and on tags matching `v*`, in addition to `workflow_dispatch`.
- Replaced static `aws-access-key-id`/`aws-secret-access-key` secrets with `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget` for OIDC-based role assumption in `eu-north-1`.
- Narrowed `permissions` from `write-all` to just `id-token: write` (required for OIDC) and `contents: read` (required for checkout) — the blanket `write-all` was unnecessary and is no longer needed now that there are no credentials to leak scope for.
- Slack notify step untouched, still runs after deploy.

**`README.md`** — updated to describe the tag-triggered deploys and OIDC auth, noting no long-lived AWS keys are stored in the repo.

Note: you'll still need to configure the trust policy on `arn:aws:iam::123456789012:role/deploy-widget` in AWS to trust GitHub's OIDC provider for this repo, and remove/rotate the old `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` secrets from the repo settings — those side aren't something I can change from here.
