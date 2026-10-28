I couldn't review the role because it isn't in this repository. I searched every file for an IAM role, `assume_role`, an `aws_iam_*` resource, OIDC federation, AWS credential variables or a `terraform plan`/`apply` step, and found nothing. The only Terraform is `infra/main.tf`, which defines one security group. None of the CI definitions (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `Jenkinsfile`) run Terraform or assume a role. Whatever role production apply would use is defined somewhere else: another repo, the AWS console, or a CI-side secret.

To review it, I need one of these:
- the Terraform or JSON that defines the role, meaning its **trust policy** and its **permission policies** (attached and inline), or
- the path or repo where it lives, or the pipeline config that assumes it.

When I have it, I'll check:
- **Trust policy:** short-lived OIDC federation rather than static access keys; the condition keys are pinned to specific branches or environments (`sub`, `aud`), not `repo:org/*` or a wildcard.
- **Permissions:** only what this configuration actually manages. No `*:*`, no `AdministratorAccess`, no unrestricted `iam:*`, `iam:PassRole` or `sts:AssumeRole` paths that would allow privilege escalation.
- **Plan/apply split:** `plan` runs with read-only credentials and the write role can only be assumed from the protected apply job.
- **Guardrails:** a permissions boundary or SCP, a session duration, and access to state (backend bucket and lock table) limited to what's needed.

## Problems I did find on the pipeline path
These would matter for a production apply whatever the role looks like:

1. **`.github/workflows/deploy.yml:7`: `permissions: write-all`** on a `pull_request` trigger. Every PR run gets a token that can write to the repo. If an OIDC role were added here, it would also get `id-token: write`, so any PR could request cloud credentials. Set permissions to the minimum (e.g. `contents: read`) and grant `id-token: write` only to a job gated on a protected environment or branch.
2. **`deploy.yml:14`: script injection.** `${{ github.event.pull_request.title }}` is substituted into a shell `run` line, so a PR title like `"; curl … | sh #` runs arbitrary commands. Combined with point 1, that's a direct route to the token. Pass the title through `env:` and use `"$TITLE"` instead.
3. **`infra/main.tf:8`: SSH (22/tcp) open to `0.0.0.0/0`** on the bastion security group. This isn't about the IAM role, but it's what this apply would put into production. Restrict it to known CIDRs or replace SSH with SSM Session Manager.

I didn't run `fmt`, `validate` or `tflint`, because I made no changes. I also couldn't read the skill's execution-identity reference file because permission was denied, so the checklist above comes from the skill's summary and general practice.

Send me the role definition or tell me where it lives, and I'll finish the review.
