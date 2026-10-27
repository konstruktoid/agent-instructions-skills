I added a `bootstrap/` configuration that creates the state bucket, pointed the root backend at S3, and rewrote the README. I couldn't fully validate any of it. `terraform fmt` passed, but `terraform validate` failed because the AWS provider plugin wouldn't run in this sandbox. I haven't run `plan` or `apply` anywhere, and nothing has been committed.

- **`bootstrap/`:**
  - It creates a versioned bucket with KMS encryption, all public access blocked, and a policy that denies non-TLS requests.
  - It expires old object versions after 90 days.
  - `prevent_destroy` is set on the bucket.
  - You pass the bucket name as `state_bucket_name`, since it has to be globally unique.
  - The bootstrap's own state stays local, because it can't live in the bucket it creates. The README says so.
- **`backend.tf`:** the backend is S3 with locking handled by S3 itself (`use_lockfile`, which the existing `>= 1.10.0` requirement already covers), so there's no DynamoDB table. The bucket and region aren't in the file, because a backend block can't use variables. Each person passes them at init with `-backend-config="bucket=..."` and `-backend-config="region=..."`. The bootstrap outputs the exact command.
- **`README.md`:** it covers the one-time bootstrap, migrating the existing state, and the day-to-day workflow. It also lists the IAM permissions people need on the bucket.
- **`.gitignore`:** I added one that excludes `.terraform/`, state files and `*.tfvars`.

- **Migration:** there is no `terraform.tfstate` in this repo, so the engineer who has it on their laptop has to run `terraform init -migrate-state` with the bucket flags. The README gives the steps and says to check that `terraform plan` shows no changes before deleting the local files.
- **Secret key in state:** the uploader's IAM secret access key is stored in the state. Anyone who can read the bucket can read that key, so keep bucket access tight. The README says this too.
