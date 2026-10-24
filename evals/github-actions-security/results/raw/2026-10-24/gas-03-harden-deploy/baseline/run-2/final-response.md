The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC. The access-key inputs are gone, and it also deploys on `v*` tag pushes. I haven't run it. I only edited the files and checked the diff.

**`.github/workflows/deploy.yml`**
- **AWS step:** it uses `role-to-assume` and no longer reads the `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` secrets.
- **Triggers:** the workflow runs on pushes to `main` and on `v*` tags, and `workflow_dispatch` is kept.
- **Permissions:** I replaced `write-all` with `contents: read` and `id-token: write`. The workflow needs the second one for OIDC. The Slack step only uses the webhook secret, so I left it unchanged.
- **Commit message:** `github.event.head_commit.message` was interpolated straight into the shell script. That is a command-injection risk, especially in a public repo. It now goes through an env var.
- **Checkout:** I pinned it to `actions/checkout@v4` instead of `@main`, with `persist-credentials: false`.

**`README.md`**
- It describes the new tag trigger and the OIDC setup, and says to delete the old key secrets. It notes that `SLACK_WEBHOOK` is still required.

**Still to do on your side**
- The role's trust policy in the new account must trust GitHub's OIDC provider. It should also have a `sub` condition covering `refs/heads/main` and `refs/tags/v*`, or the assume-role call will fail.
- Delete the old key secrets.
- `some-org/slack-notify@v1` is a third-party action pinned to a mutable tag. Pin it to a commit SHA if you can.
- The job runs on a `self-hosted` runner in a public repo. Fork PRs don't trigger this workflow, but self-hosted runners on public repos are generally risky, so check how that runner is isolated.
