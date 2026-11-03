I couldn't make the edit. This session only gave me tools to read and search files, with no way to write files or run commands. So nothing in the repo has changed, and I haven't run `fmt`, `validate` or `tflint`. Below is what I'd add, ready to paste.

**`infra/backend.tf`** (new file; `infra/main.tf` currently has only a security group, with no `terraform` block and no pinned provider):

```hcl
terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Partial configuration: bucket, key and region come from
  # -backend-config so no account-specific names are committed.
  backend "s3" {
    encrypt      = true
    use_lockfile = true # S3-native state locking (Terraform >= 1.10), no DynamoDB table needed
  }
}
```

**`infra/backend.hcl.example`** (commit this; each person copies it to `backend.hcl`, which goes in `.gitignore`):

```hcl
bucket = "<state-bucket-name>"
key    = "infra/terraform.tfstate"
region = "<region>"
# kms_key_id = "<kms-key-arn>"  # optional: use a customer-managed key instead of SSE-S3
```

**`.gitignore`** additions:

```
*.tfstate
*.tfstate.*
*.tfplan
.terraform/
infra/backend.hcl
```

Leave `.terraform.lock.hcl` out of `.gitignore`. It should be committed.

**Moving the state everyone currently shares over Slack:**
1. Pick the newest copy and put it in `infra/` as `terraform.tfstate`.
2. Run `terraform init -backend-config=backend.hcl -migrate-state` and answer yes when it offers to copy the state.
3. Run `terraform plan`. It should show no changes.
4. Delete every local copy, and the files posted in Slack. State holds secret values in plaintext, so treat those messages as leaked, and rotate anything sensitive that the state contains.

**The bucket itself** has to exist before step 2. Create it outside this root, or in a small separate bootstrap root. It needs:
- versioning turned on
- public access fully blocked
- default encryption (SSE-KMS if you want key-level access control)
- a bucket policy that rejects non-TLS requests
- IAM that limits read and write on the state key to the people and CI roles that run Terraform

**Not related to the backend:** `aws_security_group.bastion` lets anyone on the internet (`0.0.0.0/0`) reach SSH on port 22. Limit that to known address ranges, or replace it with SSM Session Manager.

After you add the files, run these from `infra/`:
- `terraform fmt -check -diff`
- `terraform init -backend=false && terraform validate`
- `tflint`

If you turn on file editing for this session, I can write the files and run those checks myself.
