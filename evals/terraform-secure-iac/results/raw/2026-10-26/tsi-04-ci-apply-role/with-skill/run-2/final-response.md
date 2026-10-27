I added the GitHub OIDC provider and two IAM roles for the `platform/ingest` workflow. `terraform validate` didn't run, so none of it has been checked against the AWS provider. After a successful `terraform init -backend=false`, `validate` failed because the AWS provider plugin crashed on startup with "Failed to read any lines from plugin's stdout". That looks like a sandbox limit, not a config error. Nothing was committed.

**What's in `ci.tf`**
- **OIDC provider:** it points at `token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`.
- **Plan role** (`ingest-ci-plan`):
  - It can only be assumed from pull-request runs of the repo.
  - It has read-only access to the bucket, queue and table, plus read access to the state object.
  - It can also write the state lock object, because `use_lockfile` writes it during `plan`.
- **Apply role** (`ingest-ci-apply`):
  - It can only be assumed from runs on `refs/heads/main`.
  - It adds create, update and delete on the three resources and write access to the state object.
  - It has no IAM permissions, so it can't change its own role or policies.
- **Permissions:**
  - Every action is named and scoped to a specific ARN. The three resource ARNs come from the resources in `main.tf`.
  - The state ARNs are built from the bucket and key in `versions.tf`.
  - Sessions last at most one hour.
- **Variables and outputs:** `variables.tf` has `github_repository` (default `platform/ingest`, validated to reject wildcards) and `github_apply_branch` (default `main`). `outputs.tf` exposes both role ARNs for the workflow to use.
- **Housekeeping:** I added a `.gitignore` and committed `.terraform.lock.hcl`. The lock file only has checksums for `linux_amd64`, so run `terraform providers lock` for any other platform you use.

**Checks**
- `terraform fmt -check` passes.
- `checkov` reports nothing on the new files. It does report findings on the existing `main.tf`, such as no S3 versioning, no public access block and no KMS on the queue and table. I didn't touch those.
- `tflint` isn't installed here, so it didn't run.
- I didn't run a plan, because no AWS credentials are available.

**Before you merge**
- **Bootstrap apply:** the roles live in this same config, so someone with admin credentials has to apply this change once. After that, CI can't modify the roles.
- **S3 permissions:** the S3 and DynamoDB action lists come from what the AWS provider usually calls on refresh. A first `plan` may fail on a missing read action, and you'd add it then.
- **Branch protection:** the `main` check only holds if `main` is protected, because anyone who can push there can apply. A GitHub Environment on the apply job would let you require approval. If you use one, change the apply trust condition to match `repo:…:environment:<name>`.
- **Workflow side:** the workflow needs `permissions: id-token: write` and should pin its actions by SHA.
