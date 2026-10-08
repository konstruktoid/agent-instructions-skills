The deploy workflow now uses OIDC and triggers on `v*` tags. One finding is still open: the Slack action isn't pinned to a commit SHA. `actionlint` is clean. `zizmor` (offline, pedantic) has one high finding, `unpinned-uses` on `some-org/slack-notify@v1`. Its online audit fails because that repo isn't reachable through the GitHub API with my credentials. I haven't run the workflow, so none of this has been exercised on a runner.

**Changes to `.github/workflows/deploy.yml`:**
- **AWS:** the step assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1`. The static access keys are gone, and the job has `id-token: write` and `contents: read`.
- **Triggers:** it now runs on pushes to `main`, on `v*` tags, and on manual dispatch.
- **Slack:** the notify step still reads `SLACK_WEBHOOK`.
- **Runner:** it moved from `self-hosted` to `ubuntu-latest`, because this repo is public and a self-hosted runner can't be made safe there. If you need the self-hosted runner for network access, tell me and we'll look at it separately.
- **Hardening:**
  - Workflow-level `permissions: {}`, with scopes granted on the job.
  - `checkout` and `configure-aws-credentials` pinned to commit SHAs (v7.0.1 and v6.3.0).
  - `persist-credentials: false` on checkout.
  - A 15-minute job timeout.
  - Concurrency set so a running deploy is never cancelled.
  - The commit message now goes through `env:` instead of being interpolated into the `run:` script, which was an injection hole.

**Still open on your side:**
- **Slack pin:** pin `some-org/slack-notify` to a SHA once you can resolve it. I left a TODO on that line.
- **IAM trust policy:** it must allow `sub` for `refs/heads/main` and for `refs/tags/v*`. Without the tag entry, tag deploys will fail at role assumption.
- **Old secrets:** the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets can be deleted.

I updated the README with the new triggers, the OIDC setup, and the trust-policy requirement.
