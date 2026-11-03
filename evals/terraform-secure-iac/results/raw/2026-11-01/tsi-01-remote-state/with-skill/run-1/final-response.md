I added `bootstrap/`, pointed the root backend at S3 and rewrote the README workflow. I haven't applied anything or migrated your state: I had no AWS credentials, and the backend-enabled `init` and `plan` need them. `terraform fmt` and `terraform validate` pass in both directories. Checkov passes with 6 skips, listed below. I didn't run `tflint` because it isn't installed here.

**Before anyone else runs `apply`**
- `backend.hcl` has placeholder values: `example-org-terraform-state` and a dummy KMS key ARN. Replace both with the `state_bucket_name` and `state_kms_key_arn` outputs from the bootstrap apply.
- You have to run the bootstrap apply and then migrate the state with `terraform init -backend-config=backend.hcl -migrate-state` on the laptop that holds `terraform.tfstate`. The README walks through both.

**What changed**
- **`bootstrap/`:**
  - It creates the S3 bucket and a KMS key with rotation.
  - The bucket has versioning, KMS encryption and public access blocked. Old state versions expire after 90 days, and the bucket can't be destroyed by accident.
  - The bucket policy rejects non-TLS requests and denies every principal not in `state_access_principal_arns`. Include the identity that applies the bootstrap in that list, or it locks itself out.
  - `bootstrap/` keeps its own state locally, because it creates the bucket the other state lives in. That is a deliberate one-time exception, and the README says so.
- **Root `versions.tf`:**
  - The `backend "s3"` block uses encryption and S3-native locking (`use_lockfile`), so no DynamoDB table is needed.
  - The bucket and key come from `backend.hcl`, which holds only non-secret names.
  - I raised `required_version` from 1.10 to 1.11, because native locking is only stable from 1.11.
- **Housekeeping:** I added `.gitignore` for state, plan files, `.terraform/` and tfvars. I committed `.terraform.lock.hcl` for both directories, covering four platforms (linux and macOS, amd64 and arm64).
- **Checkov skips:**
  - Three KMS key-policy findings (`"*"` resources are standard in a key policy).
  - Three bucket findings: access logging, cross-region replication and event notifications. Each skip has a one-line justification in the code. Add logging if you have a central log bucket.

**Secret in state:** `aws_iam_access_key.uploader` writes the secret access key into state in cleartext. `sensitive = true` only hides it from CLI output. Anyone with access to the state bucket can read that key, so keep `state_access_principal_arns` short. Longer term, consider replacing the static key with a role the export job assumes. I didn't change that here.

Nothing is committed. All of this is uncommitted in the working tree on `main`.
