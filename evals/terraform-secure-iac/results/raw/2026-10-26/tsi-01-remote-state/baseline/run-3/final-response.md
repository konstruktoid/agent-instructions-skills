I've added the `bootstrap/` configuration, pointed this configuration's backend at S3, and rewritten the README. I haven't run `terraform validate`, `plan` or `apply`. The AWS provider plugin fails to start in this sandbox and there are no AWS credentials. `terraform fmt -check` passes, but nothing has been checked against AWS and the state hasn't been migrated.

**What changed**
- **`bootstrap/`:** creates the bucket `reports-tfstate-<account-id>`. The bucket has versioning, AES256 encryption, a full public-access block, and a policy that denies non-TLS access. Old state versions expire after 90 days. `prevent_destroy` is set so it can't be deleted by accident. The bootstrap's own state stays local, because it can't live in a bucket that doesn't exist yet. The README says to keep that file somewhere safe.
- **`backend.tf`:** uses S3 with `use_lockfile = true` for locking, which works because `versions.tf` already requires Terraform 1.10 or later. No DynamoDB table is needed. The bucket name isn't hardcoded because it depends on the account, so each person supplies it with `terraform init -backend-config=backend.hcl`. `backend.hcl.example` shows the format, and `backend.hcl` is git-ignored.
- **`.gitignore`:** new, covering `.terraform/`, `*.tfstate*` and `backend.hcl`.
- **`README.md`:** covers the one-time bootstrap, the daily init/plan/apply workflow, the bucket permissions teammates need, and force-unlock.

**Migrating the existing state**
- The person with the current `terraform.tfstate` runs `terraform init -backend-config=backend.hcl -migrate-state` after the bootstrap apply, then confirms `terraform plan` shows no changes. The README spells this out.
- The state holds the uploader's secret access key in plaintext. I kept AES256 encryption rather than a KMS key, so anyone with read access to the bucket can see that key. Switching to a KMS key would let you restrict it further, at the cost of extra key permissions for each teammate.

I also left `.terraform.lock.hcl` untracked in the root, created by my `terraform init`. `bootstrap/` has no lock file of its own because its init didn't complete. You'll probably want to commit the root one. Nothing has been committed.
