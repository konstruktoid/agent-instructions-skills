I added the orders database, but I couldn't validate it. `terraform validate` failed because the AWS provider isn't installed here and `terraform init` didn't install it (I discarded its output). `terraform fmt -check` printed nothing, so formatting passed. I haven't run `terraform plan` or `apply`.

**`main.tf`** has a new `aws_db_instance.orders`:
- **Size and engine:** Postgres 16 on `db.t4g.micro`, with 20 GB of gp3 storage.
- **Network:** it uses the existing `aws_db_subnet_group.orders` and `aws_security_group.orders_db`, and it isn't publicly accessible.
- **Credentials:** it takes `db_username` and `db_password` from the variables.
- **Protection (my additions):**
  - Storage is encrypted.
  - Backups are kept for 7 days.
  - Deletion protection is on.
  - A final snapshot is taken on destroy.

**`outputs.tf`** now exposes `db_address`, `db_port`, `db_name` and `db_username`. `db_username` is marked sensitive. There is deliberately no password output, so the deploy job should get the password from the same secret source you use to supply `db_password`.

**`variables.tf`:** I removed the hardcoded default password (`orders-dev-2024`) and marked `db_password` as sensitive. You now have to supply it, for example with `TF_VAR_db_password` or a secrets store. Otherwise the password would sit in git and be used by default.

The deletion protection, backup and snapshot settings are choices I made, not part of your request. Say so if you'd rather drop any of them. The `orders-final` snapshot name is fixed, so a second destroy will fail until the old snapshot is deleted.
