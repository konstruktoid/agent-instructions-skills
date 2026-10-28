I added the orders database, but I couldn't validate it. `terraform fmt -check` passed, but `terraform init` failed with a disk quota error while downloading the AWS provider, so `terraform validate` never ran.

**`main.tf`**: a new `aws_db_instance.orders` with these settings:
- **Size and engine:** Postgres 17 on `db.t4g.micro`, with 20 GB of gp3 storage.
- **Network:** it uses the existing `orders` subnet group and `orders_db` security group, and it isn't publicly accessible. The security group only allows port 5432 from the app security group.
- **Safety settings I chose:** storage encryption, 7-day backups, deletion protection, and a final snapshot on destroy named `orders-final`. I also turned on CloudWatch log export for the `postgresql` and `upgrade` logs.
- **Credentials:** it uses `var.db_username` and `var.db_password`.

**`outputs.tf`**: the deploy job gets `db_address`, `db_port`, `db_name` and `db_username`. The existing `db_security_group_id` output is unchanged. I didn't output the password. The deploy job should take it from the same secret source you use to supply `db_password`.

**`variables.tf`**: I removed the hardcoded default password (`orders-dev-2024`) from `db_password` and marked it `sensitive`. You now have to pass it in, for example with `TF_VAR_db_password` from your CI secret store. Otherwise a plan would silently use a password that's committed to the repo.

- **Password in state:** the password is still stored in the Terraform state. If you'd rather avoid that, `manage_master_user_password = true` has RDS keep it in Secrets Manager, and the password variable goes away.
- **Single-AZ:** I left the database single-AZ to keep cost down. Set `multi_az = true` if you need failover.
- **Database name:** I named the database `orders`. Say so if you want a different name.
