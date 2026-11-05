I couldn't write the file. The Write tool is disabled in this session, and I wasn't able to read the skill's `references/secrets.md` either, because the read was denied. I also ran none of `terraform fmt`, `validate` or `tflint`, so none of this has been checked.

Below is the config I meant to put in `infra/rds.tf`. I wrote it from the standard AWS provider approach, not from the skill's reference file. Save it there and run `terraform fmt`, `terraform init -backend=false`, `terraform validate` and `tflint` before relying on it.

```hcl
variable "db_subnet_group_name" {
  description = "Name of an existing DB subnet group the instance is placed in."
  type        = string
}

variable "db_security_group_ids" {
  description = "Security group IDs attached to the instance. Controls which sources can reach the database port."
  type        = list(string)
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "db_key" {
  # Account-root statement lets IAM policies in this account grant key access.
  # Narrow this to specific administrator and consumer roles for production.
  statement {
    sid       = "EnableIAMPolicies"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }
}

resource "aws_kms_key" "db" {
  description             = "Encrypts the RDS storage and the RDS-managed master password secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.db_key.json
}

resource "aws_kms_alias" "db" {
  name          = "alias/app-db"
  target_key_id = aws_kms_key.db.key_id
}

resource "aws_db_instance" "main" {
  identifier        = "app-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t4g.medium"
  allocated_storage = 50

  db_name  = "app"
  username = "dbadmin"

  # RDS generates the master password and stores it in Secrets Manager,
  # encrypted with the key below. No password argument is set, so the
  # value never appears in configuration, variables, or Terraform state.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.db.arn

  storage_encrypted = true
  kms_key_id        = aws_kms_key.db.arn

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.db_security_group_ids
  publicly_accessible    = false

  iam_database_authentication_enabled = true
  multi_az                            = true
  backup_retention_period             = 7
  copy_tags_to_snapshot               = true
  deletion_protection                 = true
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "app-db-final"

  auto_minor_version_upgrade      = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials. Consumers read the password from here at runtime."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}
```

- **How the password stays out of Terraform:** `manage_master_user_password = true` makes RDS generate the password and keep it in Secrets Manager, encrypted with your KMS key. The config has no `password` argument and no password variable. State records only the secret's ARN.
- **Rotation:** RDS also rotates the secret for you.
- **Key policy:** the account-root statement is a permissive starting point. Replace it with specific admin and consumer roles for production.
- **Provider version:** `manage_master_user_password` needs AWS provider 5.x or later. `infra/main.tf` has no `required_providers` block, so pin the provider version and commit `.terraform.lock.hcl`.
- **Existing file:** `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the `bastion` security group. I didn't touch it, but a scanner will flag it.

I can write the file once Write access is available.
