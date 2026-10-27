I added the orders database and its outputs. `terraform validate` could not run here, so the config is not schema-checked, and nothing is committed or applied.

**What changed**
- `main.tf` now has an `aws_db_instance.orders`:
  - It is Postgres 16 on `db.t4g.micro` with 20 GB of encrypted gp3 storage.
  - It uses the existing subnet group and security group, and is not publicly accessible.
  - It keeps 7 days of backups, has deletion protection on, and takes a final snapshot when destroyed.
- `outputs.tf` adds `db_address`, `db_port`, `db_name` and `db_username` for the deploy job.
- `variables.tf`:
  - **Password default removed:** `db_password` had a committed literal default (`orders-dev-2024`). I removed it, so the password must now be supplied at run time, for example `TF_VAR_db_password` from the CI secret store. Treat the old literal as compromised and don't reuse it.
  - **Not stored in state:** `db_password` is now `sensitive` and `ephemeral` and is passed through the write-only `password_wo` argument. It never reaches state or plan files. This relies on the repo's existing Terraform ≥ 1.11 and AWS provider 6.
  - **New `db_password_version` variable:** To rotate the password, change the secret and increment `db_password_version`.
  - **Descriptions added:** I added descriptions to the two db variables.
- I added a `.gitignore` for `.terraform/`, state files and plan files. `.terraform.lock.hcl` was generated and is left for you to commit.

**For the deploy job:** the outputs give it the host, port, database name and username. There is deliberately no password output, so the job has to take the password from the same secret store that feeds `TF_VAR_db_password`.

**Checks**
- **`terraform fmt`:** clean.
- **`terraform validate`:** failed to load the AWS provider plugin in this sandbox ("failed to read any lines from plugin's stdout"). That is an environment problem, not a config error, but it means the config has not been schema-checked.
- **`tflint`:** not installed here, so not run.
- **`checkov`:** 17 passed and 7 failed. I did not suppress any of the failures:
  - **New database:** no Multi-AZ, enhanced monitoring, Performance Insights, IAM database authentication, log exports or query logging. These are cost or operational choices for you to make.
  - **Existing security group:** it has no description (CKV_AWS_23).
- **`terraform plan`:** not run, since there are no credentials or backend access here.

`final_snapshot_identifier = "orders-final"` is a fixed name, so a destroy and recreate cycle would fail on the name clash until the old snapshot is deleted.
