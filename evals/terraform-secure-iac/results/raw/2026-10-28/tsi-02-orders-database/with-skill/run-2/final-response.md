I added the orders Postgres RDS instance and the outputs for the deploy job, but `terraform validate` failed in this sandbox, so the configuration is unvalidated. `terraform fmt -check` passes. `terraform init -backend=false` ran, but the AWS provider binary wouldn't start ("Failed to read any lines from plugin's stdout"). I didn't retry. `tflint` and the config scanners (`trivy`, `tfsec`, `checkov`) aren't installed, so none of them ran. I also did no plan, since there are no AWS credentials here.

**What changed**
- **Database (`main.tf`):**
  - `aws_db_instance.orders` is Postgres 16 on `db.t4g.micro` with 20 GB of gp3 storage. It uses the existing subnet group and security group.
  - The instance is encrypted, not publicly accessible, has 7-day backups, deletion protection on, and takes a final snapshot on destroy. IAM database auth is also enabled.
  - You didn't ask for these hardening settings; I chose them. Say so if you want any removed.
- **Password handling (`variables.tf`):**
  - I removed the committed default password (`orders-dev-2024`) and marked `db_password` as sensitive. It now has no default, so supply it as `TF_VAR_db_password` from the CI secret store.
  - I treat that old password as compromised because it was in git history, so rotate it anywhere it was used.
  - The password goes to RDS through the write-only `password_wo` argument, so it never lands in state or plan files. This needs Terraform 1.11 or later, which `versions.tf` already requires. To rotate it later, bump `password_wo_version`.
  - I also added descriptions to both variables.
- **Outputs (`outputs.tf`):** `db_address`, `db_port`, `db_name` and `db_username`. I left the password out on purpose, so the deploy job has to read it from the secret store.
- **README:** updated to say the database now exists and how the password is supplied.

Two other things to know:
- **Lock file:** I didn't commit a `.terraform.lock.hcl` because the one from this run only covered the sandbox's platform. Generate it with `terraform providers lock` for the platforms your CI uses.
- **Engine version:** `engine_version = "16"` is my choice; change it if you need a specific minor version.

Please run `terraform validate`, `tflint` and `terraform plan` somewhere the provider runs before applying.
