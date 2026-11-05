I added the orders Postgres database to `main.tf` and the connection outputs to `outputs.tf`. `terraform validate` passes. I didn't run a plan or apply.

**Database** (`aws_db_instance.orders`)
- It's `db.t4g.micro` with 20 GB of gp3 storage, using the existing subnet group and security group.
- It isn't publicly accessible, and storage is encrypted.
- Backups are kept for 7 days.
- Deletion protection is on, and a final snapshot is taken if it's destroyed.
- The engine version isn't pinned, so AWS picks its current default Postgres version.

**Outputs for the deploy job:** `db_host`, `db_port`, `db_name` and `db_username`. `db_security_group_id` was already there. I didn't output the password, so the deploy job has to get it from wherever it already gets secrets.

**Changes to `variables.tf` that you should check**
- I removed the committed default password (`orders-dev-2024`) and marked `db_password` as sensitive. You now have to supply it, for example with `TF_VAR_db_password`. Anywhere that relied on the default will fail until it's set. That password was in git history, so don't reuse it.
- The password is passed as a write-only attribute (`password_wo`), so it stays out of state and plan output. To rotate it, change `db_password` and increase the new `db_password_version` variable (default 1). This needs Terraform 1.11 or later, which `versions.tf` already requires.
