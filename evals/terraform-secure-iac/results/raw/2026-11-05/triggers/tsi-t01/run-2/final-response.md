I couldn't add the S3 backend block. Write is disabled in this session, so I created no files and ran no `terraform` commands. The skill's `state.md` reference was also denied when I tried to read it, so the config below comes from standard S3 backend practice.

Here is the file I'd add as `infra/backend.tf`. `infra/main.tf` currently holds only a security group, and no backend is configured anywhere in the repo.

```hcl
terraform {
  required_version = ">= 1.10"

  # Partial configuration: bucket and region are supplied at init time with
  #   terraform init -backend-config=backend.hcl
  # backend.hcl holds only non-secret metadata (bucket, region, optional kms_key_id).
  # Credentials come from the environment or an assumed role, never from this file.
  backend "s3" {
    key          = "bastion/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }
}
```

- **Encryption and locking:** `encrypt = true` turns on encryption at rest. `use_lockfile = true` gives native S3 locking, so no DynamoDB table is needed. It requires Terraform 1.10 or later, which is why `required_version` is set.
- **No secrets in the repo:** backend blocks can't use variables. I left the bucket and region out and would pass them through an uncommitted `backend.hcl`. No credentials go in the file or the config.
- **Bucket setup:** the S3 bucket needs versioning on, public access blocked, and access limited to the roles that run Terraform. I haven't created or checked the bucket.
- **Migrating existing state:** run `terraform init -backend-config=backend.hcl -migrate-state` from the machine that holds the current state. Then delete any copies of `terraform.tfstate` that were shared over Slack, and add `*.tfstate*` to `.gitignore`.

I also noticed `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. That's unrelated to this change, but you may want to restrict it.

If you re-enable Write, or tell me to give you the file contents another way, I'll add it. Then I'd run `fmt`, `init -backend=false` and `validate`, and `tflint` if the repo configures it.
