I've added the orders database and verified the config. I'm now wrapping up with a final summary.

**Added**
- `main.tf`: `aws_db_instance.orders` is Postgres 16 on `db.t4g.micro` with 20 GB gp3. It uses the existing subnet group and security group.
  - The instance is encrypted and not publicly accessible.
  - Backups are kept for 7 days, deletion protection is on, and a final snapshot is taken on destroy.
  - IAM database authentication is on, and the `postgresql` and `upgrade` logs go to CloudWatch.
- `variables.tf`: I removed the committed default password `orders-dev-2024`. `db_password` is now `sensitive` and `ephemeral` with no default, and it goes to RDS through the write-only `password_wo` argument, so it never reaches state or plan files. I also added `db_password_version` (default 1) for rotation, plus descriptions.
- `outputs.tf`: `db_address`, `db_port`, `db_name` and `db_username`. There is no password output, so the deploy job has to take the password from the CI secret store, for example `TF_VAR_db_password`.
- `.gitignore`: I added it to cover `.terraform/`, state, plans and tfvars. I left `.terraform.lock.hcl` untracked, so commit it.

**Checks**
- `terraform fmt` is clean.
- `terraform validate` passes.
- `tflint` isn't installed here, so I didn't run it.
- `checkov` still fails these checks:
  - Multi-AZ, performance insights and enhanced monitoring: skipped on purpose. They cost extra, and enhanced monitoring needs an IAM role. Say if you want them.
  - Security group description: skipped on purpose, because adding one would force replacement of the existing group.
- I didn't run a plan because there are no AWS credentials here.

**For you to do**
- Treat `orders-dev-2024` as compromised, since it was in git history. Rotate it anywhere it was used.
- The write-only password needs Terraform 1.11 or later and AWS provider 5.x or later. `versions.tf` already requires both.
- I didn't commit anything.
