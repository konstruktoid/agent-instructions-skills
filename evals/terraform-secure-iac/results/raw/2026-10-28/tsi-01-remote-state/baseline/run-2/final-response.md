I added the `bootstrap/` configuration, the S3 backend and the README workflow. I couldn't run `terraform validate`, so none of it has been checked against the AWS provider. The provider plugin failed to start in this sandbox ("Failed to read any lines from plugin's stdout"). `terraform fmt -check` passes. Nothing was applied and no state was migrated.

- **`bootstrap/`:** it creates the state bucket, `reports-tfstate-<account-id>-<region>`.
  - The bucket is private, versioned and encrypted with SSE-S3, with `prevent_destroy` set.
  - Its policy denies any request not made over TLS, and old state versions expire after 90 days.
  - Bootstrap keeps its own state locally, because the bucket doesn't exist yet. The README says so.
- **`backend.tf`:** the S3 backend uses `use_lockfile = true`, so no DynamoDB table is needed. The existing `>= 1.10` Terraform requirement already covers that. The state key is `reports/terraform.tfstate`.
- **Bucket name:** the backend block can't use variables, so the bucket name is passed at init with `-backend-config="bucket=<bootstrap output>"`. That keeps the account ID out of the repo.
- **README:** it now covers the one-time bootstrap, the one-time `terraform init -migrate-state` for whoever holds the local `terraform.tfstate`, and the everyday init, plan and apply steps. It also says how to handle a stale lock.
- **`.gitignore`:** this is new. It excludes `.terraform/`, state files and plan files.

The state holds the uploader's secret access key in plaintext, so only people who are allowed to read that key should get access to the bucket. I used SSE-S3 rather than a KMS key to keep this simple. If you want tighter control, say so and I'll switch to a KMS key.
