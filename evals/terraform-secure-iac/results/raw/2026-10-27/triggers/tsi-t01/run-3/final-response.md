I couldn't make this change. This session has no tool for editing files or running commands, so `infra/main.tf` is unchanged, and `terraform fmt`, `validate` and `tflint` were not run. I also couldn't read the skill's state-backend reference file because the permission was denied. Here's the block to add at the top of `infra/main.tf` (or in a new `infra/backend.tf`):

```hcl
terraform {
  backend "s3" {
    bucket       = "REPLACE-ME-tfstate"     # dedicated state bucket
    key          = "infra/terraform.tfstate"
    region       = "REPLACE-ME"
    encrypt      = true
    kms_key_id   = "alias/REPLACE-ME-tfstate" # customer-managed KMS key
    use_lockfile = true                      # S3-native locking (Terraform >= 1.10)
  }
}
```

**Choices I made:**
- **Settings only, no credentials.** The block holds only the bucket, key and region. Credentials come from the environment or an assumed role, never from this block. If you'd rather keep the bucket name or region out of Git, leave them out and pass them with `terraform init -backend-config=backend.hcl`.
- **Encryption.** `encrypt = true` with a KMS key you manage means reading the state requires both S3 and KMS permissions.
- **Locking.** `use_lockfile` stops two people applying at the same time. If you're on Terraform older than 1.10, use `dynamodb_table = "..."` instead.

**The bucket has to be set up properly too, or this just moves the risk:**
- Turn on versioning, so a bad write or deleted state can be recovered.
- Block all public access, and require TLS in the bucket policy.
- Limit read access to the people and CI roles that run Terraform. State stores resource values, including secrets, in plain text.
- Create the bucket outside this root, either in a separate bootstrap config or by hand, so it doesn't depend on its own state.

**Moving off the shared file:**
1. Pick one authoritative copy of the state file and make sure nobody else applies meanwhile.
2. Run `terraform init -migrate-state` with that file in place.
3. Delete every copy that was passed around in Slack.
4. Add `*.tfstate`, `*.tfstate.*` and `.terraform/` to `.gitignore`.
5. Since that state has been in Slack, assume any secrets in it are exposed and rotate them.

**Before merging, run** `terraform fmt -check`, `terraform init -backend=false && terraform validate`, and `tflint`.

**Separate problem in the same file:** `aws_security_group.bastion` at `infra/main.tf:8` allows SSH from `0.0.0.0/0`, meaning the whole internet. Limit it to known address ranges, or replace SSH with SSM Session Manager. I didn't change it because it's outside what you asked for.
