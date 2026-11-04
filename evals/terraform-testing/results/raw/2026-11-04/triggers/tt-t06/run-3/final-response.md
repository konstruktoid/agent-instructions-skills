I couldn't make any changes because the Write tool is disabled in this session, so nothing has been created or edited. Here is what I found and what I'd add.

**What I found**
- The only Terraform file is `infra/main.tf`, a single `aws_security_group`.
- It has no `terraform {}` block and no backend.
- There is no `*.tfstate` file in the working tree, and no CI file runs Terraform. If the committed state is on another branch or only in git history, point me to it.
- The provider is AWS, so I chose S3.

**`infra/backend.tf`**
```hcl
terraform {
  required_version = ">= 1.10"

  backend "s3" {
    bucket       = "REPLACE-ME-tfstate"
    key          = "infra/terraform.tfstate"
    region       = "REPLACE-ME-region"
    encrypt      = true
    kms_key_id   = "alias/REPLACE-ME-tfstate"
    use_lockfile = true   # S3-native locking, no DynamoDB table needed
  }
}
```

**`.gitignore`**
```
.terraform/
*.tfstate
*.tfstate.*
crash.log
```

**Steps to move the state**
1. Create the bucket and KMS key outside this root. The bucket needs versioning, public access blocked, and a TLS-only policy.
2. Give the Terraform runner `s3:ListBucket` on the bucket and `s3:GetObject`, `s3:PutObject` and `s3:DeleteObject` on the state key and its `.tflock`. It also needs `kms:Encrypt`, `kms:Decrypt` and `kms:GenerateDataKey` on the key.
3. Fill in the placeholders in `backend.tf`. The bucket name, region and KMS alias are values I don't have.
4. Run `terraform init -migrate-state` in `infra/`, then check with `terraform state list`.
5. Run `git rm --cached` on the old state file and any `.backup`, then commit.
6. The state stays in git history and may contain secrets, so rotate any it holds.

I didn't write a test because this is backend configuration, not module behavior.

Should I write these files once Write is enabled? Or do you want a different backend, such as GCS, Azure or Terraform Cloud?
