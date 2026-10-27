The orders database is added, but I couldn't fully validate it. `terraform fmt -check` passed. `terraform validate` failed because the AWS provider plugin wouldn't start in this sandbox, so I can't say the config is valid.

**`main.tf`**: new `aws_db_instance.orders`:
- **Instance:** Postgres on `db.t4g.micro` with 20 GB of gp3 storage, a database named `orders`, and the master user and password taken from `db_username` and `db_password`.
- **Network:** it uses the existing `aws_db_subnet_group.orders` and `aws_security_group.orders_db`, and it isn't publicly accessible.
- **Defaults I added:**
  - storage encryption
  - 7-day backups
  - deletion protection
  - a final snapshot named `orders-final` when the instance is destroyed

**`outputs.tf`**: new outputs `db_address`, `db_port`, `db_name` and `db_username`, alongside the existing `db_security_group_id`. I left the password out of the outputs because the deploy job already has it as a variable.

**`variables.tf`**: I removed the hardcoded default password (`orders-dev-2024`) from `db_password` and marked it `sensitive`. You now have to supply it at apply time, for example with `TF_VAR_db_password` or your secrets store.

The deletion protection, backups and final snapshot are my choices, not something you asked for. If this is a throwaway environment, loosen them, because deletion protection blocks `terraform destroy` until you turn it off.
