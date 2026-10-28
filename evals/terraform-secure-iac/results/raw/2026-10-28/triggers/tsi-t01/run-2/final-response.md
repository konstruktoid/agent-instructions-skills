I couldn't make this change. This session only gave me tools to read and search files, so I had no way to edit `infra/main.tf` or run `terraform fmt`, `validate` or `tflint`. I also couldn't open the skill's state reference file because permission wasn't granted. Below is the block to add, written as a new file next to `infra/main.tf`. It hasn't been formatted or validated.

### `infra/backend.tf` (new)

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
    # bucket, key, region and kms_key_id come from backend.hcl via
    # `terraform init -backend-config=backend.hcl`, so no account details are committed here.
    encrypt      = true
    use_lockfile = true
  }
}
```

### `infra/backend.hcl.example` (commit this; each person copies it to `backend.hcl`)

```hcl
bucket     = "example-tfstate-bucket"
key        = "infra/terraform.tfstate"
region     = "eu-west-1"
kms_key_id = "alias/example-tfstate"
```

### Why it's set up this way
- **Locking:** `use_lockfile = true` uses S3's own locking, so you don't need a DynamoDB table. It requires Terraform 1.10 or newer, which is why the version is pinned. If you're on an older version, use `dynamodb_table` instead.
- **Encryption:** `encrypt = true` plus a KMS key keeps the state encrypted at rest. State holds secret values in plain text, so treat the bucket as a secrets store.
- **Partial configuration:** the bucket name, region and key aren't in the committed file, so account details stay out of the repo.
- **Provider pinning:** I added `required_providers` because the root didn't declare one. Commit the `.terraform.lock.hcl` that `init` creates.

### The state bucket needs these settings, or the backend gives only partial protection
- Versioning turned on, so you can recover from a bad or corrupted state.
- Block Public Access on, and a bucket policy that refuses non-TLS requests.
- Read and write access only for the people and roles that run `plan` or `apply`, with access to the KMS key limited the same way.

### Moving the state that's been passed around on Slack
1. Get the most recent `terraform.tfstate` and put it in `infra/`.
2. Run `terraform init -backend-config=backend.hcl -migrate-state`.
3. Run `terraform plan` and confirm it shows no changes.
4. Delete every local copy and the copies in Slack. They contain everything that's in state.

Add these lines to `.gitignore`:
```
*.tfstate
*.tfstate.*
.terraform/
*.tfplan
backend.hcl
```

### Separate security problem
`infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, meaning the whole internet. I'd limit it to known address ranges or replace the bastion with SSM Session Manager. I didn't change it, since it's outside this task.

To finish, the files need to be written and `terraform fmt -check`, `terraform init -backend=false && terraform validate`, and `tflint` run. You can do that, or grant me edit and shell access and I'll do it.
