I've added `bootstrap/`, pointed this configuration at an S3 backend, and rewritten the README. `terraform validate` failed on both configurations, so none of it has been checked beyond `terraform fmt`.

Validate failed with "Failed to load plugin schemas": the AWS provider binary would not start in this sandbox. That points at the sandbox, not the configuration, but I haven't confirmed it. I did not run `tflint` or a scanner, and no backend-enabled `init` or `plan`, because there are no AWS credentials here. `terraform fmt -check` is clean. Please run `terraform init -backend=false && terraform validate` plus `tflint` before merging.

**What changed**
- **`bootstrap/`:** it creates the state bucket and a KMS key (rotation on). The bucket is encrypted with that key and versioned, and it blocks all public access. A bucket policy denies non-TLS requests. Old state versions expire after 90 days. This configuration keeps its own state locally, because it can't store state in the bucket it creates.
- **`backend.tf`:** it uses the `s3` backend with `encrypt = true`, the KMS key, and `use_lockfile = true`. Locking is S3-native, so there is no DynamoDB table. This relies on the `>= 1.10` version you already require.
- **`.gitignore`:** new, covering state files, plan files, `.terraform/` and tfvars.
- **`.terraform.lock.hcl`:** newly generated at the root. I did not generate one for `bootstrap/`, so run `terraform init` there and commit the lock file.
- **README:** it now covers the bootstrap step, the IAM and KMS permissions the team needs, a one-time `init -migrate-state` of the existing state, and the daily workflow.

**Before you apply**
- **Bucket name:** `reports-tfstate-example` is a placeholder in both `bootstrap/variables.tf` and `backend.tf`. S3 names are global, so pick a real one and keep the two in sync. Backend blocks can't read variables.
- **Secret in state:** the uploader's secret access key sits in cleartext in state, and `sensitive` only hides it from CLI output. Anyone with read access to the bucket and key can read that credential, so restrict access tightly. Consider moving off a long-lived IAM user key, for example to a role the export job assumes. I didn't change that because it would alter how the job gets its key.
- **Migration:** the local `terraform.tfstate` is on one laptop, so that person has to run the migration. They should also delete the local copy afterwards.
