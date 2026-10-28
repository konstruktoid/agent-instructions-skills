The `bootstrap/` configuration, the S3 backend block and the README update are written. `terraform validate` fails here, so none of it has been checked beyond formatting. I didn't run `tflint`, and `terraform plan` and `apply` weren't attempted because there are no AWS credentials here.

**What changed**
- **`bootstrap/`** creates the state bucket and a KMS key. The bucket has versioning, KMS encryption, a public access block, owner-enforced ownership and a policy that denies non-TLS access. Superseded versions are kept for 90 days. The bucket name is a required variable, and `terraform.tfvars.example` uses a placeholder.
- **`versions.tf`** now has a `backend "s3"` block with `encrypt = true` and `use_lockfile = true`. S3 native locking needs Terraform 1.10 or later, which the config already requires, so there is no DynamoDB table.
- **`.gitignore`** is new and excludes state files, `.terraform/`, plan files and real `.tfvars`.
- **Lock files:** `.terraform.lock.hcl` is added to the root and to `bootstrap/`, with checksums for linux and darwin on amd64 and arm64.
- **`README.md`** covers the one-time setup (bootstrap, set the bucket name, grant access, run `terraform init -migrate-state`, delete the local state). It also covers the daily workflow, unlocking, and recovering an old state version.

**Checks**
- `terraform fmt -recursive -check` passes.
- `terraform init -backend=false` succeeded in both directories. `terraform validate` failed in both, because the AWS provider binary can't start in this sandbox. It reported an architecture or handshake error, not a problem in the configuration.

**Before you apply**
- **Bucket name:** `example-org-terraform-state` in `versions.tf` is a placeholder. Set the real name before running `terraform init`, because backend blocks can't use variables.
- **Bootstrap state:** this stays local, since the bucket doesn't exist yet. It holds no secrets.
- **Access:** I didn't add a bucket policy limiting who can read state, so access is controlled through IAM and KMS grants. The README lists the permissions to give each person or role.
- **Secret in state:** state for this configuration holds the uploader's secret access key in cleartext, because of `aws_iam_access_key`. `sensitive` only hides it from CLI output. The KMS key and the access list are what protect it. I left that resource alone. The longer-term fix is to stop storing the key in state, for example with a role or a secret manager.
