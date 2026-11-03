I added `bootstrap/`, pointed the backend at S3, and rewrote the README workflow. Nothing has been applied or migrated. `terraform validate` passes on `bootstrap/`. The root configuration hasn't been validated and no AWS calls were made.

**What changed**
- **`bootstrap/`** creates the state bucket and a KMS key with rotation (`alias/reports-tfstate`). The bucket has:
  - versioning;
  - KMS encryption;
  - all public access blocked;
  - a policy that denies non-TLS requests;
  - 90-day expiry of old versions;
  - `prevent_destroy`.

  The default bucket name is `reports-tfstate-<account id>`.
- **`backend.tf`** uses the S3 backend with `use_lockfile = true`. That is S3-native locking, which the existing `>= 1.10.0` requirement supports, so there's no DynamoDB table.
- **`README.md`** now covers the one-time bootstrap, the state migration (`terraform init -migrate-state`), and the daily `init`/`plan`/`apply` workflow.
- **`.gitignore`** is new. It excludes `.terraform/`, tfstate files and tfvars.

**Before it works**
- **Bucket name:** `backend.tf` contains the placeholder `<ACCOUNT_ID>` because backend blocks can't use variables. Replace it with the real account id after bootstrapping. Until then `terraform init` fails on the root configuration.
- **Bootstrap state:** `bootstrap/` keeps its own state locally, because the bucket doesn't exist yet. Whoever runs it should keep that file safe. It holds no secrets.
- **Secret in state:** the state contains the uploader's IAM secret access key in plaintext. That's why I used KMS. Limit access to the bucket and KMS key to people who are allowed to see that key.
- **Migration:** run it from the laptop that holds the current `terraform.tfstate`, and confirm `terraform plan` shows no changes before deleting the local file.
