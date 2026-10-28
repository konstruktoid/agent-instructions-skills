I couldn't make the change. This session only gives me read and search tools, with no way to write files or run commands. I also couldn't read the skill's `state.md` reference because that read needs a permission you haven't granted yet. So here is the block to add yourself, and nothing has been run through `fmt`, `validate` or `tflint`.

### Add to `infra/main.tf` (or a new `infra/backend.tf`)

```hcl
terraform {
  required_version = ">= 1.10.0"

  backend "s3" {
    key          = "infra/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

### `infra/backend.hcl` (supplied at init time)

```hcl
bucket     = "<state-bucket-name>"
region     = "<region>"
kms_key_id = "<kms-key-arn>"
```

Then run `terraform init -backend-config=backend.hcl -migrate-state`. Whoever has the current state file runs this once to upload it, and the team then deletes every copy shared over Slack.

### Why it's set up this way

- **Bucket details are kept in a separate file.** The bucket name, region and key ARN go in `backend.hcl`, which holds only non-secret settings. This keeps account details out of the main config. Credentials don't belong in either file; they come from the environment or an SSO profile.
- **`use_lockfile = true`** uses S3's built-in locking, so you don't need a DynamoDB table. It needs Terraform 1.10 or later, which is why `required_version` is set.
- **`encrypt` plus `kms_key_id`** encrypts the state at rest with a key you control. This matters because state stores secret values in plain text, even ones marked `sensitive`.
- **The bucket itself needs to be set up correctly.** None of these settings can be enforced from the backend block:
  - versioning enabled, so a corrupted or overwritten state can be recovered
  - Block Public Access on
  - TLS required for all access
  - read and write access limited to the people and pipelines that run Terraform

  Create the bucket in a separate bootstrap config, not in this root.
- **Ignore local state files** by adding these to `.gitignore`: `*.tfstate`, `*.tfstate.*`, `.terraform/` and `*.tfplan`. Commit `.terraform.lock.hcl`.

### Already in the repo, unrelated to this change
`infra/main.tf:8` opens SSH (port 22) on the bastion to `0.0.0.0/0`, which means anyone on the internet. You should probably narrow that to known address ranges or use SSM Session Manager instead.

To finish: allow file writes and I'll make the edit, then run `terraform fmt -check`, `init -backend=false`, `validate` and `tflint`.
