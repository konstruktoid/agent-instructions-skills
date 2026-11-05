I couldn't write the file. The Write tool is disabled in this session, and my read of the skill's `references/secrets.md` was also denied. Below is the Terraform I intended to save as `infra/database.tf`. I haven't run `fmt`, `validate`, `tflint` or a scanner on it.

```hcl
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "db_key" {
  # Key administration stays with the account root, so IAM policies govern access.
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
  description             = "Encrypts the RDS instance storage and its managed master password secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.db_key.json
}

resource "aws_kms_alias" "db" {
  name          = "alias/${var.name}-db"
  target_key_id = aws_kms_key.db.key_id
}

resource "aws_db_instance" "main" {
  identifier     = "${var.name}-db"
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage = var.allocated_storage
  storage_encrypted = true
  kms_key_id        = aws_kms_key.db.arn

  db_name  = var.db_name
  username = var.master_username

  # RDS generates the master password and stores it in Secrets Manager,
  # encrypted with the key above. No password is in configuration or state.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.db.key_id

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.vpc_security_group_ids
  publicly_accessible    = false

  iam_database_authentication_enabled = true
  multi_az                            = true
  backup_retention_period             = 7
  deletion_protection                 = true
  copy_tags_to_snapshot               = true
  auto_minor_version_upgrade          = true
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "${var.name}-db-final"

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.db.arn
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

variable "name" {
  description = "Prefix used in the names of the KMS alias and the RDS instance."
  type        = string
}
variable "engine_version" {
  description = "PostgreSQL engine version for the RDS instance."
  type        = string
  default     = "16.4"
}
variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.medium"
}
variable "allocated_storage" {
  description = "Allocated storage in GiB."
  type        = number
  default     = 50
}
variable "db_name" {
  description = "Name of the initial database."
  type        = string
}
variable "master_username" {
  description = "Master username. The password is generated and held by RDS in Secrets Manager."
  type        = string
  default     = "dbadmin"
}
variable "db_subnet_group_name" {
  description = "Name of an existing private DB subnet group."
  type        = string
}
variable "vpc_security_group_ids" {
  description = "Security groups attached to the instance."
  type        = list(string)
}

output "db_endpoint" {
  description = "Connection endpoint of the RDS instance."
  value       = aws_db_instance.main.endpoint
}
output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials. Consumers read the value at runtime."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}
```

**How Terraform never sees the password:**
- `manage_master_user_password = true` makes RDS generate the password and keep it in Secrets Manager.
- The secret is encrypted with the customer-managed KMS key through `master_user_secret_kms_key_id`.
- The configuration has no password argument, variable or output, and the state has no password value.
- The state does hold the secret's ARN and the instance metadata, so the state backend still needs encryption and access control.
- The output exposes only the secret ARN. Applications fetch the value at runtime with `secretsmanager:GetSecretValue` and `kms:Decrypt`.

**Things to check before you use it:**
- The key policy delegates access to IAM through the account root. Grant the application role `kms:Decrypt` on this key, or it can't read the secret.
- `engine_version` and `instance_class` are placeholder defaults. Change them to match what you run.
- The instance has deletion protection and a final snapshot, so `terraform destroy` will need extra steps.
- The existing `infra/main.tf` has a bastion security group open to `0.0.0.0/0` on port 22. I didn't touch it, but you should look at it.

If you re-enable Write, I'll save the file and run `terraform fmt`, `terraform validate` and `tflint`.
