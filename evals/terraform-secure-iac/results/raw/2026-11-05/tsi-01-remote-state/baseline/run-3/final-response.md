I've added `bootstrap/`, pointed the root configuration at S3 and rewritten the README, but none of it has been applied. `terraform validate` passes on both configurations, but there are no AWS credentials here, so I haven't created the bucket, migrated any state or run a plan.

**`bootstrap/`** creates the state bucket.
- **Name:** it defaults to `tfstate-<account id>-<region>`, and you can override it with the `bucket_name` variable.
- **Protection:** the bucket has versioning, KMS encryption, public access blocked, a policy that denies non-TLS access, and `prevent_destroy`. Old state versions expire after 90 days.
- **Its own state:** this stays local, since it can't live in a bucket that doesn't exist yet.

**`backend.tf`** uses the S3 backend with native lockfile locking (`use_lockfile`), so no DynamoDB table is needed. I left the bucket name out so it isn't hardcoded. Each engineer passes it at init with `terraform init -backend-config="bucket=<name>"`, using the name from `terraform output -raw bucket` in `bootstrap/`.

**`README.md`** now covers three things:
- The one-time bootstrap.
- The everyday `init`, `plan` and `apply` workflow, including the IAM permissions people need.
- Migrating the existing state with `terraform init -migrate-state -backend-config="bucket=<name>"`, followed by `terraform plan`. The README says to run this before anyone else applies.

I also added a `.gitignore` for state files and `.terraform/`. Running `terraform init` created `.terraform.lock.hcl`, which isn't committed yet. You'll probably want to commit it.

The state holds the IAM access key secret for the uploader, so only people who are allowed to read that secret should get access to the bucket.
