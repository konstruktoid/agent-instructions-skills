State now has an S3 backend, and a new `bootstrap/` configuration creates the bucket. I haven't run a real `plan` or `apply`, because there are no AWS credentials here. Nothing is committed.

**What changed**
- **`bootstrap/`** is new and creates the state bucket with:
  - KMS encryption (rotating key)
  - versioning, plus expiry of old versions after 90 days
  - public access fully blocked
  - a bucket policy that requires TLS and denies everyone except `state_access_principal_arns` (a required variable) and the identity running bootstrap
  - no hardcoded account IDs or names; the bucket name and principals are variables
- **Backend**: `versions.tf` now has a `backend "s3"` block with `encrypt = true` and `use_lockfile = true`. That gives S3-native locking, so there's no DynamoDB table (needs Terraform 1.10 or later, which `versions.tf` already requires).
- **Other files**:
  - `.gitignore` is new and covers state, plan files, `.terraform/` and `*.tfvars`.
  - Both `.terraform.lock.hcl` files are generated and cover linux and darwin on amd64 and arm64.
- **README** now describes the one-time bootstrap, migrating the existing state with `terraform init -migrate-state`, and the plan-then-apply workflow.

**Checks**
- `terraform fmt` was clean.
- `init -backend=false` plus `validate` passed in both directories.
- `tflint` and `trivy` aren't installed here, so I didn't run them.
- `checkov` on `bootstrap/` passed 30 checks and failed 4:
  - Cross-region replication, S3 event notifications and access logging are unaddressed. I left them out as extra infrastructure and cost, so say if you want them.
  - The KMS key has no explicit policy, so it uses the AWS default.

**Before you use it**
1. **Bucket name**: the `bucket` value in `versions.tf` is a placeholder (`example-org-reports-tfstate`). Set it to your real bucket name before running `init -migrate-state`.
2. **Bootstrap state**: it stays local, since it can't live in the bucket it creates. It holds no secrets, but someone has to keep it.
3. **Access**: the uploader's IAM secret access key is stored in this state in cleartext. `sensitive` only hides it from CLI output. Anyone with state access can read the key, so keep `state_access_principal_arns` small. The README says the same.
4. **KMS and S3 permissions**: the listed principals also need KMS and S3 permissions of their own. The README lists them.
5. **Environment**: the state key is hardcoded to `reports/staging/...`. Change it if you add other environments.
