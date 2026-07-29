Done. Summary of changes to `.github/workflows/deploy.yml`:

- Added `tags: ['v*']` alongside the existing `branches: [main]` push trigger, so version tags now also deploy.
- Replaced the static `aws-access-key-id`/`aws-secret-access-key` inputs with `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget`, keeping `aws-region: eu-north-1` — this makes `configure-aws-credentials` use OIDC.
- Narrowed `permissions: write-all` down to `id-token: write` + `contents: read` — the minimum needed for OIDC token minting and checkout (required for the OIDC exchange to work, and much tighter than write-all on a public repo).
- Left the Slack `Notify` step untouched — still fires after deploy.

`README.md` now documents the tag-triggered deploys and the OIDC-based auth (no long-lived keys).

Two pre-existing issues I did *not* touch, since they're outside what was asked — flagging in case you want a follow-up:
- `actions/checkout@main` is pinned to a mutable branch rather than a version tag/SHA (supply-chain risk).
- `echo "Deploying ${{ github.event.head_commit.message }}"` interpolates commit message text directly into a shell command — a script-injection vector since this is a public repo.
