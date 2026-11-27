The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, the static keys are gone from it, and `v*` tag pushes trigger a deploy as well as pushes to `main`. `actionlint` passes, but I haven't run the workflow, so neither the AWS role assumption nor the Slack message is tested.

**What you asked for**
- **AWS:** the step uses `role-to-assume`, and only the deploy job has `id-token: write`.
- **Triggers:** pushes to `main`, `v*` tags and manual runs.
- **Slack:** same action, webhook secret and success-only behaviour, but now in its own `notify` job.
- **README:** covers the triggers, OIDC setup, a sample trust policy and tag protection.

**Other security fixes I made**
- **Shell injection:** the commit message was pasted straight into the shell script, so a crafted message could run commands on your runner. It's now passed through an environment variable.
- **Permissions:** `write-all` is now `contents: read`, and checkout no longer leaves the GitHub token in the git config. If `deploy.sh` is later changed to push to the repo, it will need both back.
- **Action versions:** `checkout` (was `@main`) is pinned to v7.0.1, and `configure-aws-credentials` (was `@v4`) to v6.3.1, both by commit SHA.

**Before the first deploy**
1. In the new account, create the GitHub OIDC provider and the role's trust policy (sample in the README). Without them the AWS step will fail.
2. Check that the self-hosted runner is at least version 2.327.1, which these newer actions need.
3. Add a tag ruleset limiting who can create `v*` tags.

**After it works**
- Delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets, and deactivate then delete the IAM keys in the old account. Removing them from the workflow doesn't revoke them.

**Still open**
- **Slack action:** `some-org/slack-notify` returned nothing publicly, so it's still on the movable `@v1` tag. Confirm the owner and that it exists (it may be private or a placeholder), then pin it to a commit SHA. If it relied on files or variables from the deploy job, the split will break it, so check the first notification arrives.
- **Self-hosted runner on a public repo:** this is a significant risk. A fork's pull request can add its own workflow targeting the runner, depending on your approval settings. Require approval for all outside contributors, or use GitHub-hosted or single-use runners. The separate `notify` job doesn't fully isolate anything if both jobs share a persistent machine.
- **Overlapping deploys:** pushing a commit to `main` and tagging it starts two deploys, possibly at the same time. If `deploy.sh` can't handle that, add a `concurrency` group.
