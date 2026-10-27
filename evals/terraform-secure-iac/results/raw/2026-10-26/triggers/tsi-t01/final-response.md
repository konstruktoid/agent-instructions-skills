I couldn't add the backend. Write is disabled in this session, so I haven't created or changed any files. I also couldn't read the skill's `references/state.md`, because read permission for it wasn't granted. What follows comes from my own knowledge of S3 backends, not from that reference.

The root is a single file, `infra/main.tf`. It has no existing backend, no `required_version`, no `.gitignore`, and no `.tflint.hcl`.

**Proposed `infra/backend.tf`**
```hcl
terraform {
  required_version = ">= 1.10"

  # Partial configuration: bucket, key and region come from
  # `terraform init -backend-config=backend.hcl`, so the repo holds no
  # environment-specific names. No credentials here or in that file.
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
```

**Proposed `.gitignore`**
```
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
tfplan
crash.log
backend.hcl
```

**Bucket prerequisites**
- Create the state bucket outside this root, so it doesn't depend on its own state.
- Turn on versioning and default encryption, ideally with KMS.
- Block all public access.
- Limit access to the team's role and require TLS.
- `use_lockfile` handles locking with S3-native lock files, so no DynamoDB table is needed. It requires Terraform 1.10 or later.
- State can hold secrets, so treat read access to the bucket as secret access.

**Migrating existing state:** run `terraform init -backend-config=backend.hcl -migrate-state`. Then delete any state files that have been shared over Slack.

**Existing security issue:** `main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I haven't changed it, but you should restrict it.

I haven't run `fmt`, `validate`, or `tflint`, since nothing was written. If you re-enable writes, or want me to apply this some other way, I'll create the files and run those checks. I'd also need the bucket name and region for `backend.hcl`.
