I added `bootstrap/`, pointed this configuration's backend at S3, and rewrote the README. I haven't applied anything or migrated any state. I only ran `terraform validate` on `bootstrap/`, and it passed. The root backend hasn't been initialised or tested, because that needs AWS credentials and the real bucket.

- **`bootstrap/main.tf`** creates the state bucket. It is private and encrypted, keeps versions (old ones expire after 90 days), allows only TLS, and has `prevent_destroy`. The default name is `reports-tfstate-<account-id>-<region>`. The bootstrap's own state stays local, since it can't live in the bucket it creates.
- **`backend.tf`** is an S3 backend that uses native S3 locking (`use_lockfile`), which your existing `>= 1.10` requirement already supports. No DynamoDB table is needed. The bucket name sits in `backend.hcl` because backend blocks can't take variables.
- **`README.md`** now covers the one-time bootstrap, migrating the existing state, and the day-to-day `init`, `plan` and `apply`.
- **`.gitignore`** now excludes `.terraform/` and `*.tfstate*`.

The state includes the IAM uploader's secret access key in plaintext, so only give bucket access to people who are allowed to read that key. The README says this too.

To switch over:
1. Run `terraform apply` in `bootstrap/`.
2. Put the `state_bucket` output into `backend.hcl`. It currently holds a placeholder.
3. On the laptop that has the current `terraform.tfstate`, run `terraform init -backend-config=backend.hcl -migrate-state`.
4. Run `terraform plan` and check it shows no changes.

I haven't committed anything.
