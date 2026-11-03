The configuration now uses an S3 backend and there is a `bootstrap/` config that creates the bucket. I haven't applied anything or tested the backend against real AWS. There's no AWS access here, and the workspace had no `terraform.tfstate` to migrate.

`terraform fmt` is clean. `terraform init -backend=false` and `terraform validate` pass in both the root and `bootstrap/`. I didn't run `tflint` because it isn't installed.

**What I added**
- **`bootstrap/`**: creates the state bucket with versioning, AES256 encryption, a public access block, a deny-non-TLS policy and `prevent_destroy`. Old state versions expire after 90 days by default. `state_bucket_name` has no default because bucket names are global.
- **Backend**: an `s3` block in `versions.tf` with key `reports/terraform.tfstate`, `encrypt = true` and `use_lockfile = true`. S3 native locking needs no DynamoDB table, and the existing `required_version >= 1.10` already supports it.
- **`backend.hcl`**: holds the bucket name, which is a placeholder (`example-org-reports-tfstate`). Someone needs to set the real name after running bootstrap.
- **`.gitignore`**: new, covers state, plan files and `.terraform/`.
- **`.terraform.lock.hcl`**: now exists for both configs and records checksums for linux and darwin on amd64 and arm64.
- **README**: now has the one-time setup (bootstrap, set the bucket, `init -migrate-state`), the everyday workflow, the IAM permissions needed, and how to recover a bad state write.

**Things to know**
- **Secret key in state:** the uploader's IAM secret access key is stored in state in cleartext. Marking it `sensitive` doesn't protect it there. Access to the bucket is access to that key, so keep bucket permissions tight. Longer term, a key that Terraform doesn't generate would keep it out of state.
- **Old local state:** after migrating, delete the local `terraform.tfstate` and its backup, because they still hold that key.
- **Bootstrap state:** `bootstrap/` keeps its own local state. It holds no secrets, but someone has to keep it somewhere durable.
- **Checkov findings:** it flags the state bucket for missing access logging, replication, event notifications and a customer-managed KMS key. I left those out and listed them in the README as not covered. The existing `reports` bucket has similar findings, and I didn't touch it.

I haven't committed anything.
