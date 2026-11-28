I've switched the deploy to OIDC role assumption, added the `v*` tag trigger and updated the README. `actionlint` passes, but `zizmor` still reports one high finding on the Slack action. The workflow hasn't been run, and nothing is committed or pushed.

**What you asked for**
- The AWS step now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1`, and both static key inputs are gone.
- It deploys on pushes to `main`, pushes of `v*` tags, and manual runs.
- Slack keeps the same webhook and still fires only after a successful deploy. It's now a separate job, so that third-party action can't get the AWS credentials or request its own.
- The README covers the trigger, AWS trust policy, GitHub settings and Slack secret.

**Other changes to check**
- **Runner:** I moved from `self-hosted` to `ubuntu-latest`, because the README says the repo is public and outsiders can get code onto a self-hosted runner. If the deploy needs that machine's network or tools, tell me, and also check this before merging. Otherwise, deregister the runner.
- **Environment:** the job now uses a `production` environment, so AWS can match one exact value for both `main` and tags, with no wildcard.
- **Security fixes:** token permissions are cut from `write-all` to what each job needs. The commit message can no longer inject shell commands. Checkout no longer keeps its token.
- **Versions:** `actions/checkout` is pinned to v7.0.1. `configure-aws-credentials` is pinned to v6.3.0 (up from v4) rather than v6.3.1, which is only 3 days old.
- **Run limits:** deployments now run one at a time, with job timeouts.

**Before the first deploy**
1. In the new AWS account, add the GitHub OIDC provider and set the role's trust policy as shown in the README.
2. In GitHub, create the `production` environment and limit it to the `main` branch and `v*` tags. **Without this, a workflow on any branch can assume the role.**
3. After a successful run, delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets, and deactivate then delete the keys in the old account. Removing them from the workflow doesn't revoke them.

**Still open**
- **Slack action:** `some-org/slack-notify@v1` is still unpinned (`zizmor`: `unpinned-uses`). I couldn't access that repository, which may be private or a placeholder name. It receives your webhook, so pin it to a commit SHA you've checked. If `v1` doesn't resolve on GitHub, the notify job will fail.
- **Verification:** `zizmor` ran offline, and the `gh` CLI isn't logged in. To test, merge and watch the run, then push a `v*` tag and confirm both the deploy and the Slack message.
- **Double deploys:** pushing a commit to `main` and then tagging it deploys it twice. If several runs queue up, GitHub keeps only the newest waiting one.
- **Dependabot:** there's no config to keep the pinned versions current. I can add one if you like.
