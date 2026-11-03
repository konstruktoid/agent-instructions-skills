I added the orders database (`aws_db_instance.orders`) in `main.tf`. `terraform fmt -check` and `terraform validate` pass. `tflint` isn't installed here and the repo has no scanner configured, so neither ran. I also didn't run a plan, because there are no AWS credentials in this environment.

- **Instance:** Postgres on `db.t4g.micro` with 20 GB of gp3 storage. It uses the existing `orders` subnet group and `orders-db` security group.
- **Hardening I chose:**
  - Storage is encrypted and the instance is not publicly accessible.
  - Backups are kept for 7 days.
  - Deletion protection is on, and a final snapshot is taken on delete.
- **Outputs for the deploy job:** `db_endpoint` (host:port), `db_address`, `db_port`, `db_name` and `db_username`. The password is not an output.

**Change to the password variable:** `variables.tf` had a hardcoded default password (`orders-dev-2024`) for `db_password`. I removed it and marked the variable `sensitive` and `ephemeral`. The instance passes it to RDS through a write-only argument, so it never lands in state or plan files. I added a `db_password_version` variable; bump it to push a changed password, because Terraform can't detect a change to a value it doesn't store.

- **Rotate the password:** that default is in git history, so treat it as compromised and don't use it on a real database.
- **Supply the password:** `db_password` now has no default. CI must provide it, for example as `TF_VAR_db_password` from the secret store. The deploy job also has to read the password from the secret store, since it isn't in the outputs.
- **Version requirements:** write-only arguments need Terraform 1.11 or later and AWS provider 5.x or later. `versions.tf` already requires 1.11 and provider `~> 6.0`.

I also added a `.gitignore` for state, plan and `.terraform` files, and committed `.terraform.lock.hcl` with checksums for linux_amd64, linux_arm64 and darwin_arm64. Nothing is committed yet.
