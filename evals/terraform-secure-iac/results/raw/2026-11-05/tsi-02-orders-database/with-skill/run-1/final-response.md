I added the orders RDS Postgres instance and the outputs the deploy job needs. `terraform fmt` and `terraform validate` pass. `tflint` isn't installed here, so I didn't run it. I also didn't run a backend-enabled `plan`, because there are no credentials in this environment. Nothing is committed.

**Database (`main.tf`)**
- Instance:
  - Postgres 16 on `db.t4g.micro` with 20 GB of gp3 storage, using the existing subnet group and security group.
  - The storage is encrypted and the instance is not publicly accessible.
- Safety settings:
  - It keeps 7 days of backups.
  - Deletion protection is on, and a final snapshot is taken if the instance is destroyed.
- The settings I picked, which you may want to change: Postgres 16, gp3, 7-day backups, and the database name `orders`.

**Password (`variables.tf`)**
- The staged `db_password` had a literal default (`orders-dev-2024`), which is now in git history, so treat it as compromised. I removed the default and marked the variable `sensitive` and `ephemeral`.
- It is passed to RDS through a write-only argument (`password_wo`), so it never reaches state or plan files. This relies on the `required_version >= 1.11.0` and `~> 6.0` provider constraints already in `versions.tf`.
- You now have to supply it at plan and apply time, for example through `TF_VAR_db_password` from the CI secret store.
- I added `db_password_version`. Increment it when you rotate the password, because Terraform can't detect a change to a write-only value.
- `db_username` keeps its `orders` default and now has a description.

**Outputs (`outputs.tf`)**
- The new outputs are `db_address`, `db_port`, `db_name` and `db_username`. None of them is the password.
- The deploy job has to get the password from the same secret store that feeds `TF_VAR_db_password`.

**Repo hygiene**
- I added a `.gitignore` covering `.terraform/`, state files, plan files and `*.tfvars`.
- I generated `.terraform.lock.hcl` for linux amd64, linux arm64 and darwin arm64. Commit it, and add any other platform your CI runs on.
