I added the `orders` Postgres RDS instance to `main.tf`. `terraform fmt` and `terraform validate` pass. I haven't run `plan` or `apply`, so nothing has been created in AWS.

**The instance**
- It is `db.t4g.micro` with 20 GB of gp3 storage, using the existing `orders` subnet group and `orders-db` security group.
- Storage is encrypted and the instance isn't publicly accessible.
- Backups are kept for 7 days, and deletion protection is on.
- A final snapshot named `orders-final` is taken if the instance is destroyed.
- The engine version is left to the AWS default. Pin `engine_version` if you want a specific one.

**Outputs for the deploy job:** `db_host`, `db_port`, `db_name` and `db_username` are in `outputs.tf`. There is no password output. The deploy job should get the password from the same secret source that supplies `db_password`.

**Password variable:** I removed the hardcoded default (`orders-dev-2024`) from `db_password` in `variables.tf` and marked it `sensitive`. Anyone running Terraform now has to supply it, for example with `TF_VAR_db_password`. Make sure the pipeline sets that before the next plan. The old default is in git history, so don't reuse it for a real database.

The password is still stored in the Terraform state, which is in an encrypted S3 bucket. If you'd rather keep it out of state, RDS can generate and manage the password in Secrets Manager (`manage_master_user_password`). I used your `db_password` variable as asked.
