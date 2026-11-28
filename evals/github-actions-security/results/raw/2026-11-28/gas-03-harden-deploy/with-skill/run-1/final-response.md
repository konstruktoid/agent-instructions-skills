The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, has no static keys, and also deploys on `v*` tags. It hasn't run on GitHub and nothing is committed. `actionlint` passes, but `zizmor` reports one high finding on the Slack action.

**Before you merge**, or the deploy will fail or be too open (steps and trust policy are in the README):
1. Add the GitHub OIDC provider and the `deploy-widget` role in the new account.
2. Create a `production` environment and limit it to branch `main` and tag `v*`. This matters: the role trusts that environment, and if GitHub creates it automatically it has no restrictions.
3. After a successful deploy, delete the two old AWS secrets and revoke the key in the old account.

**What you asked for**
- **AWS:** the trust policy matches one exact subject, `repo:OWNER/REPO:environment:production`, which covers both `main` and tags. There's no git remote, so fill in `OWNER/REPO` yourself.
- **Slack:** same action, input and secret, and it still runs only after a successful deploy. It's now a separate job, so it can't see the AWS credentials.
- **README:** updated with the triggers, AWS and GitHub setup, and old key cleanup.

**Other changes I made**
- **Runner:** I moved from `self-hosted` to `ubuntu-latest`, because the README says the repository is public and outside code could end up running on your machine. If the real deploy needs tools or network access only that machine has, this will break it. Also check whether the runner is still registered, since changing this file doesn't remove that exposure.
- **Script injection:** the commit message was pasted straight into the shell script; it's now passed as an environment variable.
- **Permissions:** `write-all` is replaced with only what each job needs; the Slack job gets none.
- **Versions:** `actions/checkout` went from `@main` to v7.0.1, and the AWS action from v4 to v6.3.0, both pinned by commit SHA. v6.3.1 is only three days old, so I held it back. The AWS upgrade moves to Node 24 and is stricter about invalid true/false inputs.
- **Overlapping deploys:** only one deploy runs at a time. If several queue up, GitHub keeps only the newest waiting one, so pushing `main` and a tag together while another deploy runs can cancel one.

**Still open**
- **Slack action not pinned:** I couldn't read `some-org/slack-notify`, so it stays at `@v1`; it may be private or a placeholder. This is the `zizmor` finding (`unpinned-uses`), which I left visible rather than suppressing. It receives your webhook, so pin it once you can look up the commit. If it relied on the old token permissions or checked-out files, it will now fail.
- **Limited checks:** `gh` isn't logged in, so `zizmor` ran offline, without its checks that need the GitHub API.

To verify, push to `main` after the setup and confirm the role is assumed and the Slack message arrives, then push a test `v*` tag. Both will run a real deploy.
