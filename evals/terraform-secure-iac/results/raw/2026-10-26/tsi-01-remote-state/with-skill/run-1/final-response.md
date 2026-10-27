I added `bootstrap/`, pointed the root backend at the bucket it creates, and rewrote the README for the new workflow. `terraform validate` did not pass because the AWS provider plugin won't run in this sandbox, so none of it has been planned or applied. Nothing is committed.

**What changed**
- **`bootstrap/`** creates:
  - the state bucket, with versioning, KMS encryption (a key with rotation on), a public access block, a TLS-only policy and `prevent_destroy`;
  - a 90-day expiry for old state versions.
  - Its own state stays local and git-ignored, since it can't use the bucket it creates. It holds no secrets.
- **`backend.tf`** uses the S3 backend with `encrypt = true` and S3 native locking (`use_lockfile`, which needs Terraform 1.10 or later; `versions.tf` already requires that). The bucket name is a literal `reports-terraform-state`, because backend blocks can't read variables. It must match `state_bucket_name` in `bootstrap/`, and S3 bucket names are global, so you may need a different name. If you change it, change it in both places.
- **`.gitignore`** is new and covers state, plan files and tfvars. I also left a `.terraform.lock.hcl` in the repo root.
- **`README.md`** now covers the bucket setup, the one-time `terraform init -migrate-state`, the everyday plan/apply flow and the IAM/KMS permissions each engineer needs.

**Checks**
- `terraform fmt` is clean.
- `terraform validate` failed in both directories with "Failed to load plugin schemas"; the provider binary won't start here.
- `checkov` on `bootstrap/` passed 30 checks and failed 4. All four are optional hardening, and I suppressed none:
  - bucket access logging;
  - event notifications;
  - cross-region replication;
  - an explicit KMS key policy. The default policy applies, which delegates access to IAM.
- I tried to make the lock file cover linux and macOS on amd64 and arm64, but `providers lock` timed out. The lock files only record the platform I ran on. Before committing, run `terraform providers lock -platform=…` in the root and in `bootstrap/` for the platforms your team uses.

**Things to know**
- The root configuration creates an IAM access key, so its secret is in the state file in plaintext. Moving the state to S3 puts that secret in the bucket, so bucket and key access should be limited to people who may run `apply`. The README says this. I didn't change the key itself.
- Run `terraform init -migrate-state` once, from the laptop that has the current `terraform.tfstate`, and then delete the local state files.
- I ran `pkill` against a stray background lock command, and it also killed my shell. My first README write was lost and I redid it. No other files were affected.
