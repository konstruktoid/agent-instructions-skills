The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, the static keys are gone from it, and it also deploys on `v*` tags. The README is updated. Nothing is committed, and the workflow hasn't run.

**Do this before merging**
1. **GitHub environment:** create `production` and limit it to branch `main` and tags `v*`. If it doesn't exist, GitHub creates it unprotected on the first run, and any branch that uses it could assume the role.
2. **AWS:** add the OIDC provider and role in the new account, using the trust policy in the README. Check your repository's actual `sub` claim format.
3. **After a successful deploy:** delete the two GitHub secrets, and deactivate and delete the key in the old AWS account.

**Changes you didn't ask for**
- **Runner:** moved from `self-hosted` to `ubuntu-latest`, because the README says the repository is public. If `deploy.sh` will need tools or private network access from your machine, this will break it. Also remove that runner's registration for this repository, since editing the workflow doesn't do that.
- **Environment:** added `production`, so branch and tag deploys share one exact trust condition with no wildcard.
- **Slack:** moved to its own `notify` job so the action can't see the AWS credentials. It still runs only after a successful deploy, with the same webhook input.
- **Hardening:**
  - Replaced `write-all` with per-job permissions.
  - Fixed a shell injection through the commit message.
  - Added timeouts and made deploys run one at a time.
  - Stopped checkout from keeping its token.
- **Versions:** `actions/checkout` is pinned to v7.0.1 (was `@main`). The AWS action is pinned to v6.3.0 (was `@v4`); v6.3.1 came out yesterday, so I held it back. v5 changed how invalid boolean inputs are handled and v6 moved to Node 24; neither should affect this setup.

**Still open: the Slack action**
`some-org/slack-notify@v1` is still on a movable tag. GitHub's public API returns Not Found for it, so it may be private or a placeholder, and I couldn't get a commit SHA or read its code.

- **Pin it:** if it's real, pin it to a full SHA.
- **Check it still works:** the new job has no checkout and its `GITHUB_TOKEN` has no permissions. If the action needs either, it will fail or post less than before.

**Checks**
- `actionlint` passes.
- `zizmor` (pedantic, offline) reports one high finding, the unpinned Slack action. I didn't suppress it.
- The stricter auditor mode also notes that `SLACK_WEBHOOK` isn't held in an environment.
- The AWS role, the tag trigger and Slack can only be verified by a real run. A push to `main` and then a `v*` tag would cover them.

You might also add a Dependabot config for `github-actions` with a 7-day cooldown, so the pinned versions stay current.
