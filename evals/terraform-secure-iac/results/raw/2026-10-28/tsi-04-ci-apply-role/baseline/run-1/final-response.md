I added `ci.tf` with the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. I couldn't fully validate it. `terraform fmt -check` passes, but `terraform validate` failed because the AWS provider plugin wouldn't start in this sandbox. Nothing was planned or applied.

I split the roles by job:
- **`ingest-ci-plan`** is for the PR `plan` job. Only tokens with subject `repo:platform/ingest:pull_request` can assume it. It can read the bucket, queue and table, and read the state. It can also write the state lock file, because `plan` takes the lock.
- **`ingest-ci-apply`** is for the `apply` job on merges. Only tokens with subject `repo:platform/ingest:ref:refs/heads/main` can assume it. It has the plan permissions plus create, update and delete on those three resources.

Other details:
- **Scoping:** both roles are limited to the three named resources and the state key `ingest/terraform.tfstate` plus its `.tflock` object. They have no IAM permissions, so CI can't change its own access.
- **Audience and outputs:** both trust policies require the `sts.amazonaws.com` audience. The role ARNs are exposed as the outputs `ci_plan_role_arn` and `ci_apply_role_arn`.
- **Gitignore:** I also added a `.gitignore` containing `.terraform/`.

Before you merge:
1. **Bootstrap:** the roles don't exist yet, so someone has to run the first `terraform apply` from a laptop, as today. Then put the output ARNs in the workflow's `role-to-assume`, and give the workflow `permissions: id-token: write`.
2. **Existing provider:** an AWS account can hold only one OIDC provider for `token.actions.githubusercontent.com`. If one already exists, import it with `terraform import aws_iam_openid_connect_provider.github <arn>` rather than creating it.
3. **GitHub environments:** if the apply job uses a GitHub `environment:`, the token subject becomes `repo:platform/ingest:environment:<name>`. The apply trust condition would then need to change to match.
4. **Permission list:** the IAM action list is hand-written. The S3 read actions use wildcards because the v6 provider reads many bucket attributes. Check the first CI `plan` and `apply` for any `AccessDenied` and add what's missing.
5. **Self-managed roles:** the roles are managed by this same configuration, but CI deliberately can't modify them. Changes to `ci.tf` need an admin to apply them.
