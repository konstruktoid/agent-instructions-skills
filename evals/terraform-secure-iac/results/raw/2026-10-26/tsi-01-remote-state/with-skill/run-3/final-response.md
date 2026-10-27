I added the `bootstrap/` configuration, pointed the root backend at S3, and rewrote the README. I couldn't validate it or run a plan, and the backend still has placeholder values, so the first-time setup has to happen before anyone can use it.

**What I changed**
- **`bootstrap/`**:
  - The bucket is versioned and encrypted with a KMS key that has rotation on.
  - It blocks all public access and refuses non-TLS requests.
  - It expires old state versions after 90 days (configurable) and has `prevent_destroy`.
  - `state_bucket_name` has no default, so you choose a globally unique name.
- **`backend.tf`**: points at the bucket with `encrypt = true`, a KMS key and `use_lockfile = true`. Locking uses an S3 lock object, so there's no DynamoDB table. It needs Terraform 1.10 or later, which `versions.tf` already requires.
- **Placeholders**: `bucket` and `kms_key_id` are `REPLACE-WITH-...`. Fill them in from `terraform output` after bootstrapping.
- **`.gitignore`**: new file covering state, plan files and `.terraform/`.
- **`README.md`**: now covers the one-time setup (bootstrap, fill in `backend.tf`, `terraform init -migrate-state`), then the daily plan and apply workflow.

**Checks**
- `terraform fmt -check` is clean.
- `terraform validate` failed in both directories. The AWS provider binary installed by `init` won't start in this sandbox (plugin handshake failure), so the failure comes from the environment, not from a config error I could see.
- `tflint` isn't installed, so I didn't run it.
- I didn't try a backend-enabled `init` or a plan, since there are no AWS credentials here.
- The lock files (`.terraform.lock.hcl`, in the root and in `bootstrap/`) only record the platform I ran on. The multi-platform `terraform providers lock` command failed here, probably because there's no network. Someone should run it for the team's platforms and commit the result.

**Things to know**
- **The state is sensitive.** It contains the IAM access key's secret in cleartext, because `sensitive` only hides it from CLI output. Restrict bucket read access and `kms:Decrypt` to the people and CI identity that may run `apply`. The README says this too. I didn't change the access-key resource, but moving that credential out of Terraform would be worth considering.
- **Bootstrap state is local.** `bootstrap/` keeps its own state in `bootstrap/terraform.tfstate`. That state holds no secrets, and the README explains how to move it into the bucket afterwards.
- **Migration runs on the laptop.** The existing `terraform.tfstate` is on that engineer's laptop, so `terraform init -migrate-state` has to run there. Confirm bucket versioning is on first.
