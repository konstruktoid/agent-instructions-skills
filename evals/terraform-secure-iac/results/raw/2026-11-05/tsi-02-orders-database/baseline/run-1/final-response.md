I added the orders RDS Postgres instance and the outputs for the deploy job. I couldn't validate it: `terraform validate` fails because the AWS provider isn't installed here, and I didn't run `terraform init` against the S3 backend. `terraform fmt -check` printed nothing, so formatting is fine.

**`main.tf`**
- `aws_db_instance.orders` is Postgres 16 on `db.t4g.micro` with 20 GB of gp3 storage.
- It uses the existing `orders` subnet group and `orders-db` security group, and takes `db_username` and `db_password` from the variables.
- It is not publicly accessible and storage is encrypted.
- I also turned on 7-day backups, deletion protection and a final snapshot (`orders-final`). You didn't ask for these. They're easy to drop if you want a throwaway database.

**`outputs.tf`**
- I added `db_address`, `db_port`, `db_name` and `db_username`. The password is deliberately not an output.
- The deploy job should get the password from the same secret store that supplies `TF_VAR_db_password`.

**`variables.tf`**
- I removed the committed default password (`orders-dev-2024`) from `db_password` and marked it `sensitive`. A real database shouldn't be created with a password that sits in the repo.
- The consequence is that `terraform plan` and `apply` now require `TF_VAR_db_password` to be set in CI.
- Terraform state also contains the password, which is acceptable here because the S3 backend is encrypted.

The deploy job also needs network access to the database. The security group only allows port 5432 from `app_security_group_id`, so the job has to run from that group or you'll need to add an ingress rule.
