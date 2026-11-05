I added `bootstrap/`, pointed the root backend at S3, and rewrote the README. Both configurations pass `terraform validate`. I didn't run `plan` or `apply` against AWS, so the bucket and the state migration are untested.

- **`bootstrap/`**: creates the state bucket, named `reports-tfstate-<account id>-<region>` unless you set `bucket_name`. The bucket has versioning, AES256 encryption, a full public-access block, and a policy that denies non-TLS requests. Old state versions expire after 90 days. `prevent_destroy` is set on the bucket. Its own state stays local, since it can't live in a bucket that doesn't exist yet. `terraform output init_command` prints the exact `init` command to use.
- **Root `versions.tf`**: now has an `s3` backend with `use_lockfile = true` and `encrypt = true`, which needs Terraform 1.10 or later, as the config already requires. This means no DynamoDB table. The bucket and region are not in the file. Each engineer passes them with `-backend-config` at `init`, because the bucket name depends on the AWS account.
- **`README.md`**: describes the one-time bootstrap, a one-time `terraform init -migrate-state` for whoever has the current `terraform.tfstate`, and the day-to-day `init`, `plan` and `apply`. It also lists the S3 permissions each engineer needs.
- **`.gitignore`**: new, so state files and `.terraform/` stay out of git.

- **Secret in state:** the state holds the uploader's IAM secret access key in plaintext. Anyone who can read the bucket can read that key, so restrict bucket access to people who should have it.
- **Migration:** someone has to run `-migrate-state` from the laptop that has `terraform.tfstate`. If you skip it, the first `apply` from S3 would try to recreate the resources.
- **Lock file:** `terraform init` created `.terraform.lock.hcl` at the root. It's untracked, and you'll probably want to commit it. I haven't committed anything.
