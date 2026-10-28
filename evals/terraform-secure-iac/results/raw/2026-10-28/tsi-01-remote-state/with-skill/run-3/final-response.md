I added `bootstrap/`, pointed the root backend at S3, and rewrote the README for the new workflow. Nothing has been applied, and no plan was run because there are no AWS credentials here. Nothing is committed.

**Checks:** `terraform fmt -check` is clean, and `terraform validate` passes on both the root and `bootstrap/` after `init -backend=false`. I ran validate with `TMPDIR` set to a scratch directory, because the sandbox hit a disk-quota error on the first attempt. `tflint` isn't installed here and the repo has no scanner configured, so neither was run.

**Changes:**
- **`bootstrap/`** creates the state bucket with these protections:
  - versioning on, and noncurrent versions deleted after 90 days
  - AES256 encryption, public access blocked, `BucketOwnerEnforced`, and `prevent_destroy`
  - a bucket policy that denies non-TLS requests and any principal not in `state_access_principal_arns`
- **Root `versions.tf`** now has an `s3` backend block with `encrypt = true` and `use_lockfile = true`. S3-native locking needs no DynamoDB table and works with the existing `>= 1.10` requirement. The bucket name is the placeholder `example-org-reports-tfstate`, and no credentials are in the file.
- **`.gitignore`** excludes state, plan files, `.terraform/` and `*.tfvars`.
- **`.terraform.lock.hcl`** is new and uncommitted (I don't commit unless asked). It records only the platform that generated it, so run `terraform providers lock` for the platforms your team and CI use before committing.
- **README** covers the one-time bucket creation, `terraform init -migrate-state`, daily use, stale-lock handling and rollback.

**Before you rely on it:**
- **Secret key in state.** The uploader's IAM secret access key is in state in cleartext, and `sensitive` doesn't change that. Anyone who can read the bucket can read the key, which is why the bucket policy uses an allow-list. Consider replacing the long-lived IAM user key with a role, or storing the secret in Secrets Manager.
- **Bucket name.** You must replace the placeholder name in `versions.tf` with your real one.
- **Allow-list lockout.** The allow-list must include every principal that runs `plan` or `apply`, and the one applying `bootstrap/`. Otherwise the deny policy locks you out.
- **Bootstrap state.** `bootstrap/` keeps its own state locally. That state holds no secrets, but someone needs to keep it.
- **Encryption key.** I used SSE-S3 rather than a customer-managed KMS key. Say if you want a KMS key instead.
