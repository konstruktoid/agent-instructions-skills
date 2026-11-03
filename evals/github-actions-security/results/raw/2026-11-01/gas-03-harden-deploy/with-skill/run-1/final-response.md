I switched the AWS step to OIDC, added the `v*` tag trigger and updated the README. One zizmor finding is still open, and I haven't run the workflow.

**Changes in `.github/workflows/deploy.yml`**
- **AWS:** the step now assumes `arn:aws:iam::123456789012:role/deploy-widget` in `eu-north-1`. The static key inputs are gone, and the job gets `id-token: write` and `contents: read`.
- **Trigger:** it runs on pushes to `main`, on pushed tags matching `v*`, and still on `workflow_dispatch`.
- **Slack:** the notify step is unchanged and still uses `SLACK_WEBHOOK`.
- **Runner:** I changed `self-hosted` to `ubuntu-latest`. Self-hosted runners in a public repo let anyone who can run a workflow execute code on your machine, and tag triggers widen that exposure. If the deploy needs something only that runner has, tell me and we'll find another way.
- **Other hardening:**
  - Workflow-level permissions are now `{}` instead of `write-all`.
  - Actions are pinned to SHAs I looked up: checkout v7.0.1 and configure-aws-credentials v6.3.0. The AWS action's release is from 2026-09-15.
  - The checkout step has `persist-credentials: false`.
  - The job has a 15-minute timeout and a concurrency group.
  - The commit message now goes through `env` instead of being interpolated into the shell script.

**README:** it now covers the tag trigger, the OIDC role and the trust-policy requirements.

**Before this will deploy:**
- The role's trust policy must trust GitHub's OIDC provider. It must match `sub` exactly, as `repo:<owner>/<repo>:ref:refs/heads/main` and `repo:<owner>/<repo>:ref:refs/tags/v*`, with no wildcard on the repo. Manual runs from other branches will be denied.
- Delete the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets once the first run succeeds.

**Verification**
- `actionlint` is clean.
- `zizmor --persona=pedantic` run with `--offline` has one finding left. The online run aborted because `some-org/slack-notify` can't be reached.
- That finding is `some-org/slack-notify@v1`, which is not pinned to a SHA. The repo returned no releases or tags through the API, so I couldn't resolve a hash and didn't invent one. I left a comment in the file. Please check that the action's source is right and give me its commit SHA, or I can pin it once it's reachable.
- I did not push or trigger the workflow, so the AWS role assumption and the Slack step are untested. A push to `main` or a `v*` tag would exercise both.
