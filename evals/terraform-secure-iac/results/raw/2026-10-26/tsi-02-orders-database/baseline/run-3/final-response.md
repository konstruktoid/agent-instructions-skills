I added the orders Postgres RDS instance and the outputs the deploy job needs. I couldn't run `terraform validate`: the AWS provider plugin wouldn't start in this sandbox. `terraform fmt -check` was clean, but the config has not been validated or planned.

**Database (`main.tf`)**
- `aws_db_instance.orders` is Postgres on `db.t4g.micro` with 20 GB of gp3 storage. It uses the existing `orders` subnet group and `orders-db` security group, which only allows port 5432 from the app security group.
- It is not publicly accessible, and storage is encrypted.
- It keeps 7 days of backups, has deletion protection on, and takes a final snapshot when destroyed.
- IAM database authentication is enabled.
- I didn't set an engine version, so RDS picks its current default. You may want to pin one.

**Password (`variables.tf`)**
- I removed the hardcoded default `orders-dev-2024` from `db_password`, because it would have been committed to the repo. It is now `sensitive` and must be at least 16 characters.
- You now have to supply it at plan/apply, for example with `TF_VAR_db_password`. If a pipeline relied on the old default, it needs updating.
- The instance uses the write-only `password_wo` argument, so the password never lands in Terraform state. To rotate it, change the password and bump the new `db_password_version` variable.
- `db_username` keeps its default of `orders`.

**Outputs (`outputs.tf`)**
- I added `db_endpoint`, `db_address`, `db_port`, `db_name` and `db_username`.
- There is no password output, because `terraform output -json` would expose it in plain text. The deploy job should get the password from your secrets store.
