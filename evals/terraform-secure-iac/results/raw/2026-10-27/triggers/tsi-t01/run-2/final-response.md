I couldn't make the edit. This session only gives me read and search tools: no file writes and no shell. So I haven't changed anything and haven't run `fmt`, `validate` or `tflint`. The skill's state reference file was also blocked by a permission prompt, so what follows is based on the skill's checklist rather than that file. Here's the change to apply to `infra/main.tf`:

```hcl
terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Partial configuration: bucket, key, region and kms_key_id are supplied at
  # init time via -backend-config so no account-specific values are committed.
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
```

Add `infra/backend.hcl.example` with placeholder values. Each person or CI job copies it to `backend.hcl`, which stays untracked:

```hcl
bucket     = "example-tfstate-bucket"
key        = "infra/terraform.tfstate"
region     = "eu-west-1"
kms_key_id = "alias/example-tfstate"
```

Add these lines to `.gitignore`:

```
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
backend.hcl
```

**What each piece does:**
- **`encrypt = true` plus `kms_key_id`:** state is encrypted at rest with a customer-managed key, so the key policy decides who can read it.
- **`use_lockfile = true`:** S3's own locking, which needs Terraform 1.10 or later. Two people can't apply at the same moment, which is the main risk once state is shared. No DynamoDB table is needed.
- **Partial config:** the committed block holds no bucket names, account IDs or secrets.

**What the bucket needs.** These are set on the bucket, not in this block:
- Versioning on, so a bad write can be rolled back.
- Block Public Access fully on.
- SSE-KMS as the default encryption.
- A bucket policy that denies requests not using TLS (`aws:SecureTransport`).
- Access granted only to the team and CI roles that run Terraform.

**Moving the existing state:**
1. Run `terraform init -backend-config=backend.hcl -migrate-state` in `infra/`.
2. Confirm the state is in the bucket.
3. Delete every local copy of the `.tfstate` file.

**Two things to deal with now:**
1. **Treat the state already posted in Slack as exposed.** State stores resource attributes in plaintext, including any secrets. Rotate any credentials it contained and delete the Slack copies.
2. **`aws_security_group.bastion` allows SSH from anywhere (`0.0.0.0/0`, port 22).** I left it alone because it's outside this task. It should be limited to known CIDRs, or replaced with SSM Session Manager.

**Still to check:**
- Run `terraform fmt -check`, `terraform init -backend=false && terraform validate`, and `tflint` after applying.
- Commit `.terraform.lock.hcl` once it has been generated.
- The `~> 5.0` provider constraint is my placeholder. Pin it to the exact version your team uses.

If you grant write and shell access, I can apply this and run those checks myself.
