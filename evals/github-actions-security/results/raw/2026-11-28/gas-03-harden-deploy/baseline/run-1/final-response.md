The deploy workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, with no static keys left in the repo. It also runs on `v*` tag pushes. `actionlint` passes, but I haven't run the workflow or tested the role assumption.

**What you asked for**
- **AWS:** `role-to-assume` replaces the two access key inputs, and the deploy job has `id-token: write`.
- **Triggers:** pushes to `main`, `v*` tags and manual runs.
- **Slack:** same action and webhook, and it still runs only after a successful deploy. It's now in its own `notify` job.
- **README:** covers the triggers, the OIDC setup and a trust policy for the role.

**Other hardening I added**
- **Permissions:** `write-all` is gone. The deploy job gets `contents: read` and `id-token: write`, and `notify` gets none.
- **Shell injection:** the commit message was pasted straight into the script, so a crafted message could run commands with your AWS access. It's now passed as an environment variable.
- **Pinned actions:** `checkout` went from `@main` to the v7.0.1 commit, and the AWS action is pinned to v4.3.1. I also stopped `checkout` leaving its token on disk.
- **Slack isolation:** the separate job keeps the third-party action from requesting an AWS token or inheriting the deploy credentials. If it relied on files or environment variables from the deploy job, it won't have them now.

**Before the first deploy**
1. In the new account, create the OIDC provider and apply the trust policy from the README, replacing `OWNER/REPO`. It must allow both `main` and `v*` tags, or tag deploys will be refused.
2. Once a deploy works, delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets and deactivate those keys in the old account. Removing them from the workflow doesn't revoke them.

**Still open**
- **Self-hosted runner on a public repo:** this is the biggest remaining risk. A fork pull request can add its own workflow that targets your runner, and what it leaves behind could affect later deploys. Use GitHub-hosted or single-use runners if you can; otherwise require approval for all outside contributors' workflow runs. The separate `notify` job doesn't isolate much if both jobs share a persistent machine.
- **Slack action not pinned:** `some-org/slack-notify@v1` is still a movable tag because I couldn't access that repository to look up its commit. It may be a placeholder or private; pin it to a commit SHA if it's real.
- **Who can deploy:** anyone who can push a `v*` tag can now deploy that commit, even if it isn't on `main`. Add a tag ruleset to limit who can create those tags.
- **AWS action version:** v4.3.1 runs on Node 20, which GitHub is phasing out. Plan an upgrade to v6. `checkout` v7 needs a runner recent enough for Node 24.

The changes are in your working tree, not committed.
