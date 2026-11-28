The AWS step now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, the static key inputs are gone, and pushing a `v*` tag now triggers a deploy. `actionlint` passes, but I haven't run the workflow, so neither the role assumption nor the Slack message is tested.

**Changes you asked for**
- **Workflow:** added the OIDC role and the tag trigger.
- **Slack:** the `Notify` step is unchanged and still runs only after a successful deploy.
- **README:** covers the triggers, the AWS setup with a trust policy, Slack and the runner.

**Hardening I added**
- **Permissions:** `write-all` is now `contents: read` plus `id-token: write`. If the Slack action relies on the default `GITHUB_TOKEN` for more than that, it will need the extra permission.
- **Script injection:** the commit message was pasted directly into the shell script, so a crafted message could run commands on your runner. It's now passed as an environment variable.
- **Pinned actions:** `checkout` (was `@main`, now v7.0.1) and `configure-aws-credentials` (was v4, now v6.3.1) are pinned to commit SHAs. These need runner 2.327.1 or newer, so check yours.

**To do before the first deploy**
1. In the new account, create the OIDC provider and the role. The trust policy must allow both `main` and `v*` tags; the README has it, with `OWNER/REPO` to fill in.
2. After a successful deploy, delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets in GitHub, and deactivate the keys in the old account. Removing them from the workflow doesn't revoke them.
3. Check `scripts/deploy.sh` for anything tied to the old account. The version here only prints "deploying".

**Risks still open**
- **Self-hosted runner on a public repo:** this is the biggest one. A pull request from a fork can add its own workflow that targets your runner, subject to your approval settings. Use a GitHub-hosted runner if you can. Otherwise require approval for all outside contributors and use an ephemeral, isolated runner.
- **Slack action:** I couldn't read `some-org/slack-notify` (it's private, missing or a placeholder), so it's still on the movable `@v1` tag. It runs in the same job as the deploy, so it can use the AWS role. Check its source and pin it to a SHA. Moving it to a separate job without `id-token` would isolate it further, though less reliably on a shared self-hosted runner.
- **Who can deploy:** anyone who can push a `v*` tag can deploy that commit, even if it isn't on `main`. Add a tag ruleset to limit who can create those tags.
- **Double deploys:** pushing `main` and a tag together starts two runs, which could overlap. If `deploy.sh` can't handle that, add a `concurrency` group.

Nothing is committed; the changes are in your working tree.
