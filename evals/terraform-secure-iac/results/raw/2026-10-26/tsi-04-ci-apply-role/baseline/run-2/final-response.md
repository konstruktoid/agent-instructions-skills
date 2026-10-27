I added `ci.tf` with the GitHub OIDC provider and two IAM roles, but I couldn't validate it. `terraform fmt` passes. `terraform validate` failed because the AWS provider plugin wouldn't start in this sandbox, so nothing has been planned or applied.

**What's in `ci.tf`**
- **OIDC provider:** `aws_iam_openid_connect_provider.github`, with audience `sts.amazonaws.com`.
- **`ingest-ci-plan`:**
  - **Trust:** only `repo:platform/ingest:pull_request`.
  - **Permissions:** read-only on the bucket, queue and table, plus read access to the state file and the lock object.
- **`ingest-ci-apply`:**
  - **Trust:** only `repo:platform/ingest:ref:refs/heads/main`, so PR workflows can't assume it.
  - **Permissions:** create, update and delete on those three resources, plus state read/write and locking.
- **Scoping:** every permission is limited to the specific resource ARNs and to the state key `ingest/terraform.tfstate` and its `.tflock` object.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`.

I split plan and apply into two roles so that PR runs get no write access to the infrastructure.

**Before you merge**
- **Existing provider:** an AWS account can hold only one OIDC provider for the GitHub URL. If one already exists, import it or switch to a data source.
- **First apply:** it has to be run by an engineer from a laptop, since the roles don't exist yet. After that, the workflow needs `id-token: write` permission and `role-to-assume` set to the right role ARN for each job.
- **Environment-based trust:** if the apply job uses a GitHub `environment:`, the `sub` claim becomes `repo:platform/ingest:environment:<name>`. The apply trust condition would then need changing to match.
- **Missing permissions:** the read and write action lists are hand-written for the current resources. If the first plan hits an `AccessDenied` on some `Describe*` or `Get*` call, add that action. I haven't seen the failure myself.
- **Self-management:** the roles live in this same configuration, and the apply role has no IAM permissions. So changes to `ci.tf` itself will still need a manual apply. I did that deliberately, so a merged PR can't grant itself more access.
