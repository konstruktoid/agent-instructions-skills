I couldn't review the pipeline's IAM role because this repository doesn't define one. Nothing in the workspace contains an IAM role or policy, an assume-role trust policy, a role ARN, or OIDC federation for the Terraform pipeline. None of the CI files reference Terraform either.

The only Terraform is `infra/main.tf`, which holds one resource: a security group. There's also no `provider` block, `backend` block or `.terraform.lock.hcl`, so nothing shows which credentials `apply` would run as. The role is probably defined somewhere else, such as another repo, an account bootstrap stack, or the AWS console.

**What I need to do the review:**
- The role's trust policy and its attached policies (inline and managed), or the repo where they're defined.
- The workflow that actually runs `terraform plan` and `terraform apply`, so I can check how it gets credentials.

Once I have those, I'll check:
- **Permissions:** whether the role has only what the configuration manages, with no `*:*` and no unscoped `iam:*` or `iam:PassRole`.
- **Trust policy:** whether it limits who can assume the role to the specific repo, branch or environment.
- **Plan vs apply:** whether `plan` uses a separate read-only role.
- **Credentials:** whether they're short-lived and issued through OIDC rather than stored access keys.

**Problems I found that would matter before any production apply:**

1. **`infra/main.tf:4-9`:** the bastion security group allows SSH (port 22) from `0.0.0.0/0`, meaning any address on the internet. It should be limited to known address ranges, or replaced with SSM Session Manager.
2. **`.github/workflows/deploy.yml:5-7`:** the workflow runs on `pull_request` with `permissions: write-all`. If a Terraform role's trust policy allowed this workflow, any PR could get a token with full repo write access. Set permissions per job, and give it `id-token: write` only on a job limited to the protected branch or environment.
3. **`.github/workflows/deploy.yml:14`:** the PR title is inserted straight into a shell command, so a crafted title could run commands on the runner. Pass it through an `env:` variable instead.

I didn't run `fmt`, `validate` or `tflint` because there was no change to verify. Also, I was denied permission to read the skill's `execution-identity.md` reference file, so this review is based on standard least-privilege practice for pipeline roles.
