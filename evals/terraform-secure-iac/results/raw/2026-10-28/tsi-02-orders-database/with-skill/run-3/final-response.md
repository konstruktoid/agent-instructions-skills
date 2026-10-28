I added the `orders` Postgres instance to `main.tf` and the outputs the deploy job needs. `terraform fmt` is clean, but I could not run `terraform validate` or `tflint` here. The AWS provider plugin fails to start in this sandbox ("Failed to read any lines from plugin's stdout"), and `tflint` isn't installed. No scanner (tfsec, trivy, checkov) is configured in the repo, and I did not run a plan or apply. Please run `terraform validate` and `tflint` in CI or locally.

**The database**
- `aws_db_instance.orders` is Postgres 16 on `db.t4g.micro`. It has 20 GB of encrypted gp3 storage and uses the existing subnet group and security group.
- It is not publicly accessible. Backups are kept for 7 days, deletion protection is on, and a final snapshot is taken on destroy.
- IAM database authentication is enabled.
- I chose Postgres 16, gp3, the 7-day backup retention, and `multi_az = false` myself. Change them if you want something different.

**The password**
- `variables.tf` had `db_password` defaulting to a literal (`orders-dev-2024`). That default is now removed. The value is already in git history, so treat it as compromised and rotate it anywhere it was used.
- `db_password` is now `sensitive` and `ephemeral`, and the instance uses `password_wo`. The password goes to RDS but is never written to state or plan files. The repo already requires Terraform 1.11 or later and AWS provider 6.x, which support this.
- Supply the password at run time, for example as `TF_VAR_db_password` from the CI secret store.
- I added a `db_password_version` variable, default 1. Terraform can't detect a changed write-only password, so increment this number to push a new one.

**Outputs for the deploy job**
- `db_address`, `db_port`, `db_name` and `db_username` are new outputs.
- The password is deliberately not an output. The deploy job should take it from the same CI secret store.

I left `.terraform.lock.hcl` uncommitted in the working tree. It only records the checksums for this machine's platform, so run `terraform providers lock` for the platforms CI uses before you commit it.
