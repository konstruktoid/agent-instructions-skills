State now moves to S3 through a new `bootstrap/` configuration. I couldn't run `terraform validate`: the AWS provider plugin won't start in this sandbox (it fails on load). `terraform fmt` is clean, but I haven't applied or planned any of it.

**`bootstrap/`** creates the state bucket and a KMS key.
- **Bucket:** it is versioned, encrypted with the KMS key, blocks all public access, and expires old versions after 90 days. It has `prevent_destroy` set. The default name is `reports-tfstate-<account id>`, and you can override it with `state_bucket_name`.
- **Access:** the bucket policy denies plain-HTTP requests and denies every principal not listed in `state_access_principal_arns`. I locked it down that tightly because this state holds the uploader's IAM secret key in plaintext.
- **Bootstrap's own state:** it stays local. It holds no secrets.
- **Tfvars example:** `terraform.tfvars.example` shows the format for the principal list.

**Root `backend.tf`** points at the bucket, with the key `reports/terraform.tfstate`, encryption on, and `use_lockfile = true`. S3 native locking needs Terraform 1.10 or later, which `versions.tf` already requires, so there is no DynamoDB table.
- **Bucket name:** it is not hardcoded, so each person passes it at init with `-backend-config="bucket=<name>"`. The name comes from the bootstrap `state_bucket` output.
- **Keeping state out of git:** I added a `.gitignore` for `*.tfstate*`, `.terraform/` and `*.tfvars`. There wasn't one before.
- **Lock file:** a `.terraform.lock.hcl` appeared in the repo root from the init I ran. I left it untracked so you can commit it, which is normal practice.

**README** now covers three things: the one-time bootstrap, the one-time migration, and the everyday init/plan/apply workflow.

**Before you apply:**
1. Put the bootstrap operator's own ARN in `state_access_principal_arns`. Otherwise the bucket policy locks them out.
2. Everyone listed also needs S3 and KMS permissions in their own IAM policy. The README lists them.
3. Migrate on the laptop that holds the current state: run `terraform init -migrate-state -backend-config="bucket=..."`, check that `terraform plan` shows no changes, then delete the local `terraform.tfstate*` files.
