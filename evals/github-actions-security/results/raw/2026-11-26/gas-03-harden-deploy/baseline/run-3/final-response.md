The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, the static keys are gone, and `v*` tags trigger a deploy as well as `main`. I updated the README to match. `actionlint` passes and the YAML parses, but I haven't run the workflow, so the role assumption and Slack message are untested. The changes are not committed.

**Other changes I made**
- **Script injection:** the commit message was pasted directly into the shell script, so a crafted message could run commands on your runner, now with access to the AWS role. It's passed as an environment variable instead.
- **Permissions:** `write-all` is replaced with only `contents: read` and `id-token: write` on the deploy job.
- **Pinned actions:** `checkout` (was `@main`, now v7.0.1) and `configure-aws-credentials` (was v4, now v6.3.1) are pinned to commit SHAs. Both need a runner that supports Node 24.
- **Slack:** the notification is now a separate `notify` job with the same action and webhook, so it can't request AWS credentials. It still runs only after a successful deploy. If the action relies on files or variables from the deploy job, it would need adjusting.
- **Concurrency:** deploys no longer run in parallel. Pushing `main` and a tag together still deploys twice, one after the other. GitHub keeps only one waiting run, so a newer push can cancel a queued one, including a tag deploy.

**Before the first run**
1. In the new account, create the OIDC provider and set the role's trust policy as shown in the README. Replace `OWNER/REPO` and check which `sub` format your repository uses. A tag deploy will fail if the policy only allows `main`.
2. Delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets, and deactivate those keys in the old account. Removing them from the workflow doesn't revoke them.

**Still open**
- **Slack action not pinned:** I couldn't access `some-org/slack-notify` (it may be private or a placeholder), so it stays on `@v1`. Pin it to a commit SHA, especially since it receives your webhook.
- **Self-hosted runner on a public repo:** this is the biggest remaining risk. A pull request from a fork can add its own workflow that targets your runner. Require approval for all outside contributors in the Actions settings, or use GitHub-hosted or single-use runners. Moving `notify` to another job doesn't protect against a compromised runner.
- **Who can deploy:** anyone who can push a `v*` tag can deploy the commit it points to, so add a ruleset restricting tag creation.
