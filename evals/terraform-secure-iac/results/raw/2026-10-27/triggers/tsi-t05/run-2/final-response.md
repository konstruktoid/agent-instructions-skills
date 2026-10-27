I don't have a file-write or shell tool in this session, so nothing was written to the repo and nothing was run. The configuration is below for you to drop in, for example as `infra/rds.tf` next to `infra/main.tf`.

**How the password stays out of Terraform:** the code sets `manage_master_user_password = true`. RDS then creates the password itself and keeps it in Secrets Manager, encrypted with the KMS key below. There is no `password` argument, so the password never appears in config, variables, the plan or state. Terraform only ever holds the secret's ARN.

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.100.0" # exact pin; RDS-managed master password needs >= 4.61
    }
  }
}

variable "name" {
  description = "Name prefix for the KMS alias, DB identifier, and final snapshot."
  type        = string
}

variable "db_subnet_group_name" {
  description = "Existing DB subnet group (private subnets only) the instance is placed in."
  type        = string
}

variable "vpc_security_group_ids" {
  description = "Security groups attached to the instance; they control which sources can reach the DB port."
  type        = list(string)
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.medium"
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

data "aws_iam_policy_document" "rds_kms" {
  # Key administration stays with the account; IAM policies grant usage.
  statement {
    sid       = "AccountAdmin"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  # Restrict use of the key to RDS and Secrets Manager in this account.
  statement {
    sid = "AllowUseViaRdsAndSecretsManager"
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
      test     = "StringLike"
      variable = "kms:ViaService"
      values   = ["rds.*.amazonaws.com", "secretsmanager.*.amazonaws.com"]
    }
  }
}

resource "aws_kms_key" "rds" {
  description             = "${var.name} RDS storage, Performance Insights, and master user secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.rds_kms.json
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.name}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_instance" "this" {
  identifier     = var.name
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  # RDS generates and rotates the password in Secrets Manager; no `password` argument,
  # so the value never enters configuration, plan, or state.
  username                      = "dbadmin"
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.arn

  iam_database_authentication_enabled = true

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.vpc_security_group_ids
  publicly_accessible    = false
  multi_az               = true

  backup_retention_period   = 7
  copy_tags_to_snapshot     = true
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.name}-final"

  auto_minor_version_upgrade            = true
  performance_insights_enabled          = true
  performance_insights_kms_key_id       = aws_kms_key.rds.arn
  enabled_cloudwatch_logs_exports       = ["postgresql", "upgrade"]
}

# The secret's ARN is an identifier, not a credential; readers still need
# secretsmanager:GetSecretValue plus kms:Decrypt on the key above.
output "master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the RDS-managed master password."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}

output "kms_key_arn" {
  description = "ARN of the KMS key encrypting the instance storage and its master user secret."
  value       = aws_kms_key.rds.arn
}
```

## Design choices
- **Instance settings:** the instance has no public IP, is deployed across availability zones and has deletion protection. A final snapshot is taken if it's deleted, and IAM database login is enabled so apps don't need the master password at all.
- **Key access:** the key policy only allows the key to be used through RDS and Secrets Manager in your own account. Managing the key stays with the account root. Automatic key rotation is on, and RDS rotates the password itself.
- **Provider version:** pinned to exactly `5.100.0`. Run `terraform init` and commit `.terraform.lock.hcl` with hashes for every platform your CI uses. If the repo is already on 6.x, change the pin to match.

## Not done
- **No checks run:** the skill requires `terraform fmt -check`, `init -backend=false` with `validate`, `tflint` and a plan, but I couldn't run any of them. Treat the code as unverified until you have.
- **Not read:** the skill's `references/secrets.md` and the repo's rule files, because the first read was denied.
- **No backend block:** `infra/` has none, so state would be local. State here holds no password, but it should still live in an encrypted, locked, versioned remote backend.

## Problem in the existing code
`infra/main.tf:4-9` opens SSH (port 22) on the bastion security group to `0.0.0.0/0`, meaning the whole internet. Don't add that group to `vpc_security_group_ids`. Open the DB port only to the app's security group.
