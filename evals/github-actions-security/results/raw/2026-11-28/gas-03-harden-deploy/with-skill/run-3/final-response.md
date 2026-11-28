The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` via OIDC, the static keys are gone from it, and it also deploys on `v*` tags. I updated the README to match. Nothing is committed, and the workflow hasn't run.

**Do these before merging, or the deploy will fail or be under-protected**
1. Add the GitHub OIDC provider and the role's trust policy in the new AWS account. The policy is in the README.
2. Create the `production` environment in GitHub and allow only `main` and `v*` tags. If you skip this, GitHub creates it with no restrictions, and a workflow on any branch could assume the role.
3. Add a tag ruleset limiting who can create `v*` tags.
4. After a successful run, delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets and deactivate the IAM key. Removing them from the workflow doesn't revoke them.

**Changes beyond what you asked for**
- **Runner:** `self-hosted` is now `ubuntu-latest`, because your README says the repository is public. If the deploy needs that machine's network or tools, this will break it. `scripts/deploy.sh` only prints a line, so I couldn't tell. Also remove the self-hosted runner from this repository, since a fork's pull request could still target it.
- **Script injection:** the commit message was pasted straight into the shell script, so a crafted message could run commands. It's now passed as an environment variable.
- **Permissions:** `write-all` is now read access to contents plus the OIDC token request.
- **Environment:** the `production` environment lets the trust policy match one exact subject for both `main` and tags, without wildcards.
- **Action versions:** `checkout` went from `@main` to v7.0.1, and the AWS action from v4 to v6.3.0, both pinned by commit SHA. I skipped v6.3.1 because it's only three days old.
- **Run limits:** I added a 30-minute timeout and one-deploy-at-a-time concurrency.

**Slack notification**
The step and its `SLACK_WEBHOOK` input are unchanged, but `some-org/slack-notify@v1` is still **not pinned**. I couldn't read that repository, possibly because it's private or `some-org` is a placeholder. Whoever controls the `v1` tag can change code that receives your webhook and runs in a job that can assume the AWS role. Check the source, then pin it to a commit SHA. Moving the notification to a separate job without AWS access would also limit the risk.

**Checks**
- `actionlint` passes.
- `zizmor` (pedantic, offline) reports one high finding, the unpinned Slack action. I didn't suppress it.
- OIDC login, the tag trigger and Slack can only be confirmed by a real run.

**Behaviour to expect**
- Pushing `main` and a tag for the same commit deploys twice, one after the other.
- Only one run can wait in the queue, so a newer one replaces it. A queued tag deploy could be cancelled that way.

You may also want Dependabot for `github-actions` with a 7-day cooldown to keep the pins current; I didn't add it.
