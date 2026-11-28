The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, the static keys are gone, and pushing a `v*` tag triggers a deploy. `actionlint` passes. I haven't run the workflow or touched AWS, and nothing is committed.

**What you asked for** (`.github/workflows/deploy.yml`, `README.md`)
- `role-to-assume` replaces the two access key inputs.
- Slack notification still runs only after a successful deploy, with the same action and secret. It's now a separate `notify` job.
- The README covers the triggers, AWS setup, an example trust policy and the runner requirement.

**Security fixes I made along the way**
- **Command injection:** the commit message was pasted straight into the shell script, so a crafted message could run commands on your runner. It's now passed as an environment variable.
- **Permissions:** `write-all` is replaced with `contents: read` and `id-token: write` on the deploy job, and none on `notify`. This also keeps the third-party Slack action from requesting an AWS token.
- **Pinned actions:** `checkout` was tracking `@main` and is now pinned to the v7.0.1 commit. The AWS action moved from v4 to a pinned v6.3.1, a major version upgrade. Checkout also no longer leaves its token on disk.

**Before the first deploy**
1. In the new account, create the GitHub OIDC provider and the `deploy-widget` role. The trust policy must allow both `main` and `v*` tags, or tag deploys will fail. Replace `OWNER/REPO` with your repository.
2. Check that your self-hosted runner is version 2.327.1 or later.
3. Once a deploy succeeds, delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets, and deactivate the keys in the old account.

**Still open**
- **Slack action not pinned:** I couldn't access `some-org/slack-notify` anonymously, so it's still on `@v1`. It receives your webhook, so confirm it's the action you intend and pin it to a commit SHA.
- **Self-hosted runner on a public repo:** this is the biggest remaining risk. This workflow doesn't run on pull requests, but a fork's pull request can add a workflow that targets your runner. Require approval for all outside contributors, or use GitHub-hosted or single-use runners. The separate `notify` job gives little isolation if both jobs share a persistent machine.
- **Who can deploy:** anyone who can push a `v*` tag can now deploy, even from a commit that isn't on `main`. Add a tag ruleset to limit who can create those tags.
- **Overlapping deploys:** pushing `main` and a tag together starts two deploys of the same commit. If `deploy.sh` can't handle that, add a `concurrency` group.
