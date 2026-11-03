The bootstrap configuration and the S3 backend are written, but I haven't run `apply` or the state migration. Both need your AWS credentials and the laptop that holds the current state. `terraform fmt` is clean, and `terraform validate` passes on `bootstrap/`. I didn't validate the root configuration or run `terraform init` against the new backend.

**What I added**
- **`bootstrap/`** creates the state bucket `reports-terraform-state` with:
  - versioning and KMS encryption;
  - a full public-access block, and a bucket policy that denies non-TLS access;
  - `prevent_destroy`, and 90-day expiry of old noncurrent versions.

  It keeps its own state locally, because the bucket doesn't exist yet when it first runs.
- **`backend.tf`** points this configuration at that bucket, with key `reports/terraform.tfstate`. It uses S3's built-in locking (`use_lockfile`, available from Terraform 1.10, which `versions.tf` already requires), so there's no DynamoDB table.
- **`.gitignore`** now excludes `.terraform/`, state files and plan files. There wasn't one before, so a local `terraform.tfstate` could have been committed.
- **`README.md`** now covers the one-time bootstrap, the one-time state migration, and the day-to-day workflow. It also lists the IAM permissions each engineer needs.

**What you need to do, in order**
1. Run `terraform init && terraform apply` in `bootstrap/`.
2. On the laptop with the current state, run `terraform init -migrate-state` from the repo root and answer `yes`. Then run `terraform plan`, which should show no changes.
3. Delete the local `terraform.tfstate*` files, and have nobody else apply until the migration is finished.

**Things to check**
- S3 bucket names are global, so `reports-terraform-state` may already be taken. Backend blocks can't use variables, so if you rename it, change both `bootstrap/variables.tf` and `backend.tf`.
- The state contains the uploader's IAM secret access key in plaintext, because of the `aws_iam_access_key` resource. Limit who can read the bucket to people who should have that key.
