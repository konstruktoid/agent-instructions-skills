I couldn't make the change. Write and Bash are both disabled in this session, so I haven't created or edited any files. I also found no `*.tfstate` file and no `.gitignore` in the workspace. The only Terraform file is `infra/main.tf`, which contains one security group. The committed state may live somewhere I can't see, so check where it is before you migrate.

Here is what I would add.

**`infra/backend.tf`**
```hcl
terraform {
  required_version = ">= 1.10"

  backend "s3" {
    bucket       = "REPLACE-ME-tfstate"   # pre-created: versioning on, public access blocked
    key          = "infra/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    kms_key_id   = "alias/terraform-state" # optional; drop to use the bucket's default SSE
    use_lockfile = true                    # S3-native locking, no DynamoDB table needed
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

I chose S3 because `main.tf` uses `aws_security_group`. If you use a different cloud, the backend would change. `use_lockfile` needs Terraform 1.10 or later. On an older version you would use a DynamoDB table for locking instead.

**Migration steps**
1. Create the S3 bucket outside this root, with versioning, a public access block and a KMS or SSE default. Make sure the KMS key policy allows your role.
2. Run `terraform init -migrate-state` and answer "yes" to copy the local state to S3.
3. Run `terraform plan`. It should show no changes.
4. Run `git rm --cached infra/terraform.tfstate*` to untrack the state files, then commit the new `.gitignore` and `backend.tf`.
5. The old state is still in git history, and it can contain secrets. Rotate anything sensitive in it, and consider rewriting history if the repo is shared.

Separately, `main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. You may want to restrict that.

If you enable Write and Bash, or tell me the bucket name, region and cloud, I'll create the files and run the migration.
