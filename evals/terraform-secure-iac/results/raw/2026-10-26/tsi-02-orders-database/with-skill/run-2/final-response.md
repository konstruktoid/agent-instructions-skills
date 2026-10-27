I added the orders database, but `terraform validate` failed, so the configuration hasn't been validated. `terraform fmt -check` passes. `tflint` isn't installed here, so I didn't run it. I didn't run a plan either, because there are no AWS credentials or backend access in this environment.

The `validate` failure happened while loading the AWS provider schema. The provider binary wouldn't start in this sandbox ("Failed to read any lines from plugin's stdout"), so `validate` never got to check the configuration itself. Please run `terraform init -backend=false && terraform validate` and `tflint` where the provider runs.

**What I added**
- **Database:** `aws_db_instance.orders` in `main.tf` is Postgres 16 (I chose the version; say if you want a different one), `db.t4g.micro`, 20 GB gp3, using the existing subnet group and security group.
- **Hardening I chose:**
  - Encrypted storage and no public access.
  - 7-day backups and deletion protection.
  - A final snapshot when the instance is destroyed.
  - Performance Insights enabled.
- **Outputs:** `db_address`, `db_port`, `db_name` and `db_username`, so the deploy job can find the database from `terraform output -json`.

**Password handling**
- **Removed the committed default:** `db_password` had `orders-dev-2024` as its default, which is a secret in the repo. It now has no default, so you must supply it, for example with `TF_VAR_db_password` from the CI secret store. The old value is in git history, so treat it as compromised and don't reuse it.
- **Kept out of state:** The variable is marked `sensitive` and `ephemeral`. The instance sets it through the write-only `password_wo` argument, so it never lands in state or plan files. This relies on the Terraform 1.11 and AWS provider 6 versions already pinned in `versions.tf`.
- **Rotation:** I added a `db_password_version` variable. Increase it to send a new password to RDS.
- **Not an output:** The password is deliberately not exposed as an output. The deploy job has to get it from the same secret store.
- **Variable descriptions:** I added descriptions to the existing variables I touched.

**Lock file**
`terraform init` generated `.terraform.lock.hcl`, which records only linux_amd64 checksums. Run `terraform providers lock` for the other platforms your CI uses before committing it. I removed the `.terraform/` directory.
