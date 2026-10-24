I've switched the workflow to OIDC and added the `v*` tag trigger. I haven't run it or committed anything.

**`.github/workflows/deploy.yml`**
- **AWS step:** It now uses `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget` with region `eu-north-1`. The access-key and secret-key inputs are gone.
- **Permissions:** `write-all` is replaced by `contents: read` at the top level. The deploy job also gets `id-token: write`, which OIDC needs.
- **Triggers:** Pushes to `main`, tags matching `v*` and manual runs.
- **Slack:** The notify step is unchanged and still uses `SLACK_WEBHOOK`.

I also made two small hardening changes you didn't ask for:
- **Checkout:** `actions/checkout@main` is now `@v4`, with `persist-credentials: false`.
- **Commit message:** `github.event.head_commit.message` is now passed through an env var instead of being written into the shell script. Before, a crafted commit message could run commands on the runner.

**`README.md`**
- It now describes the tag trigger and OIDC auth, and says the old AWS key secrets can be deleted.
- It also says the role's trust policy must be restricted to this repo's `main` branch and `v*` tags.

**Still to do on your side**
- **Trust policy:** The `deploy-widget` role needs a trust policy for GitHub's OIDC provider, and the provider must exist in the new account.
- **Old secrets:** Delete the old `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets.
- **Self-hosted runner:** This repo is public and the job runs on a self-hosted runner. Forks and pull requests can be dangerous there, so use an ephemeral runner or a private repo. The workflow doesn't use `pull_request`, so it isn't directly exposed today.
- **Tag protection:** Anyone who can push a tag can trigger a deploy. Consider tag protection rules or a protected GitHub Environment with required reviewers.
- **Slack action:** `some-org/slack-notify@v1` is pinned to a mutable tag. Pin it to a commit SHA if you can.
