I've added the orders database in `main.tf` and the outputs the deploy job needs. I haven't run a plan or apply, so none of it has been checked against AWS.

`terraform fmt` and `terraform validate` are clean. `tflint` isn't installed here, so I didn't run it. Checkov passes 19 checks and fails 5, listed below.

**What changed**
- **`main.tf`:** `aws_db_instance.orders` is Postgres 16 on `db.t4g.micro` with 20 GB gp3, using the existing subnet group and security group.
  - It's encrypted, not publicly accessible, and has IAM auth enabled.
  - It keeps 7 days of backups, has deletion protection, takes a final snapshot, and exports the `postgresql` and `upgrade` logs to CloudWatch.
  - The ingress rule on the security group now has a description.
- **Password handling:** the password goes in as a write-only argument (`password_wo`), so it never lands in state or the plan. `db_password` is now `sensitive` and `ephemeral`.
- **Removed default password:** I deleted the default `orders-dev-2024` from `variables.tf`. It was a committed secret, so treat it as compromised and don't reuse it. Supply the password with `TF_VAR_db_password` from the CI secret store.
- **Outputs:** `db_address`, `db_port`, `db_name` and `db_username`. The password isn't output. The deploy job should read it from the same secret store.
- **Repo files:** I added a `.gitignore` for `.terraform/`, state and plan files, and a `.terraform.lock.hcl`. The lock file only records checksums for this platform. Run `terraform providers lock` for the platforms CI uses.

**Checkov findings left open**
- **Multi-AZ:** off, to keep the cost down for a micro instance.
- **Performance Insights:** not available on `db.t4g.micro`.
- **Enhanced monitoring and Postgres query logging:** need an IAM role and a parameter group, which I left out.
- **Security group description:** the group still has the default one. Changing it would force the security group to be replaced.

Decision for you: if this is production, turn on Multi-AZ. It roughly doubles the instance cost.

I didn't commit anything.
