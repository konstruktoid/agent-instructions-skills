The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, no longer references the static keys, and also deploys on `v*` tags. `actionlint` passes. I couldn't run the workflow, so the role assumption, the tag trigger and the Slack message are untested. The changes are uncommitted.

**Changes in `.github/workflows/deploy.yml`**
- **AWS and triggers:** these are the changes you asked for. Manual runs still work.
- **Permissions:** `write-all` is replaced with `contents: read` and `id-token: write` on the deploy job.
- **Slack:** it's now a separate `notify` job that runs only after a successful deploy, as before. This keeps the third-party action away from the AWS credentials and the OIDC token. If it reads files from the checkout, it will need adjusting.
- **Script injection:** the commit message was pasted straight into the shell script, so a crafted message could run commands. It's now passed as an environment variable.
- **Pinning:** `checkout` (previously `@main`, now v7.0.1) and the AWS credentials action (v4.3.1) are pinned to commit SHAs. `checkout` also no longer leaves the GitHub token on the runner.

The README now covers the triggers, the OIDC setup, an IAM trust policy and the one remaining secret.

**Before merging**
1. In the new AWS account, create the OIDC provider and the `deploy-widget` role using the trust policy in the README. `123456789012` is also AWS's usual documentation placeholder, so check it's your real account ID.
2. Check that `scripts/deploy.sh` and its targets work in the new account. The current script only prints "deploying".

**After a successful deploy**
- Delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` repository secrets, and deactivate the keys in the old account. Removing them from the workflow doesn't revoke them.
- Check the runner for leftover credentials, such as `~/.aws/credentials` or an instance role.

**Still open**
- **Self-hosted runner on a public repo (the biggest risk):** a pull request from a fork can add its own workflow that targets your runner. Require approval for all outside contributors, and preferably use GitHub-hosted or single-use runners. The separate `notify` job doesn't fully isolate anything if both jobs share a persistent machine.
- **Slack action:** I couldn't access `some-org/slack-notify`, which may be private or a placeholder, so it's still on the movable `@v1` tag. Pin it to a commit SHA once you've checked it.
- **Who can deploy:** anyone who can push a `v*` tag can now deploy, even from a commit that isn't on `main`. Add a tag ruleset to limit who can create those tags.
- **Overlapping deploys:** pushing to `main` and tagging the same commit deploys it twice, possibly at the same time. If that's a problem, add a `concurrency` group.
