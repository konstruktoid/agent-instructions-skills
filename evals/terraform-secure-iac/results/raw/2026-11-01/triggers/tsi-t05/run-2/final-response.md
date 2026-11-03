I couldn't create files or run anything in this session. I had no write or shell tool, and permission to read the skill's `secrets.md` reference was denied. So this hasn't been through `fmt`, `validate` or `tflint`. Save it as `infra/rds.tf` and run that loop before merging.

**How Terraform never sees the password:** with `manage_master_user_password = true`, RDS creates the master password itself and stores it in Secrets Manager, encrypted with your KMS key. There's no `password` argument, no `random_password` and no variable, so no password goes into config, plan or state. State only holds the secret's ARN, and Secrets Manager rotates the password (every 7 days by default for RDS-managed secrets).

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0" # pin to the exact version you test with; commit .terraform.lock.hcl
    }
  }
}

variable "identifier" {
  description = "Name of the RDS instance; also used in the KMS alias and final snapshot name."
  type        = string
}

variable "master_username" {
  description = "Master username for the database. RDS generates and stores the password."
  type        = string
  default     = "dbadmin"
}

variable "engine_version" {
  description = "PostgreSQL major or major.minor version."
  type        = string
  default     = "16"
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.medium"
}

variable "db_subnet_group_name" {
  description = "Existing DB subnet group made of private subnets."
  type        = string
}

variable "vpc_security_group_ids" {
  description = "Security groups attached to the instance; allow 5432 only from app tiers."
  type        = list(string)
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "rds_kms" {
  # Account root administers the key; access is then granted through IAM policies.
  statement {
    sid       = "AccountAdministration"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  # Lets principals in this account use the key only through RDS and Secrets Manager.
  statement {
    sid = "UseViaRdsAndSecretsManager"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:CreateGrant",
      "kms:DescribeKey",
    ]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    condition {
      test     = "StringEquals"
      variable = "kms:CallerAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values = [
        "rds.${data.aws_region.current.region}.amazonaws.com",
        "secretsmanager.${data.aws_region.current.region}.amazonaws.com",
      ]
    }
  }
}

resource "aws_kms_key" "rds" {
  description             = "Encrypts ${var.identifier} storage, Performance Insights, and its master user secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.rds_kms.json
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.identifier}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_instance" "main" {
  identifier     = var.identifier
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  # RDS generates the password and keeps it in Secrets Manager under this key.
  username                      = var.master_username
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.arn

  db_subnet_group_name                = var.db_subnet_group_name
  vpc_security_group_ids              = var.vpc_security_group_ids
  publicly_accessible                 = false
  iam_database_authentication_enabled = true

  backup_retention_period   = 7
  copy_tags_to_snapshot     = true
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.identifier}-final"

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  auto_minor_version_upgrade      = true
}

# ARN only; this is not the password. Grant apps secretsmanager:GetSecretValue on it
# plus kms:Decrypt on the key.
output "master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret that holds the RDS master credentials."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}

output "kms_key_arn" {
  description = "ARN of the KMS key encrypting the instance and its master secret."
  value       = aws_kms_key.rds.arn
}
```

**Before you merge:**
- **AWS provider version:** `manage_master_user_password` needs AWS provider 4.67 or later. `aws_region.region` needs 6.x; on 5.x use `.name` instead.
- **What else could leak a password:** don't add `password`, `password_wo` or `random_password` alongside this. Apps should read the secret at runtime, or use IAM authentication, which is enabled here.
- **Checks to run:** `terraform fmt -recursive -check -diff`, then `terraform init -backend=false && terraform validate`, then `tflint`. Run them in a sandbox with no credentials in the environment.
- **Existing bastion rule:** `infra/main.tf` already has a security group that opens SSH (port 22) to `0.0.0.0/0`, meaning anyone on the internet. I didn't change it, but don't put that group on the database. It should be narrowed or replaced with SSM Session Manager.
