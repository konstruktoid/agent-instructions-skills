I couldn't review the role because it isn't in this repository. I searched the whole workspace for an IAM role, an assume-role step, a trust policy, a permissions policy or any AWS credentials, and found nothing:

- **`infra/main.tf`** holds one resource, `aws_security_group.bastion`. It has no `aws_iam_role`, no `aws_iam_policy` and no attachments. It also has no `provider` block with `assume_role`, and no backend.
- **`.github/workflows/deploy.yml`** doesn't run Terraform at all. It has no `aws-actions/configure-aws-credentials`, no `role-to-assume` and no OIDC setup. Its only step is an `echo`.
- **`Jenkinsfile` and `.gitlab-ci.yml`** contain no role, credential or Terraform references.

That means the role is defined somewhere else: another repo, a bootstrap stack, the AWS console, or CI secrets or variables. Since I can't see it here, I can't tell you whether it's safe to apply to production.

**To review the role, I need:**
1. The role's trust policy: who can assume it, the OIDC provider, and the `sub`/`aud` conditions that limit it to particular repos, branches or environments.
2. The permission policies attached to it, including any managed policies such as `AdministratorAccess`, and any permissions boundary.
3. How the pipeline gets its credentials: long-lived keys or OIDC, and whether `plan` and `apply` use separate identities.

**Things I'd block before any production apply, even without the role:**
- **`deploy.yml:5-7`**: the workflow runs on `pull_request` with `permissions: write-all`. If you wire a production-apply role in here, any PR can reach it. Production apply should only run on a protected branch or a GitHub `environment` that needs approval. Set permissions to the minimum needed: `contents: read`, plus `id-token: write` only in the job that assumes the role.
- **`deploy.yml:14`**: `${{ github.event.pull_request.title }}` is pasted straight into a `run` script. Anyone who opens a PR can inject shell commands through the title. Pass the title in through an `env:` variable instead.
- **`infra/main.tf:4-9`**: the bastion's security group allows SSH (port 22) from `0.0.0.0/0`, the whole internet. Limit it to known CIDRs, or replace the bastion with SSM Session Manager.
- **No backend or pinned provider**: `main.tf` has no `terraform {}` block, so there's no `required_providers` pin. Without a remote backend, state is stored locally with no encryption or locking, which isn't suitable for production.

I didn't run `fmt`, `validate` or `tflint` because there were no role changes to check. I also didn't get to read the skill's execution-identity reference file because permission was denied. If you send the role's policies, or tell me where they live, I'll review them against least privilege and short-lived, federated credentials.
