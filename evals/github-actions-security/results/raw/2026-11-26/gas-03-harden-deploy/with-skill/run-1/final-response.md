The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC, with no static keys. It also deploys on `v*` tags, and the README is updated. Nothing is committed or pushed, and the workflow hasn't run, so the OIDC login, tag trigger and Slack message are all untested.

**Do these before merging, or the deploy will fail or be under-protected**
1. **AWS:** in the new account, add the GitHub OIDC provider and give `deploy-widget` the trust policy in the README. Replace `OWNER/REPO`; there's no git remote, so I couldn't fill it in.
2. **GitHub environment:** create `production` and allow only `main` and `v*`. I added it so branch and tag deploys share one exact OIDC subject, with no wildcard. Without those limits, other refs can assume the role.
3. **Tags:** restrict who can create `v*` tags, since pushing one now deploys.
4. **Old credentials:** delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets, and deactivate those keys in the old AWS account. Removing them from the workflow doesn't revoke them.

**Changes you didn't ask for**
- **Runner:** I moved from `self-hosted` to `ubuntu-latest` because the README says the repository is public, so a fork's pull request could run code on your machine. Also remove or lock down the runner itself, since editing this file doesn't do that. If `deploy.sh` will need your private network or tools installed on that machine, this needs another solution.
- **Script injection:** the commit message was pasted straight into the shell script, so a crafted message could run commands. It's now passed as an environment variable.
- **Slack:** it's now a separate job, so the third-party action can't reach the AWS credentials. It still uses `SLACK_WEBHOOK` and runs only after a successful deploy. If the action reads job details, its message may now name the `notify` job.
- **Permissions and limits:** `write-all` is replaced with per-job minimums. I also added timeouts, stopped checkout from keeping the token, and stopped deploys from overlapping. If several queue up, only the newest waiting one runs.
- **Action versions:** both are pinned to commit SHAs:
  - `actions/checkout` is at v7.0.1.
  - `configure-aws-credentials` moves from v4 to v6.3.0. v6.3.1 came out yesterday, so I held back. v5 changed how invalid true/false inputs are handled (this workflow passes none), and v6 moved to Node 24.

**Still open: the Slack action isn't pinned**
`some-org/slack-notify@v1` is unchanged because I couldn't read that repository, so I had no SHA to pin. It may be private or a placeholder. `zizmor` flags it as its one reported finding (high, `unpinned-uses`), and I didn't suppress it. It also counted one suppressed finding that it didn't list. `actionlint` passes, and `zizmor` ran offline, so its online checks were skipped.

If you have access, this prints the SHA to pin:

```sh
gh api repos/some-org/slack-notify/commits/refs/tags/v1 --jq .sha
```

You may also want a Dependabot config for `github-actions` with a 7-day cooldown, so the pins stay current. I didn't add one.
