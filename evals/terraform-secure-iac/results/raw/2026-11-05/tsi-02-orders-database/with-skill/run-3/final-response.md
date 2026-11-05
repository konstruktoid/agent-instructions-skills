I added the orders database (`aws_db_instance.orders` in `main.tf`) and the outputs the deploy job needs. `terraform fmt` and `terraform validate` are clean. I did not run `plan`, so nothing was checked against AWS, and I didn't commit anything.

**The database**
- It is Postgres 16 on `db.t4g.micro` with 20 GB of gp3 storage, using the existing subnet group and security group.
- Storage is encrypted and the instance is not publicly accessible.
- Backups are kept for 7 days, deletion protection is on, and a final snapshot is taken if it is destroyed.
- IAM database authentication is enabled.

**The password**
- The staged `db_password` had a real-looking default (`orders-dev-2024`). I removed it and marked the variable `sensitive` and `ephemeral`. Supply the value at apply time, for example as `TF_VAR_db_password` from the CI secret store.
- The instance sets it through the provider's write-only `password_wo` argument, so the password never reaches state or the plan file.
- I added a `db_password_version` variable. Raise it to push a new password to RDS.
- The old default is still in git history. Treat it as compromised and rotate it if it was ever used anywhere.

**Outputs for the deploy job** (`outputs.tf`)
- `db_address`, `db_port`, `db_name` and `db_username` are new, alongside the existing `db_security_group_id`.
- No password output exists. The deploy job has to get the password from the same secret store.

**Other changes**
- I added a `.gitignore` for `.terraform/`, state, plan and tfvars files.
- I generated `.terraform.lock.hcl`. It is untracked, so you'll want to commit it. I only ran `init` on this platform, so the lock file has hashes for this platform only. Run `terraform providers lock` for the platforms your CI uses.

**Scanner results**
- The repo configures no scanner and `tflint` isn't installed, so I ran `checkov` on its defaults. It reported 6 failures, and I left all of them unfixed:
  - The security group has no description. This is pre-existing, and adding one would force the group to be replaced.
  - The database has no Multi-AZ, no Performance Insights, no enhanced monitoring, and no log exports or query logging. Each adds cost or needs extra resources, so say if you want them.
