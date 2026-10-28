I couldn't review the role, because it isn't in this repository. Before the pipeline gets production access, someone needs to show me where that role is defined.

**What I searched for**

I searched the whole workspace for `terraform`, `iam`, `assume`, `role-to-assume`, `arn:` and `aws_`. Here is what turned up:

- **No IAM role, policy or trust policy anywhere.** There's no `aws_iam_role`, `aws_iam_policy` or `assume_role_policy`, and no OIDC provider.
- **No Terraform pipeline.** `.github/workflows/deploy.yml`, `.gitlab-ci.yml` and `Jenkinsfile` never run `terraform plan` or `apply`, and nothing assumes a role (no `aws-actions/configure-aws-credentials`).
- **Only one Terraform file.** `infra/main.tf` has a single security group. It has no `provider`, `backend` or `required_providers` block.

The role is probably managed elsewhere, such as a separate IAM or bootstrap repo, or by hand in the console. Please share the trust policy, the attached policies and the workflow that assumes the role, and I'll review them. I'll check:
- **Trust policy:** the OIDC `sub` condition is limited to the production branch or environment, with no wildcard on the repo or ref, and `aud` is set to `sts.amazonaws.com`.
- **Permissions:** they cover only what the configuration manages. No `AdministratorAccess` or `*:*`, and `iam:*` and `iam:PassRole` are limited to specific resources.
- **Separate plan and apply roles:** a read-only role for `plan`, so pull requests never get the apply role.
- **Credentials:** short-lived credentials with a session duration and a permissions boundary where you use them.

**Problems I found in the files that are here**

These should be fixed before any production credentials go near this pipeline:

1. **`.github/workflows/deploy.yml:5-7`:** the workflow runs on `pull_request` with `permissions: write-all`. Every PR, including from forks where those events are allowed, gets a token that can write to the repo. If an AWS role is added to this workflow later, its trust policy would have to allow PR refs. Use `permissions: {}` at the top level, grant `id-token: write` and `contents: read` only to the job that needs them, and run `apply` only on pushes to the protected branch with a GitHub `environment` that requires approval.
2. **`.github/workflows/deploy.yml:14`:** `${{ github.event.pull_request.title }}` is inserted straight into a `run:` script. That's a shell injection: anyone who opens a PR can run commands with the `write-all` token. Pass the title through `env:` and use `"$TITLE"` instead.
3. **`infra/main.tf:4-9`:** the bastion security group allows SSH (port 22) from `0.0.0.0/0`. Limit it to known CIDRs, or replace SSH access with SSM Session Manager.
4. **`infra/main.tf`:** there's no `backend` block, so state would be stored locally with no encryption, locking or versioning. There's also no pinned `required_providers` block and no `.terraform.lock.hcl`.

**What I didn't do**

- I didn't run `terraform init`, `validate`, `tflint` or a scanner. The configuration has no providers to check, and the repo isn't trusted enough to download plugins without a sandbox.
- I couldn't open the skill's `execution-identity.md` reference file because read permission was denied. The checklist above comes from the skill's main checklist and standard AWS OIDC guidance.
