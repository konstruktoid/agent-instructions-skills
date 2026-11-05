State now lives in S3 as far as the code goes, but I haven't run any of it against AWS. Nothing is applied and nothing is migrated yet.

`terraform fmt -check` is clean, and `terraform validate` passes in both the root and `bootstrap/` (run after `init -backend=false`). `tflint` isn't installed here, so it didn't run. Nothing is committed.

## Changes
- **`bootstrap/`**: new configuration with its own local state, since the bucket doesn't exist yet. It creates:
  - The state bucket, with versioning, a rotating KMS key for encryption, and a public-access block.
  - A policy that denies non-TLS access, and a 90-day expiry on old state versions.
  - A `prevent_destroy` guard on the bucket.
  - Outputs for the bucket name and the KMS key ARN.
- **`versions.tf`**: now has a `backend "s3"` block with `encrypt = true` and `use_lockfile = true`. Locking uses S3's native lockfile (Terraform 1.10 or later, which `required_version` already requires), so no DynamoDB table is needed.
- **`.gitignore`**: new, covering state, plan, `.tfvars` and `.terraform/`. I left `.terraform.lock.hcl` unignored so it can be committed, as the skill requires.
- **`README.md`**: now covers the one-time bootstrap, migrating the existing state, the permissions each engineer needs, and the day-to-day workflow.

## Before you use it
- **Bucket name:** the backend bucket `reports-terraform-state` is a placeholder. S3 names are global, so pick a unique name. Pass it to `bootstrap/` as `state_bucket_name` and put the same name in the backend block.
- **Migration:** whoever holds the current `terraform.tfstate` must run `terraform init -migrate-state` once. The README has the steps, including a backup.
- **Sensitive data in state:** this state holds `aws_iam_access_key.uploader`'s secret in cleartext, because `sensitive` only hides it from CLI output. Limit bucket and KMS access to the people who actually run apply. A longer-term fix is to stop Terraform minting a long-lived IAM key, for example by giving the export job a role instead.
- **Lock files:** commit the `.terraform.lock.hcl` files in the root and in `bootstrap/`. I generated them for this machine's platform only, so run `terraform providers lock` for any other platforms your team or CI uses.

## Scan findings
`checkov` on `bootstrap/` passed 30 checks and failed 4. I left all four unfixed and didn't suppress them:
- **KMS key policy:** no explicit policy is set, so the key uses the default one.
- **Cross-region replication, access logging and event notifications:** each needs extra infrastructure (a second bucket, a log bucket, or a notification target). Add them if your policy requires them.
