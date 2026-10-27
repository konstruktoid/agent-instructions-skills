I've added `bootstrap/`, pointed the main configuration at the new bucket, and rewritten the README. I haven't run the migration, and `terraform validate` doesn't work in this sandbox. The AWS provider plugin fails to load here, so only `terraform fmt -check` passed. Run `terraform -chdir=bootstrap init` and `terraform -chdir=bootstrap validate` on a real machine before relying on this.

- **`bootstrap/`:** It creates the bucket `reports-terraform-state-eu-north-1`. Versioning, AES256 encryption, a full public-access block and a policy denying non-TLS access are all on. Old state versions expire after 90 days, and the bucket has `prevent_destroy` set. `bootstrap/` keeps its own local state, since it can't use the bucket it creates.
- **`backend.tf`:** It points at that bucket with key `reports/terraform.tfstate`, `encrypt = true`, and `use_lockfile = true`. The lockfile is S3-native locking, so no DynamoDB table is needed. It works with the `>= 1.10` Terraform version you already require.
- **`README.md`:** It now covers the one-time setup, then the everyday `init`, `plan` and `apply`. The setup steps are:
  1. Run `bootstrap`.
  2. Run `terraform init -migrate-state` on the laptop that holds the current state.
  3. Confirm `plan` shows no changes.
  4. Delete the local `terraform.tfstate*` files.
- **`.gitignore`:** I added one so `.terraform/` and state files stay out of git.

- **Bucket name:** S3 bucket names are global, so the one I picked may already be taken. A backend block can't use variables, so if you change it you must edit both `bootstrap/variables.tf` and `backend.tf`.
- **Secret in state:** The state holds the uploader's secret access key in plaintext. Anyone who can read the bucket can read that key, so limit bucket access accordingly. The README says this.

I didn't commit anything.
