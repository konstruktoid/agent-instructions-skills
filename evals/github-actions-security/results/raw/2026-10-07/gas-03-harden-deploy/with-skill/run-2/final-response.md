I switched the deploy workflow to OIDC and added the `v*` tag trigger, but I haven't run it on a runner. `actionlint` is clean. `zizmor` (pedantic) reports no findings, though it also says "1 suppressed" and I didn't find out what that was. No `zizmor.yml` suppression file exists, and I added no suppressions.

**Changes to `.github/workflows/deploy.yml`**
- **AWS:** the job assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1`. It has `id-token: write` and `contents: read`, and the static key inputs are gone.
- **Trigger:** it deploys on pushes to `main`, on pushes of tags matching `v*`, and on manual dispatch as before.
- **Hardening:**
  - Token permissions were `write-all`. They're now `permissions: {}` at workflow level, with only the two scopes above on the job.
  - Both actions are pinned to commit SHAs I looked up: `actions/checkout` v7.0.1 (previously `@main`) and `configure-aws-credentials` v6.3.0, released 2026-09-15.
  - Checkout no longer persists credentials, the job has a 15-minute timeout, and there's a concurrency group.
  - The commit message used to be interpolated straight into the shell script. It now goes through an environment variable.
- **Runner:** I moved the job from `self-hosted` to `ubuntu-latest`, because this repository is public and self-hosted runners aren't safe there. Tell me if you need a self-hosted runner for something specific.

**README:** it now lists the three triggers, and says the workflow uses OIDC and the old AWS secrets can be deleted. It also describes the role trust policy and Slack notification, and that the runner is GitHub-hosted.

**Things you need to act on**
- **Slack step:** `some-org/slack-notify@v1` doesn't exist as a public repo. I couldn't look up a release or SHA, so I couldn't pin it. I replaced it with a `curl` post of `{"text": "..."}` to the `SLACK_WEBHOOK` secret, which works for a standard Slack incoming webhook. If you rely on a private action or a custom message format, say so and I'll restore it.
- **Trust policy:** the IAM role's trust policy in the new account must match `sub` exactly, with no wildcard. It needs to allow `repo:<owner>/<repo>:ref:refs/heads/main` and `repo:<owner>/<repo>:ref:refs/tags/v*`. Without the tag entry, tag deploys will fail to assume the role. I didn't add a GitHub `environment:` with required reviewers. That would be a good gate for production, but it changes the `sub` format and needs setup in GitHub.
- **Cleanup:** delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets.
- **Unverified:** I haven't pushed anything or triggered the workflow, since that has effects outside this working copy. The AWS role assumption, the tag trigger and the Slack post are unverified until a push to `main` or a `v*` tag exercises them. I haven't committed any changes either.
