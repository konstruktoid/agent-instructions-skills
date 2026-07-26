Both `actionlint` and `zizmor --persona=pedantic` are clean. Not creating a commit unless you want one — let me know.

Summary of changes to `.github/workflows/deploy.yml`:

- **OIDC instead of static keys**: `aws-actions/configure-aws-credentials` now uses `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1`; the `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` secrets are gone, replaced by job-scoped `id-token: write`.
- **Tag trigger added**: `push.tags: ['v*']` alongside the existing `main` branch push and `workflow_dispatch`.
- **Slack notification kept**: unchanged step, still pulls `secrets.SLACK_WEBHOOK`.
- **Baseline hardening** (per the github-actions-security skill): `permissions: {}` at workflow level with `contents: read`/`id-token: write` scoped to the job; `actions/checkout` and `configure-aws-credentials` pinned to resolved commit SHAs (latest releases, v7.0.1 / v6.2.3) with `persist-credentials: false`; `runs-on` switched from `self-hosted` to `ubuntu-latest` since the repo is public (README says so) and self-hosted runners are never safe there; `timeout-minutes: 15`; a `concurrency` group to prevent overlapping deploys; the commit-message interpolation moved out of the `run:` shell text into a quoted `env:` var to close a script-injection hole.
- **One unresolved item**: `some-org/slack-notify@v1` doesn't correspond to a real GitHub repository (404 from the API), so it can't be pinned to a SHA — I left it as-is, documented why in a workflow comment, and added a scoped, commented suppression in the new `zizmor.yml` rather than silently ignoring the finding. Worth swapping in the org's actual Slack action (pinned) when you know what it really is.

README updated to describe OIDC auth, the new tag trigger, and why the runner is GitHub-hosted.
