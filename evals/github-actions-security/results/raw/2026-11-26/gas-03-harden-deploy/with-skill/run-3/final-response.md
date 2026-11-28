The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, the static keys are gone from it, and it also deploys on `v*` tags. It has not been run, so the AWS login, tag trigger and Slack message are all untested. `actionlint` passes, but `zizmor` (offline) still reports one high finding, on the Slack action.

**Do these before merging** (details are in the README):
1. **Create the `production` environment** and limit it to branch `main` and tag `v*`. Do this first: if the environment is missing, GitHub creates it with no restrictions.
2. **Add the OIDC provider and role trust policy** in the new account. The subject is `repo:OWNER/REPO:environment:production`, which covers branch and tag deploys without a wildcard. I found no git remote, so fill in `OWNER/REPO` yourself.
3. **Remove the old keys:** delete both GitHub secrets and deactivate the IAM key in the old account.
4. **Deregister the self-hosted runner** from this repository. The README says the repository is public, so a fork pull request could add a workflow that runs code on that machine. Changing this workflow alone doesn't close that.

**Changes you didn't ask for**
- **Runner:** the job now uses `ubuntu-latest`. If `deploy.sh` needs tools or network access that only your runner had, this will break it. The current script only prints a message.
- **Injection fix:** the commit message was pasted straight into the shell script, so a crafted message could run commands. It's now passed as an environment variable.
- **Permissions:** `write-all` is replaced by read access to contents plus `id-token: write` for the deploy job, and nothing for the notify job.
- **Slack:** it's now a separate `notify` job that still runs only after a successful deploy, so the Slack action can't get the AWS credentials. If it relied on files or variables from the deploy job, it won't have them. `SLACK_WEBHOOK` must be a repository or organization secret.
- **Action versions:** `checkout` is pinned to v7.0.1 and `configure-aws-credentials` to v6.3.0. I skipped v6.3.1 because it came out yesterday. The newer AWS action is a major upgrade from v4 (Node 24, stricter true/false inputs), though the two inputs used here are unaffected as far as the release notes show.
- **Limits:** I added job timeouts and allow only one deployment at a time. Pushing `main` and a tag together deploys twice, one after the other, and a newer queued run can replace an older waiting one.

**Still open**
- **Slack action not pinned:** I couldn't resolve `some-org/slack-notify` publicly (it may be private or a placeholder), so it stays at `@v1`. That is the high `zizmor` finding. If you have access, pin it to the commit SHA of its current release.
- **Webhook secret:** a stricter `zizmor` mode also warns that `SLACK_WEBHOOK` isn't tied to an environment. I left it that way so your existing secret keeps working.
- **Dependabot:** there's no configuration to keep the pinned actions updated. I'd suggest adding one for `github-actions` with a 7-day cooldown.

Nothing is committed or pushed.
