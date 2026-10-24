The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in eu-north-1 through OIDC, and the static AWS keys are gone. One zizmor finding is still open. The workflow has not run, because I didn't push or trigger anything.

**What changed in `.github/workflows/deploy.yml`:**
- **OIDC:** the job has `id-token: write` and `contents: read`, and `permissions: {}` at workflow level.
- **Tags:** it now also runs on pushed tags matching `v*`, as well as `main` and manual dispatch.
- **Runner:** I changed `self-hosted` to `ubuntu-latest`. The repo is public, and a self-hosted runner there lets anyone who can run workflow code reach your machine. If the deploy needs that runner's network, say so and we'll find another way.
- **Injection fix:** the commit message was interpolated straight into the shell script. It now goes through `env:`.
- **Pinning:**
  - `actions/checkout` is pinned to v7.0.1.
  - `configure-aws-credentials` is pinned to v6.3.0.
  - Both SHAs and versions were looked up just now.
  - Checkout also gets `persist-credentials: false`.
- **Smaller additions:** I added a 15-minute job timeout, a job name, and a concurrency group that queues deploys instead of cancelling them.
- **Slack:** the Notify step still uses `SLACK_WEBHOOK`, unchanged.

**README:** it now covers the tag trigger, OIDC, and what the role's trust policy needs.

**Checks:** actionlint is clean. zizmor, run offline, reports one high finding: `some-org/slack-notify@v1` is not pinned to a commit. I couldn't resolve that repo through the GitHub API (404), so I left it on `@v1` with a TODO comment. Give me the real repo, or pin it yourself.

**Still to do on your side:**
- **Trust policy:** the `deploy-widget` trust policy must allow both the `main` and the `v*` tag subjects:
  - `repo:<owner>/<repo>:ref:refs/heads/main`
  - `repo:<owner>/<repo>:ref:refs/tags/v*`
  - Avoid a `repo:<owner>/<repo>:*` wildcard, because it would trust pull requests and every branch.
- **Old secrets:** delete the old `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` repository secrets.
- **Optional gate:** consider a protected `production` environment with a tag rule. That would change the `sub` claim you match in the trust policy.
