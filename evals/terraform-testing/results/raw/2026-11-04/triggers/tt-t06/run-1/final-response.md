I haven't changed anything yet. The repo doesn't match what you described, and the cloud and bucket choices are yours.

**What's here**
- The only Terraform is `infra/main.tf`, which holds a single `aws_security_group`.
- It has no `terraform {}` block, no backend, no provider config and no lock file.
- There is no `.tfstate` file anywhere in the working tree, and nothing in CI references Terraform.
- There's no `.gitignore` either.

So the committed state file isn't in this checkout. It may live on another branch or in git history, or in a different repo. If it's in history, it needs more than a move. State often contains secrets in plaintext, so I'd treat anything in it as exposed and rotate it.

**Proposed change (AWS, since the resource is `aws_*`)**
Add `infra/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket       = "<state-bucket>"
    key          = "infra/terraform.tfstate"
    region       = "<region>"
    encrypt      = true
    kms_key_id   = "<kms-key-arn>"  # optional; omit to use SSE-S3
    use_lockfile = true             # S3-native locking, Terraform >= 1.10
  }
}
```

I'd also add a `.gitignore` covering `*.tfstate*` and `.terraform/`. The migration would be `terraform init -migrate-state`, then `git rm --cached` on the old state file.

**What I need from you**
1. Is AWS/S3 the right backend? I can write the equivalent for GCS, Azure Blob or Terraform Cloud instead.
2. Do you have an existing state bucket and KMS key? If not, I can write a small bootstrap config for them. It would turn on versioning, block public access, enforce TLS and use a KMS key.
3. Do you use Terraform 1.10 or later? If not, I'll use a DynamoDB lock table instead of `use_lockfile`.
4. Where is the committed state file? Which branch or path?

I won't run `init -migrate-state` against real infrastructure without your go-ahead.

Separately, `main.tf` opens SSH on the bastion to `0.0.0.0/0`. I left it alone since it's outside this request, but you'll probably want to restrict it.
