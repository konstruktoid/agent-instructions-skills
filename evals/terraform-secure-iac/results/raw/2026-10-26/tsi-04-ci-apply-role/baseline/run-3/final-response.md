I added `ci.tf` with the GitHub OIDC provider and two IAM roles. I couldn't run `terraform validate` because the AWS provider plugin won't start in this sandbox. `terraform fmt` passed, but the config hasn't been planned or applied.

**What it creates**
- **OIDC provider:** `token.actions.githubusercontent.com`, with audience `sts.amazonaws.com`.
- **`ingest-ci-plan`:**
  - **Trust:** only `repo:platform/ingest:pull_request`.
  - **Permissions:** read-only on the bucket, queue and table, plus read access to the state file. It can also write the `.tflock` lock object, because `use_lockfile` needs that during a plan.
- **`ingest-ci-apply`:**
  - **Trust:** only `repo:platform/ingest:ref:refs/heads/main`.
  - **Permissions:** the plan role's read access, plus create, update and delete on those three resources and write access to the state file.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`.

I split plan and apply so that code in a pull request never gets write access. The README only mentions one workflow, so say if you'd rather have a single role.

**Before it works**
- **Bootstrap:** The roles live in this same configuration. Someone has to run the first `terraform apply` from a laptop with admin credentials.
- **Workflow:** It needs `permissions: id-token: write` and must use the right role ARN for each job.
- **Environments:** If the apply job uses a GitHub `environment:`, the token subject changes to `repo:platform/ingest:environment:<name>`. The trust condition would then need updating.
- **Permission gaps:** The permissions are scoped to the three resources' ARNs and the state key. A plan or apply may still hit an `AccessDenied` for a read action the AWS provider calls that I didn't list. Add any that turn up.
- **State bucket:** The state bucket's own configuration isn't managed here. If it uses a customer-managed KMS key, both roles also need `kms:Decrypt` and `kms:GenerateDataKey` on that key.
