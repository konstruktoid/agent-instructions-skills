The workflow now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1` through OIDC and no longer uses the static AWS keys. It also deploys on `v*` tag pushes. `actionlint` exits clean, and `zizmor` (pedantic, version 1.31.1) reports no findings, with one finding suppressed by default and no `zizmor.yml` in the repo. I haven't run the workflow, so the AWS role assumption and the Slack post are untested. I haven't committed anything.

- **Triggers:** it runs on pushes to `main`, on `v*` tag pushes, and still on manual dispatch.
- **Permissions:** the workflow-level `write-all` is replaced by `permissions: {}`. The deploy job gets only `contents: read` and `id-token: write`.
- **Runner:** I changed the runner from `self-hosted` to `ubuntu-latest`. A self-hosted runner in a public repository isn't safe, because anyone can open a pull request against it. If the deploy needs something that only your runner has, tell me and we'll look at it separately.
- **Pinning:** `actions/checkout` is now pinned to v7.0.1 and `aws-actions/configure-aws-credentials` to v6.3.0 (released 2026-09-15), each by a commit SHA I looked up. The AWS action's v6 line needs a newer Actions runner, which GitHub-hosted runners have.
- **Other hardening:**
  - Checkout no longer persists credentials.
  - The job has a 15-minute timeout.
  - A `concurrency` group prevents overlapping deploys.
  - The commit message is passed through `env:` instead of being interpolated into the script, which closes a script-injection hole.
- **Slack:** I couldn't resolve `some-org/slack-notify`. It has no releases, so I couldn't pin it. I replaced it with a `curl` post to `SLACK_WEBHOOK`, which sends a plain-text message with the repository, ref and short SHA. If the old action sent a richer message, say so and I'll match it, or give me a real action to pin.
- **README:** it now covers the tag trigger, the OIDC role, and the Slack notification.

You still need to do these on the AWS and GitHub side:

- **Trust policy:** the role's policy has to allow both subject claims, `repo:<owner>/<repo>:ref:refs/heads/main` and `repo:<owner>/<repo>:ref:refs/tags/v*`, with no wildcard on the repository. The README spells this out.
- **Old secrets:** delete `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
- **Tag protection (optional):** consider a tag ruleset so only trusted people can push `v*` tags, since a tag push now deploys.
- **Environment gate (optional):** consider adding a protected `environment:` for deploy approval. That changes the OIDC `sub` claim, so I left it out.
