I couldn't write the file because the Write tool is disabled in this session. Here is the configuration, meant for `infra/database.tf`. I haven't run `terraform fmt`, `validate` or `tflint` on it. The skill's `references/secrets.md` was also blocked by a permission denial, so I wrote this from general knowledge rather than from the skill's reference.

```hcl
variable "db_subnet_group_name" {
  description = "Name of an existing DB subnet group (private subnets) the RDS instance is placed in."
  type        = string
}

variable "db_security_group_ids" {
  description = "Security group IDs attached to the RDS instance. Restrict ingress to the application tier."
  type        = list(string)
}

resource "aws_kms_key" "rds" {
  description             = "Encrypts the RDS storage, performance insights, and the managed master password secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

resource "aws_kms_alias" "rds" {
  name          = "alias/rds-main"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_instance" "main" {
  identifier     = "main"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t4g.medium"

  allocated_storage = 50
  storage_type      = "gp3"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  db_name  = "app"
  username = "dbadmin"

  # RDS generates the master password and stores it in Secrets Manager, so the
  # value is never in configuration, variables, or Terraform state.
  # Do not set `password` or `password_wo`.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.key_id

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.db_security_group_ids
  publicly_accessible    = false

  iam_database_authentication_enabled = true
  multi_az                            = true
  backup_retention_period             = 14
  copy_tags_to_snapshot               = true
  deletion_protection                 = true
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "main-final"
  auto_minor_version_upgrade          = true

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials. Contains the ARN only, not the password."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}
```

**How Terraform never sees the password:** `manage_master_user_password = true` makes RDS generate the password and store it in Secrets Manager, encrypted with the KMS key. The configuration has no password variable, and the state holds no password. Only the secret's ARN is exposed, and applications read the secret at runtime. A password you generate yourself would end up in state even if marked `sensitive`.

**What is not in the snippet:**
- **Missing pieces:** The snippet has no provider or backend block and no version pinning. Your repo has only `infra/main.tf`, which holds no provider block either. The values for the subnet group and security groups come from variables you supply.
- **KMS key policy:** The key uses the default policy. Add statements granting the application role `kms:Decrypt`, and scope `secretsmanager:GetSecretValue` to the secret ARN.
- **Existing `aws_security_group.bastion`:** In `infra/main.tf` it allows SSH from `0.0.0.0/0`. This is unrelated to your request, but you should restrict it.

If you re-enable Write, I'll create the file and run `fmt`, `validate` and `tflint` on it.
