I couldn't make the change. Write and Bash are both disabled in this session, so I can't create files or run `git` or `terraform`. I also found no state file or `terraform` block in the workspace to migrate, so check where your state is committed.

`infra/main.tf` holds only an `aws_security_group`. There is no `terraform {}` block, no `*.tfstate` file, and no `.gitignore` in this checkout. Since the resource is AWS, I assumed S3.

**1. Add `infra/backend.tf`:**
```hcl
terraform {
  required_version = ">= 1.10"

  backend "s3" {
    key          = "infra/terraform.tfstate"
    encrypt      = true   # server-side encryption with the KMS key
    use_lockfile = true   # S3-native locking, no DynamoDB table needed
  }
}
```
Pass the account-specific values at init time so they stay out of the repo. Replace the three placeholders with your own values:
```
terraform init -migrate-state \
  -backend-config="bucket=<state-bucket>" \
  -backend-config="kms_key_id=<kms-key-arn>" \
  -backend-config="region=<region>"
```

**2. Prepare the bucket first.** It needs versioning, a KMS default encryption rule, public access blocked, and a policy that denies non-TLS requests. Limit access to the state key to the roles that run Terraform. If you're on a Terraform version older than 1.10, drop `use_lockfile` and use `dynamodb_table` instead.

**3. Remove the committed state from git.** State files often contain secrets, and the old ones stay in history.
- Run `git rm --cached terraform.tfstate*`, then add `*.tfstate`, `*.tfstate.*` and `.terraform/` to `.gitignore`.
- Rotate any secret that ever appeared in that state.
- Consider purging it from history.

**Separate finding:** the bastion security group allows SSH from `0.0.0.0/0`. You probably want to restrict that.

If you enable Write, tell me the bucket and KMS key names (or whether you use another cloud). I'll then create the files and update `.gitignore`.
