I couldn't create or run anything this session. I only have read and search tools here, and my request to read the skill's secrets reference was denied. So the config below is untested: `terraform fmt`, `validate`, `tflint` and `plan` have not been run on it. Put it in your repo (e.g. `infra/rds.tf`) and run those through your normal tooling before merging.

## How the password stays out of Terraform

`manage_master_user_password = true` has RDS create the master password itself and store it in Secrets Manager, encrypted with the key you name in `master_user_secret_kms_key_id`. The password never appears in your config, variables or plan, and Terraform state only holds the secret's ARN. There's no `password` argument at all, so it can't leak into state.

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.100.0" # exact pin; record checksums in a committed .terraform.lock.hcl
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_partition" "current" {}

variable "db_identifier" {
  description = "Identifier of the RDS instance and prefix for the KMS alias."
  type        = string
}

variable "db_subnet_group_name" {
  description = "Existing DB subnet group (private subnets) the instance is placed in."
  type        = string
}

variable "vpc_security_group_ids" {
  description = "Security groups attached to the instance; they control which sources can reach the database port."
  type        = list(string)
}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  partition  = data.aws_partition.current.partition
}

data "aws_iam_policy_document" "rds_kms" {
  # Key administration stays with the account; IAM policies decide who can use it.
  statement {
    sid       = "AccountAdministration"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:${local.partition}:iam::${local.account_id}:root"]
    }
  }

  # Cryptographic use only when the call comes through RDS or Secrets Manager in this account.
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
      values   = [local.account_id]
    }

    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values = [
        "rds.${local.region}.amazonaws.com",
        "secretsmanager.${local.region}.amazonaws.com",
      ]
    }
  }
}

resource "aws_kms_key" "rds" {
  description             = "Encrypts ${var.db_identifier} storage, Performance Insights, and its master user secret."
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.rds_kms.json
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.db_identifier}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_instance" "this" {
  identifier     = var.db_identifier
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t4g.medium"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  username                      = "dbadmin"
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
  final_snapshot_identifier = "${var.db_identifier}-final"

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn

  auto_minor_version_upgrade = true
}

output "db_endpoint" {
  description = "Connection endpoint of the RDS instance."
  value       = aws_db_instance.this.endpoint
}

output "master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the RDS-managed master password; read access is governed by IAM, not by Terraform."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}
```

## Other choices in this config

- **Key policy:** your account manages the key. Other callers can only use it through RDS or Secrets Manager in the same account and region. Who can actually read the password is then controlled by IAM access to `secretsmanager:GetSecretValue` on that secret ARN. Keep that permission narrow.
- **One key, three uses:** the same key encrypts storage, Performance Insights and the password secret. If you want separate keys, `master_user_secret_kms_key_id` can point at a key of its own.
- **Output:** only the secret's ARN is exposed, never its value, so it doesn't need `sensitive`.
- **Values to adjust:** I picked the engine, instance class, storage size and backup retention myself. The provider is pinned to an exact version (`5.100.0`). Change it to whatever version you've reviewed, and commit the `.terraform.lock.hcl` file.
- **Rotation:** RDS turns on rotation for the managed secret by default (every 7 days). Applications should fetch the password from Secrets Manager each time rather than caching it.

## An existing problem in your repo

`infra/main.tf:4-9` lets anyone on the internet reach port 22 on `aws_security_group.bastion` (`0.0.0.0/0`). Don't reuse that group for `vpc_security_group_ids`. Separately, I'd restrict its source CIDRs or replace the bastion with SSM Session Manager.
