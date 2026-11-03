I switched the workflow to OIDC and added the `v*` tag trigger. The Slack action is still unpinned, and I haven't run the workflow.

**Changes (`.github/workflows/deploy.yml` and `README.md`)**
- **AWS:** the step now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1`, and the static key inputs are gone. The job has `id-token: write` and `contents: read`; workflow-level permissions are `{}`.
- **Trigger:** pushes to `main` and tags matching `v*` both deploy, and `workflow_dispatch` is kept.
- **README:** it now covers the tag trigger, OIDC and the role trust policy requirements.
- **Runner:** I moved the job from `self-hosted` to `ubuntu-latest`, which you didn't ask for. The repo is public, and self-hosted runners must not be used on public repos. Revert it if you have a reason.
- **Commit message:** I moved `${{ github.event.head_commit.message }}` out of the `run:` block into an env var. It was a script-injection risk.
- **Pinning:** `actions/checkout` is pinned to v7.0.1 and `configure-aws-credentials` to v6.3.0 (released 2026-09-15). Both SHAs came from the GitHub API. I also set `persist-credentials: false` and a 15-minute timeout.

**Open items for you**
1. **Slack action is unpinned.** `some-org/slack-notify` returns 404 from the GitHub API, so I couldn't look up a release or SHA. I left it as `@v1` with a TODO comment, so the notification should behave as before. If the action is private or has moved, pin it once you can resolve it.
2. **Checks:** actionlint is clean. zizmor, run with `--offline`, reports one high finding: that unpinned Slack action. Online, zizmor aborts on the unresolvable repo.
3. **IAM trust policy:** it must allow the `sub` claim for both `repo:OWNER/REPO:ref:refs/heads/main` and `repo:OWNER/REPO:ref:refs/tags/v*`. If it only allows `main`, tag deploys will fail to assume the role. Avoid a wildcard like `repo:OWNER/REPO:*`.
4. **Old secrets:** delete `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from the repo.

The workflow hasn't run. I didn't push or trigger it, since both would act on your remote and your AWS account, so the OIDC assumption and the tag deploy are untested. Pushing a `v*` tag after the trust policy is updated would exercise both.
