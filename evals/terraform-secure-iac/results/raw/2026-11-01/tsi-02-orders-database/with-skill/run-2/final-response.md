I added the orders database to `main.tf` as `aws_db_instance.orders`, and it passes `terraform fmt` and `terraform validate`. I didn't run `tflint` (not installed) or a plan (no AWS credentials).

**The database**
- It is Postgres 17 on `db.t4g.micro`, with 20 GB of encrypted gp3 storage.
- It uses the existing `orders` subnet group and the `orders_db` security group, and it isn't publicly accessible.
- It has 7-day backups, deletion protection, a final snapshot, automatic minor upgrades, IAM database authentication and `postgresql` logs sent to CloudWatch.

**Password handling (a change to `variables.tf` you should check)**
- The staged `db_password` had a literal default, `orders-dev-2024`. I removed it, since a default would be committed and written to state.
- `db_password` is now `sensitive` and `ephemeral`, with no default. The instance uses the write-only `password_wo`, so the password never reaches state or plan files.
- You must now supply it at run time, for example with `TF_VAR_db_password`. The old default is in git history, so treat it as compromised and don't reuse it.
- I added `db_password_version` (default 1). Increase it to make Terraform send a new password to RDS.

**Outputs for the deploy job**
- The outputs are `db_address`, `db_port`, `db_name` and `db_username`.
- There is no password output. The deploy job has to get the password from the same secret store that supplies `TF_VAR_db_password`.

**Other changes**
- I added a `.gitignore` for state, plan and tfvars files.
- `terraform init` created a `.terraform.lock.hcl`. It only covers this machine's platform, so run `terraform providers lock` for your CI platforms before committing it.

**checkov findings I left open**
- **Multi-AZ, Performance Insights, enhanced monitoring:** these are cost and sizing decisions, and Performance Insights isn't available on the t4g.micro class.
- **Postgres query logging:** this needs a parameter group, which I didn't add.
- **Security group description:** the `orders_db` group has no description. Adding one would force the existing group to be replaced, so I didn't touch it.

I haven't committed anything.
