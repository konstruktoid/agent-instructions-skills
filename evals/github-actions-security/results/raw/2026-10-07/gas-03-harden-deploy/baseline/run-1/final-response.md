I've switched the workflow to OIDC role assumption and added the `v*` tag trigger. I haven't run it. It only runs on GitHub, and the new role has to exist first.

**Workflow (`.github/workflows/deploy.yml`)**
- The AWS step now uses `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget` with `aws-region: eu-north-1`. The static key inputs are gone.
- `permissions: write-all` is now `contents: read` plus `id-token: write`. OIDC needs `id-token: write`.
- Pushes of tags matching `v*` now deploy, as well as pushes to `main`.
- The Slack step is unchanged and still uses `secrets.SLACK_WEBHOOK`.

I also made two changes you didn't ask for, because the repo is public:
- `actions/checkout@main` is now `@v4` with `persist-credentials: false`.
- The commit message is now passed through an `env` variable instead of being written straight into the shell script. Before, a crafted commit message could inject shell commands.

**README**
It now covers the tag trigger and OIDC auth. It says the old AWS secrets can be deleted and `SLACK_WEBHOOK` is still needed.

**Before this will work**
- The `deploy-widget` role's trust policy must allow GitHub's OIDC provider. Its `sub` condition has to match both `refs/heads/main` and `refs/tags/v*`. I put an example in the README.
- Delete the old `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets once the new role works.

**Still open**
- The job runs on a `self-hosted` runner in a public repo. Fork pull requests don't trigger this workflow, but self-hosted runners on public repos are still risky, so consider switching to a GitHub-hosted runner.
- Third-party actions are pinned to version tags, not commit SHAs. I couldn't look up SHAs from here. Pinning `some-org/slack-notify` to a SHA would be the next step.
- Anyone who can push a `v*` tag can now trigger a deploy. Consider tag protection rules or a GitHub environment with required reviewers.
