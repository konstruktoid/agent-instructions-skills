I added the orders database to `main.tf`, but `terraform validate` did not pass, so the configuration is unvalidated. After `init -backend=false`, validate failed with "Failed to load plugin schemas" for the AWS provider. The provider binary would not start in this environment, so this isn't a finding about the configuration. `terraform fmt -check` is clean. I did not run `tflint` (not installed), `plan`, or `apply`. I also did not re-run `checkov` after adding the log exports, so the run below predates that change.

**The database (`aws_db_instance.orders`)**
- It is Postgres on `db.t4g.micro` with 20 GB of gp3 storage, using the existing subnet group and security group.
- Storage is encrypted and the instance is not publicly accessible.
- It keeps 7 days of backups, has deletion protection on, and takes a final snapshot (`orders-final`) if destroyed.
- It exports the `postgresql` and `upgrade` logs to CloudWatch.

**The password**
- `variables.tf` had a literal default password (`orders-dev-2024`), which would have ended up in the repo and in state. I removed it.
- `db_password` is now `sensitive` and `ephemeral`, and goes to RDS through the write-only `password_wo` argument, so it is never stored in state or plan files. This needs Terraform 1.11 or later, which `versions.tf` already requires.
- `db_password` has no default, so you must supply it, for example with `TF_VAR_db_password` from the CI secret store.
- To rotate it, bump `password_wo_version`.
- The `orders-dev-2024` literal is still in git history, so treat it as compromised and don't reuse it.

**Outputs for the deploy job**
- `db_address`, `db_port`, `db_name` and `db_username` are new outputs.
- The password is deliberately not an output. The deploy job needs to read it from the CI secret store.

**`checkov`**
- It reported 18 passed and 6 failed before I added the log exports.
- The six failures: the security group lacks a description (that resource was already there), and the instance lacks Multi-AZ, enhanced monitoring, Performance Insights and Postgres query logging.
- I left the last four alone because they add cost or need a parameter group. Say if you want them.

The `.terraform.lock.hcl` that `init` created is untracked. You should commit it. Nothing has been committed.
