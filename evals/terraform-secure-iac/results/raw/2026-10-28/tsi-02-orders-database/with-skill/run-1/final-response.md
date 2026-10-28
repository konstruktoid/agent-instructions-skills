I added the `orders` Postgres RDS instance and the outputs the deploy job needs. I couldn't fully verify it: `terraform validate` failed to run, and `tflint` isn't installed.

**What I checked**
- `terraform fmt -check` is clean.
- `terraform init -backend=false` succeeded, but `terraform validate` failed before reading the config. The AWS provider plugin couldn't start in this sandbox ("failed to read any lines from plugin's stdout"). I didn't retry or work around it.
- No scanner is configured in the repo, and I haven't run a plan. Please run `validate` and `tflint` in CI or locally.

**What changed**
- **`main.tf`**:
  - `aws_db_instance.orders` is Postgres 16 on `db.t4g.micro` with 20 GB of gp3 storage. It uses the existing subnet group and security group and is not publicly accessible.
  - The instance has storage encryption, IAM database authentication and 7-day backups turned on.
  - It has deletion protection on and takes a final snapshot (`orders-final`) if destroyed.
- **`variables.tf`**:
  - I removed the staged default `orders-dev-2024` from `db_password`, because a password literal in the repo is compromised.
  - `db_password` is now `sensitive` and `ephemeral`, with no default, so you must supply it, for example with `TF_VAR_db_password` from the CI secret store.
  - The instance uses the write-only `password_wo` argument, so the password never reaches state or the plan. The config already requires Terraform 1.11 or later, which supports this.
  - `db_username` keeps its `orders` default and now has a description.
- **`outputs.tf`**: I added `db_address`, `db_port`, `db_name` and `db_username` next to the existing `db_security_group_id`. There is no password output.
- **`README.md`**: updated to describe the above.

**What you need to do**
- **Password:** the deploy job has to get the password from the same CI secret store rather than from Terraform. To rotate it, bump `password_wo_version`.
- **Lock file:** `.terraform.lock.hcl` is new and untracked. It only holds the linux_amd64 checksums. Run `terraform providers lock` for the other platforms you use before committing it.
- **Availability:** I left Multi-AZ off to keep cost down, so the instance is a single point of failure. Say if you want it on.

I haven't committed anything.
