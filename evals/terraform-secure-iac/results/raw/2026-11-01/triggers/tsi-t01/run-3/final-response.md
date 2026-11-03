I couldn't make the change myself. This session only lets me read and search files, so I have no tool to write `infra/main.tf`. I also couldn't run `terraform fmt`, `init -backend=false`, `validate` or `tflint`, and I couldn't open the skill's state reference file because permission to read it wasn't granted. Here is the block to add instead.

`infra/main.tf` currently holds only a security group. It has no `terraform` block, no `provider` block and no version pins. Put this at the top of the file, or in a new `infra/backend.tf`:

```hcl
terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket       = "REPLACE-with-state-bucket"
    key          = "infra/terraform.tfstate"
    region       = "REPLACE-with-region"
    encrypt      = true
    use_lockfile = true
    # kms_key_id = "alias/terraform-state"   # optional: use a customer-managed key instead of the default
  }
}
```

**Why it's set up this way:**
- **`use_lockfile = true`** turns on S3's built-in state locking, which needs Terraform 1.10 or later. This lock is what stops two people writing the state at the same time, which can happen when state is passed around by hand. If your team is on an older version, remove that line and use `dynamodb_table = "..."` instead.
- **`encrypt = true`** encrypts the state at rest. State holds secrets and resource attributes in plain text, so the bucket needs the same protection as a secret store.
- **No credentials or account IDs go in the block.** The `REPLACE-` placeholders are only bucket metadata. You can also leave `bucket` and `region` out and pass them at init with `-backend-config=backend.hcl`. Authentication should come from the environment, such as SSO or an assumed role, not from the file.

**What the bucket needs (outside this root):**
- Versioning on, so you can roll back corrupted state.
- Block Public Access on, and server-side encryption by default.
- A bucket policy that denies non-TLS requests and allows only the team's Terraform role(s) to read and write the state key.
- Ideally, created in a separate bootstrap root rather than this one.

**Moving the existing state:**
1. Get the newest copy of the state from Slack, put it at `infra/terraform.tfstate`, and run `terraform init -migrate-state`.
2. Check that `terraform plan` shows no changes.
3. Delete the local copy and the Slack copies. They contain everything in your infrastructure state, so it's worth rotating any secrets that were in them.
4. Add `*.tfstate*`, `.terraform/` and `*.tfplan` to `.gitignore`, and commit `.terraform.lock.hcl`.

**Unrelated finding:** `aws_security_group.bastion` allows SSH from `0.0.0.0/0`, which means anyone on the internet can try to log in. It's worth limiting that to known IP ranges or replacing SSH with SSM Session Manager. I can do that as a separate change if you like.

If you give me write and shell access, I'll add the block and run fmt, validate and tflint on it.
