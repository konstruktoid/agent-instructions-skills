I couldn't find a committed state file in this workspace, so I haven't changed anything yet. I need a few answers from you first.

**What the repo has**
- The only Terraform is `infra/main.tf`, which holds one `aws_security_group`. It has no `terraform {}` block, no backend, no provider block and no `.tf` version pins.
- There is no `terraform.tfstate`, no `.terraform/` directory and no `.gitignore` here. The state file you describe isn't in this checkout.
- The repo is a probe sandbox, as its README says. I can still write the backend config, but I can't migrate real state from here.

**Proposed change**

The resources are AWS, so I'd use S3 with a lockfile. I'd add `infra/backend.tf`:

```hcl
terraform {
  required_version = ">= 1.10"

  backend "s3" {
    bucket       = "REPLACE-tfstate-bucket"
    key          = "infra/terraform.tfstate"
    region       = "REPLACE-region"
    encrypt      = true
    kms_key_id   = "alias/REPLACE-tfstate"
    use_lockfile = true
  }
}
```

I'd also add a `.gitignore` covering `*.tfstate*`, `.terraform/` and `*.tfvars`.

**Questions**
1. Is AWS/S3 the right backend? Or do you use Azure, GCS or Terraform Cloud?
2. Does the state bucket exist? If not, I can add a separate bootstrap config with versioning, KMS encryption, public access blocked and a TLS-only policy.
3. What are the bucket name, region and KMS key? Do you want SSE-KMS with your own key or the default SSE-S3?
4. Which Terraform version do you run? `use_lockfile` needs 1.10 or later. On an older version I'd use a DynamoDB lock table instead.

**Steps to run on your machine**
1. Run `terraform init -migrate-state` with the real state file in place.
2. Run `git rm --cached terraform.tfstate*` and commit.
3. Treat the old state as leaked, because it's in git history and state often contains secrets. Rotate any secrets it holds, and consider rewriting history.

Once you answer, I'll write the files.
