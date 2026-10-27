The S3 backend, the `bootstrap/` configuration and the README are written. I couldn't run `terraform validate`, so none of it has been checked beyond formatting and a scan. Nothing is committed.

**What was checked**
- **Formatting:** `terraform fmt -check` is clean.
- **`terraform validate`:** it failed in both directories. The AWS provider plugin wouldn't start in this sandbox ("Failed to read any lines from plugin's stdout"), so the failure came from the environment, not from a config error.
- **`tflint`:** it isn't installed, so it didn't run.
- **checkov:** on the new state bucket it reports only access logging, cross-region replication and event notifications. I left those out as over-scope for a state bucket. It also reports findings on the existing `main.tf`, which I didn't touch.
- **Not exercised:** `bootstrap/` was never planned or applied, and I had no AWS credentials, so the backend wasn't initialised against a real bucket.

**What changed**
- **`bootstrap/`:** it creates the S3 state bucket and a KMS key. The bucket has versioning, KMS encryption, a public-access block, a TLS-only rule and `prevent_destroy`. Its bucket policy denies state-object access to anyone not in `state_access_principal_arns`, and only those principals can use the key. I used a customer-managed key because the state holds the uploader's secret access key in cleartext. The bootstrap keeps its own local state, since it can't store state in a bucket it hasn't created yet.
- **`backend.tf`:** the S3 backend, with the `reports/terraform.tfstate` key, encryption and `use_lockfile`. Locking is an S3 lock file, so there's no DynamoDB table. `bucket` and `kms_key_id` come from a git-ignored `backend.hcl`, with `backend.hcl.example` as the template.
- **`.gitignore`:** new. It excludes state, plan files, `.terraform/`, `*.tfvars` and `backend.hcl`.
- **Lock files:** both `.terraform.lock.hcl` files are generated with checksums for linux_amd64, darwin_arm64 and darwin_amd64. Both are untracked and need adding to the commit.
- **`README.md`:** it now covers the one-time bootstrap, the backend setup, the one-time `terraform init -backend-config=backend.hcl -migrate-state` for the existing local state, and the daily plan/apply routine.

**Still to do**
1. Someone runs the bootstrap with real credentials.
2. The person with the laptop `terraform.tfstate` runs the migration.
3. That person then securely deletes the local state files.

Please run `terraform validate` and `tflint` somewhere the provider plugin starts.
