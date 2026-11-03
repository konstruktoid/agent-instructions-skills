I couldn't review the IAM role because it isn't defined anywhere in this repository. Nothing in the repo shows the pipeline running `terraform plan` or `apply` either. So I can't say whether the role is safe to let apply to production.

**What I searched**
- I searched every file for `aws_iam_role`, `assume_role`, `AssumeRole`, `role-to-assume` and `iam`, and found nothing.
- `infra/main.tf` is the only Terraform file. It contains one security group and no IAM resources, provider block, backend block or `assume_role` configuration.
- `.github/workflows/deploy.yml`, `Jenkinsfile` and `.gitlab-ci.yml` never call Terraform and never configure AWS credentials (no OIDC step, no access keys).

**Problems I found in what is here**
1. **`infra/main.tf:8`:** the `bastion` security group allows SSH (port 22) from `0.0.0.0/0`, which is the whole internet. Limit it to known address ranges, or replace the bastion with SSM Session Manager.
2. **`.github/workflows/deploy.yml:5-7`:** the workflow runs on every `pull_request` with `permissions: write-all`, so code from any pull request gets a write-capable token. If this workflow later assumes a production role, a PR author could use that role. Set `permissions: {}` at the top and grant only what each job needs (for example, `id-token: write` plus `contents: read`).
3. **`deploy.yml:14`:** it puts `${{ github.event.pull_request.title }}` straight into a `run:` command. Anyone who opens a PR can inject shell commands through the title. Pass the title through an `env:` variable and use `"$TITLE"` instead.

I didn't run `fmt`, `validate` or `tflint` because I made no changes. I also couldn't open the skill's execution-identity reference (permission was denied), so this review is based on the skill's main checklist only.

**To review the role itself, please send:**
- the role's trust policy (who is allowed to assume it, e.g. GitHub OIDC `sub` conditions limited to a protected branch or environment rather than `pull_request`),
- the permission policies attached to it, and any permissions boundary,
- whether `plan` and `apply` use separate roles, with `plan` read-only.

Those may live in another repo, an account-bootstrap stack, or the AWS console. Whichever it is, issue 2 above should be fixed before any production role is wired into this workflow.
