State now goes to S3, but I haven't run `plan` or `apply`, so nothing was created or migrated. I did run `terraform validate` on both configurations, and both pass.

**What changed**
- **`bootstrap/`** creates the state bucket. It has versioning, AES256 encryption, a full public-access block, and a policy that denies non-TLS access. Old versions expire after 90 days, and `prevent_destroy` is set. The default bucket name is `reports-tfstate-<account id>`. `terraform output init_command` in `bootstrap/` prints the exact init command.
- **`versions.tf`** now has an `s3` backend with key `reports/terraform.tfstate`, `encrypt = true`, and `use_lockfile = true`. S3 native locking needs no DynamoDB table and works because the repo already requires Terraform 1.10 or later.
- **Bucket name:** backend blocks can't use variables, so the bucket and region are passed at init time with `-backend-config`.
- **`.gitignore`** is new and excludes state files and `.terraform/`.
- **`README.md`** now covers the one-time bootstrap, migrating the existing state, the everyday workflow, and the IAM permissions teammates need.
- **Lock files:** I left the generated `.terraform.lock.hcl` files in the root and in `bootstrap/`. Commit them if you want provider versions pinned.

**What you need to do**
1. Run `terraform apply` in `bootstrap/`.
2. On the laptop that holds the current state, run `terraform init -migrate-state -backend-config=...`.
3. Confirm `terraform plan` shows no changes, then delete the local `terraform.tfstate*` files.

**Things to know**
- `bootstrap/` keeps its own state locally, because it can't live in a bucket that doesn't exist yet. Keep that file somewhere safe.
- This configuration's state holds the uploader's IAM secret access key in plain text. Limit bucket access to people who are allowed to read that secret.
