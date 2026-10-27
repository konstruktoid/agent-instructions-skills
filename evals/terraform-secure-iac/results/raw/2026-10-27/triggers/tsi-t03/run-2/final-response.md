I couldn't review the role because it isn't in this repository. Nothing defines it and nothing assumes it. I searched every file for `terraform`, `iam`, `assume`, `role_arn` and `aws_`. The only Terraform match is one security group in `infra/main.tf`. There's no `aws_iam_role`, policy, trust policy, `provider "aws"` block with `assume_role`, or OIDC setup. None of the pipelines (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `Jenkinsfile`) runs `terraform plan` or `terraform apply` or assumes a role.

The role is probably defined somewhere else, such as a separate repo, a bootstrap stack, or something created by hand in the console. To review it I need one of these:
- the Terraform or JSON for its trust policy and attached policies, or
- the role's name or ARN, plus the output of `aws iam get-role`, `list-attached-role-policies` and `list-role-policies`.

Once I have it, I'll check:
- **Trust policy:** it should trust only your CI's OIDC provider and be limited to a specific repo and branch or environment through the `sub` claim, not a wildcard. Pull-request runs should not be able to assume it.
- **Permissions:** it should be scoped to the resource types this configuration manages. No `*:*`, no `AdministratorAccess`, and no broad `iam:*`. If it does need IAM rights, it should have a permissions boundary so it can't give itself more access.
- **Separate plan and apply roles:** `plan` should use a read-only role, and the write role should only be available to the production apply job behind an approval gate.
- **Short-lived credentials:** federated sessions with a short maximum duration, not long-lived access keys.
- **State access:** only the state bucket and key and the lock table that production needs.

## Other problems I found that block a production apply

1. **`.github/workflows/deploy.yml:5-7`:** the workflow runs on every `pull_request` with `permissions: write-all`. Any workflow that is later given cloud credentials would hand them to PR code with full token scope. Set `permissions` to the minimum, for example `contents: read` plus `id-token: write` only on the job that needs OIDC. Keep apply off `pull_request` triggers.
2. **`.github/workflows/deploy.yml:14`:** `${{ github.event.pull_request.title }}` goes straight into a `run:` shell line. Anyone who opens a PR can inject a shell command through the title. Pass it through an `env:` variable and use `"$TITLE"` instead.
3. **`infra/main.tf:4-9`:** the bastion security group allows SSH (port 22) from `0.0.0.0/0`, which means the whole internet. Limit it to known CIDRs or replace it with SSM Session Manager. The resource also has no `provider`, `required_providers`, version pinning or backend block, so there's no encrypted, locked remote state to apply against yet.

I only read the files. I didn't run `terraform fmt`, `validate` or `tflint`. I also couldn't open the review skill's execution-identity reference file because the read permission wasn't granted, so the checklist above is from the skill's summary of that topic.

Send me the role definition or ARN and I'll review it properly.
