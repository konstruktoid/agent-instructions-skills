I couldn't write the files. The Write tool is disabled in this session, and I have no other way to create files. I also couldn't read the skill's `references/secrets.md`, because permission wasn't granted. The Terraform below is untested: I haven't run `fmt`, `validate`, `tflint` or a scanner on it.

Save the first block as `infra/database.tf` and the second as `infra/versions.tf`, or give me write access and I'll create them and run the checks.

## `infra/database.tf`

```hcl
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "db_key" {
  # Keeps account IAM in control of the key. Grant kms:Decrypt on this key to
  # the roles that read the master secret through their own IAM policies.
  statement {
    sid       = "EnableAccountIamPolicies"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }
}

resource "aws_kms_key" "db" {
  description             = "Encrypts the RDS storage and the managed master password secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.db_key.json
}

resource "aws_kms_alias" "db" {
  name          = "alias/${var.db_identifier}"
  target_key_id = aws_kms_key.db.key_id
}

resource "aws_db_instance" "main" {
  identifier     = var.db_identifier
  engine         = "postgres"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username

  # RDS generates the master password and stores it in Secrets Manager,
  # encrypted with the key below. The value is never in configuration, plan,
  # or Terraform state; only the secret's ARN is.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.db.key_id

  storage_encrypted = true
  kms_key_id        = aws_kms_key.db.arn

  publicly_accessible                 = false
  iam_database_authentication_enabled = true
  multi_az                            = true
  vpc_security_group_ids              = var.db_security_group_ids
  db_subnet_group_name                = var.db_subnet_group_name

  backup_retention_period         = 7
  copy_tags_to_snapshot           = true
  deletion_protection             = true
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${var.db_identifier}-final"
  auto_minor_version_upgrade      = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

variable "db_identifier" {
  description = "Name of the RDS instance, also used for the KMS alias."
  type        = string
  default     = "app-db"
}

variable "db_name" {
  description = "Name of the initial database created on the instance."
  type        = string
  default     = "app"
}

variable "db_username" {
  description = "Master user name. The password is generated and held by RDS in Secrets Manager."
  type        = string
  default     = "dbadmin"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version."
  type        = string
  default     = "16.4"
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.medium"
}

variable "db_allocated_storage" {
  description = "Allocated storage in GiB."
  type        = number
  default     = 50
}

variable "db_security_group_ids" {
  description = "Security groups attached to the instance. Allow database port access from application groups only."
  type        = list(string)
}

variable "db_subnet_group_name" {
  description = "Name of an existing private DB subnet group."
  type        = string
}

output "db_endpoint" {
  description = "Connection endpoint of the RDS instance."
  value       = aws_db_instance.main.endpoint
}

output "db_master_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the master credentials. Applications fetch the password from here at runtime."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}

output "db_kms_key_arn" {
  description = "ARN of the KMS key protecting the instance storage and master secret."
  value       = aws_kms_key.db.arn
}
```

## `infra/versions.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}
```

## How Terraform never sees the password

- **Managed password:** `manage_master_user_password = true` makes RDS generate the password and keep it in Secrets Manager. There is no password argument, variable or random resource. State holds only the secret's ARN.
- **Key:** `master_user_secret_kms_key_id` encrypts that secret with the customer-managed key. The same key encrypts the instance storage.
- **Key policy:** It delegates to account IAM. Grant `kms:Decrypt` on the key and `secretsmanager:GetSecretValue` on the secret to whatever roles need the password. The account ID comes from a data source, so none is hard-coded.
- **Rotation:** RDS rotates the managed secret automatically, every 7 days by default.

## Things to check before applying

- **Backend:** The repo has no backend or `.terraform.lock.hcl`. State still holds other sensitive attributes, so add an encrypted, locked, versioned backend.
- **Lock file:** Run `terraform init` and commit `.terraform.lock.hcl`.
- **Engine and sizing:** I chose PostgreSQL 16.4, `db.t4g.medium`, 50 GiB, Multi-AZ and 7-day backups. Change them to fit your needs.
- **Existing SSH rule:** `infra/main.tf` already has a bastion security group open to SSH from `0.0.0.0/0`. A scanner will flag it. I didn't touch it.
