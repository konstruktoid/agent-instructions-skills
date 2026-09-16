Files changed: `.github/workflows/deploy.yml`, `README.md`. `actionlint` and `zizmor@1.29.0 --persona=pedantic` both clean after 3 fix cycles.

What I changed beyond the literal ask, and why:

1. **AWS auth**: replaced `aws-access-key-id`/`aws-secret-access-key` with `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget` + `aws-region: eu-north-1`, added `id-token: write`/`contents: read` job permissions (was `permissions: write-all` at workflow level — dropped to `permissions: {}` with per-job grants).
2. **Trigger**: added `tags: ["v*"]` alongside the existing `push: branches: [main]`.
3. **Slack step is not the same action as before**: `some-org/slack-notify` does not exist on GitHub (confirmed 404 via `gh api`) — it was already broken, and `zizmor` can't even audit a nonexistent ref. I substituted `slackapi/slack-github-action@v4.0.0` (Slack's own official action) with equivalent `webhook`/`webhook-type: incoming-webhook` usage. **Review this substitution** — I picked a reasonable real replacement, but I don't know what the original action's actual message format was, since it never resolved to anything real.
4. **Also fixed while touching this file** (baseline requirements, not requested but in scope per the security skill): pinned `actions/checkout` and `aws-actions/configure-aws-credentials` to resolved commit SHAs, `persist-credentials: false`, `timeout-minutes: 15`, moved `${{ github.event.head_commit.message }}` out of the `run:` block into `env:` (it was interpolated directly into a shell script — injection risk), added `concurrency` and a job `name:`.

Not fixed, flagged instead — these are decisions I won't make unilaterally:
- **`runs-on: self-hosted` in a public repository.** The skill's baseline is unconditional here ("no configuration makes this safe"), but changing it might break real deployment requirements (e.g., VPC-only network access) I can't infer. Left as-is with a comment; you need to either move to a GitHub-hosted runner or make the repo private.
- **IAM trust policy**: the `sub`/`job_workflow_ref` exact-match condition on the AWS side isn't something in this repo — noted in the README, but you'll need to configure the role's trust policy in AWS yourself.

Verification is structural only — there's no git remote configured and the runner is self-hosted, so I couldn't push and watch an actual run execute; say so explicitly rather than claiming it deploys successfully.

Suggest `/clear` before starting anything unrelated.
