I added the GitHub OIDC provider and two CI roles in `ci_access.tf`, but I couldn't run `terraform validate` or a plan, so nothing has been checked against AWS. `validate` failed because the AWS provider plugin wouldn't start in this sandbox (go-plugin handshake error). `terraform fmt -check` is clean, and Checkov reports 75 passed and 0 failed on `ci_access.tf`. `tflint` isn't installed here, so I didn't run it.

**What's in `ci_access.tf`**
- **OIDC provider:** the GitHub OIDC provider, with audience `sts.amazonaws.com`.
- **Plan role `ingest-ci-plan`:** only pull-request runs of `platform/ingest` can assume it. It has read access to the bucket, queue and table, read access to its own IAM objects, read access to the state object, and put/delete on the `.tflock` lock object.
- **Apply role `ingest-ci-apply`:** only runs on `refs/heads/main` of `platform/ingest` can assume it. It has the same read access, plus write on the state object and named create/update/delete actions on the three resources.
- **Scoping:** both roles are limited to the exact ARNs of the bucket, queue, table and state object. Sessions last one hour at most.
- **No IAM write for CI:** neither role can change IAM. These roles live in this configuration, so a CI apply that could edit IAM could widen its own permissions. Changes to `ci_access.tf` have to be applied by an administrator. A CI plan will show them but can't apply them.
- **Outputs:** `ci_plan_role_arn` and `ci_apply_role_arn`, for the workflow's `role-to-assume`.

**Things to check before relying on it**
- **Apply role bootstrap:** the roles don't exist until an administrator runs the first apply from a laptop.
- **Main-branch trust:** the apply role trusts the `main` branch. If you want a GitHub Environment with approvals instead, change the trust condition to `repo:platform/ingest:environment:<name>`.
- **Permission lists:** the permission lists are from my knowledge of what the AWS provider v6 calls, not from a real plan. If the first plan or apply fails with `AccessDenied`, add the missing action.
- **Reads on the landing bucket:** the plan and apply roles use `s3:Get*` on that bucket only, because the provider reads many bucket sub-configurations on refresh.
- **Lock file:** `terraform init` created `.terraform.lock.hcl`, which I left uncommitted. It only records `linux_amd64`, so run `terraform providers lock` for the platforms CI uses.
- **Existing scan findings:** Checkov flags the existing `main.tf`, for example no encryption, versioning or public-access block on the landing bucket. I didn't touch those.

I haven't committed anything.
