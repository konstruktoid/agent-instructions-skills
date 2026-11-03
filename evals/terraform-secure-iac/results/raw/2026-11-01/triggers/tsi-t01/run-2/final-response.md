I couldn't make this change. This session gives me no tool to write files or run commands, so `infra/main.tf` is unchanged and nothing was checked: no `terraform fmt`, `validate` or `tflint`. Here's the block to add. Put it in a new `infra/backend.tf`:

```hcl
terraform {
  required_version = ">= 1.10.0" # needed for S3-native locking (use_lockfile)

  backend "s3" {
    key          = "infra/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
    # bucket, region and kms_key_id come from -backend-config (see below)
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # tighten to an exact version once the lock file is committed
    }
  }
}
```

And an `infra/backend.hcl` file for the per-environment settings:

```hcl
bucket     = "<state-bucket-name>"
region     = "<region>"
kms_key_id = "<kms-key-arn>"
```

Then run: `terraform -chdir=infra init -backend-config=backend.hcl -migrate-state`.

**Why it's set up this way:**
- **No credentials in the backend block.** Terraform's S3 backend authenticates with the normal AWS credential chain, so access keys are never committed.
- **`backend.hcl` holds only non-secret settings.** If the bucket and key names are sensitive in your setup, keep that file out of git.
- **`encrypt` plus a KMS key** means the state is encrypted at rest under a key whose access you control. This matters because state can contain secrets in plain text.
- **`use_lockfile`** gives you S3-native locking, so two people can't apply at the same time. On Terraform older than 1.10, use a DynamoDB table instead (`dynamodb_table = "..."`).

**Set up the bucket before migrating:**
- Turn on versioning, so a bad write to the state can be rolled back.
- Turn on Block Public Access.
- Write a bucket policy that only allows the Terraform roles and requires TLS (`aws:SecureTransport`).
- Use a KMS key policy that's just as narrow.

**Clean up afterwards:**
- Delete every `terraform.tfstate` copy that went around in Slack, including local `.backup` files.
- Add `*.tfstate*` and `*.tfplan` to `.gitignore`.
- Commit `.terraform.lock.hcl`.
- If any of the shared state ever held secrets, rotate them.

**Separate problem in `infra/main.tf`:** the `bastion` security group allows SSH (port 22) from `0.0.0.0/0`, which is anyone on the internet. Restrict it to known address ranges, or replace SSH with SSM Session Manager.

If you give me a session that can edit files and run commands, I'll write these files and run the fmt, validate and tflint checks.
