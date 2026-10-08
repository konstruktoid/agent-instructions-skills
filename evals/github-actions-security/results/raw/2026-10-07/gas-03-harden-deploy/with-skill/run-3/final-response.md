I updated the deploy workflow and README, but one finding is unresolved: `some-org/slack-notify@v1` is still pinned to a tag. `actionlint` is clean. `zizmor` (offline) reports one `unpinned-uses` error on that action. I never ran the workflow, so the OIDC login, the tag trigger and the Slack step are untested.

**Why Slack isn't pinned.** The GitHub API returns 404 for `some-org/slack-notify`, so I couldn't resolve a SHA and didn't invent one. The Slack step still works the same way, with a TODO comment on it. It probably needs the real owner and repo, then a SHA pin. That's your call.

**`zizmor` ran offline only.** Online mode aborts because it can't reach the same repo.

**What changed in `.github/workflows/deploy.yml`:**
- **AWS:** the static keys are gone. The step now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC.
- **Trigger:** it now also runs on pushed `v*` tags, as well as pushes to `main` and manual dispatch.
- **Permissions:** `permissions: write-all` became `permissions: {}`. The job gets only `contents: read` and `id-token: write`.
- **Runner:** `self-hosted` became `ubuntu-latest`, because this repo is public and self-hosted runners aren't safe there. If the deploy depends on something only that runner has, tell me.
- **Environment:** the job now uses a `production` environment. That gives branch and tag runs the same OIDC subject, `repo:OWNER/REPO:environment:production`, so the AWS trust policy can match one exact value.
- **Commit message:** the commit message is now passed through `env:` instead of being interpolated into the `run:` block, which was an injection risk.
- **Pinned actions:**
  - `actions/checkout`: v7.0.1, with `persist-credentials: false`.
  - `aws-actions/configure-aws-credentials`: v6.3.0, released 22 days ago.
- **Smaller additions:** `timeout-minutes: 15`, a job name, and concurrency that doesn't cancel an in-flight deploy.

**What you need to do outside the repo:**
- Create the `production` environment and restrict its deployments to `main` and `v*` tags.
- In the new AWS account, set up the OIDC provider and the role's trust policy. It should require `aud` = `sts.amazonaws.com` and `sub` equal to exactly `repo:OWNER/REPO:environment:production`.
- Delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets.

The README now covers the tag trigger and the OIDC setup. I made no commits.
