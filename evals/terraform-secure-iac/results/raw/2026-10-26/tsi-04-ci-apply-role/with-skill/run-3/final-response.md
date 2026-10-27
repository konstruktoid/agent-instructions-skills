I added the GitHub OIDC provider and two IAM roles for the workflow, but `terraform validate` could not run, so the new config has only passed `terraform fmt`. `terraform init -backend=false` succeeded. `validate` then failed because the AWS provider binary would not start in this sandbox ("Failed to read any lines from plugin's stdout"). `tflint` isn't installed here, and I didn't run a plan because there are no credentials. Nothing is committed.

**What's in `ci_access.tf`**
- **OIDC provider:** `aws_iam_openid_connect_provider.github`, for `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`.
- **Plan role, `ingest-ci-plan`:** trusted only for `repo:platform/ingest:pull_request`. It has read-only permissions on the bucket, queue and table, plus access to the state object. It can also write the `.tflock` lock object, which `use_lockfile` needs.
- **Apply role, `ingest-ci-apply`:** trusted only for `repo:platform/ingest:ref:refs/heads/main`. It gets the plan permissions plus named write actions on the three resources. Creating queues is limited to `ingest-events-*`.
- **No IAM permissions on the apply role:** it can't change its own access.
- **Sessions:** both roles are limited to one hour.
- **Role ARN outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`, for the workflow's role-to-assume setting.

I split plan and apply into two roles rather than one, so pull-request runs never hold write access. If you want a single role, say so.

**Other changes**
- **`providers.tf`:** the region is now a variable, `aws_region`, with the same default as before (`eu-north-1`). I also added a `data "aws_caller_identity"` lookup so no account ID is hardcoded.
- **`.gitignore`:** added, covering `.terraform/`, state files and plan files.
- **`.terraform.lock.hcl`:** new, from `init`. It has checksums for linux_amd64 only. Run `terraform providers lock` for any other platform your CI or laptops use.

**Before you apply**
- The first apply has to run from an engineer's laptop with admin-capable credentials, since the CI roles don't exist yet.
- An AWS account can hold only one OIDC provider for GitHub's URL. If the account already has one, import it with `terraform import` instead of creating it.
- The managed-resource permission lists were written from what AWS provider v6 reads and writes. If a plan fails with access denied, add only the specific action it names.
- The workflow itself lives in the `platform/ingest` repository. It needs `permissions: id-token: write`, and its apply job should use a protected `main` environment.
