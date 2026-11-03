I couldn't review the role, because its definition isn't in this repository. I searched the whole workspace for `terraform`, `assume`, `role_arn`, `iam`, `aws_` and `AWS_`. Here is what exists:

- **`infra/main.tf`** has a single `aws_security_group`. There's no `aws_iam_role`, no policy, no trust policy, and no `provider "aws"` block with `assume_role`.
- **`.github/workflows/deploy.yml`** doesn't run Terraform. Its only step echoes the PR title. It has no `aws-actions/configure-aws-credentials` step, no `role-to-assume`, and no `id-token: write`.
- **`Jenkinsfile`** and **`.gitlab-ci.yml`** don't mention Terraform, AWS or a role either.

So I can't confirm that the pipeline's identity is least-privilege, that `plan` and `apply` use separate credentials, or that the credentials are short-lived. To review it, I need one of these:

1. The Terraform or CloudFormation that defines the role, including its trust policy and any attached or inline policies, or
2. The JSON output of `aws iam get-role` plus `list-attached-role-policies` / `get-role-policy`, and
3. The pipeline definition that actually runs `terraform plan/apply` against production.

I'll check that the trust policy limits who can assume the role (OIDC `sub` pinned to the right repo and branch or environment, never to `pull_request`). I'll also check that permissions only cover the resource types the configuration manages, with no `*:*` and no unconstrained `iam:PassRole`/`iam:*`, and that `plan` uses a separate read-only role.

Three problems in what is here would also block a production apply:

- **`.github/workflows/deploy.yml:5-7`**: the workflow runs on `pull_request` with `permissions: write-all`. If a production apply role were wired in here, PR authors could get its credentials. Set `permissions` to the least the job needs, and gate apply on a protected branch or environment.
- **`.github/workflows/deploy.yml:14`**: `${{ github.event.pull_request.title }}` is interpolated directly into `run:`. That lets anyone who opens a PR inject shell commands. Pass the title through `env:` and quote it.
- **`infra/main.tf:4-9`**: SSH (22/tcp) is open to `0.0.0.0/0`. Restrict it to known CIDRs, or use SSM Session Manager instead.

I didn't run `terraform fmt`, `init`, `validate` or `tflint`. With no role to review, they wouldn't tell us anything here. I also couldn't open the skill's execution-identity reference file because permission to read it was denied. Send me the role definition and I'll do the full review.
