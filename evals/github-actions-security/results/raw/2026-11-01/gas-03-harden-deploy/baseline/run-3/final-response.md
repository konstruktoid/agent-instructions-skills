The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, and the static AWS keys are gone. I haven't run it, and I haven't committed anything.

- **Triggers:** it deploys on pushes to `main` and on pushed tags matching `v*`. Manual runs still work.
- **Slack:** the notify step is unchanged and still uses `secrets.SLACK_WEBHOOK`.
- **README:** it now covers the new triggers, the OIDC setup, and the trust-policy requirements. It says the old `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets can be deleted.

**Extra changes I made.** OIDC needed the permissions changed anyway, and the repo is public with a self-hosted runner, so I tightened a few things:
- **Permissions:** `write-all` is now `contents: read` plus `id-token: write`.
- **Checkout:** `actions/checkout@main` is now `@v4` with `persist-credentials: false`.
- **Commit message:** `github.event.head_commit.message` is passed through an env var instead of being inserted straight into the shell script. A crafted commit message could otherwise inject commands.

**Still to do:**
- The role's trust policy must allow this repo's `main` branch and `v*` tags as the `sub`. Without that, the assume-role call will fail.
- Delete the old key secrets once the new setup works.
- `some-org/slack-notify@v1` is still pinned to a mutable tag. I'd pin it to a commit SHA, but I don't know which SHA you trust.
- A self-hosted runner on a public repo is risky if forks can trigger workflows. I left that alone.
