I couldn't save any files or run anything this session. The only tools I had could read and search, so nothing below has been through `terraform fmt`, `validate` or `tflint` yet. I also couldn't open the skill's secrets reference file because permission wasn't granted, so the approach below is from what I already know of the AWS provider. Here's the configuration to add as `infra/rds.tf`:

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0" # commit .terraform.lock.hcl so the exact build is pinned
    }
  }
}

variable "vpc_id" {
  description = "ID of the VPC the database security group is created in."
  type        = string
}

variable "db_subnet_ids" {
  description = "Private subnet IDs the database subnet group spans. Use at least two availability zones."
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Security group allowed to connect to the database on port 5432."
  type        = string
}

data "aws_caller_identity" "current" {}

# One customer-managed key encrypts both the database storage and the
# Secrets Manager secret that RDS creates for the master password.
resource "aws_kms_key" "rds" {
  description             = "Encrypts RDS storage and the RDS-managed master user secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AccountAdministration"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "AllowUseViaRdsAndSecretsManager"
        Effect    = "Allow"
        Principal = { AWS = "*" }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:CallerAccount" = data.aws_caller_identity.current.account_id
            "kms:ViaService" = [
              "rds.${data.aws_region.current.region}.amazonaws.com",
              "secretsmanager.${data.aws_region.current.region}.amazonaws.com",
            ]
          }
        }
      },
    ]
  })
}

data "aws_region" "current" {}

resource "aws_kms_alias" "rds" {
  name          = "alias/rds-main"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_subnet_group" "main" {
  name       = "main-db"
  subnet_ids = var.db_subnet_ids
}

resource "aws_security_group" "db" {
  name        = "main-db"
  description = "PostgreSQL access from the application tier only"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id            = aws_security_group.db.id
  referenced_security_group_id = var.app_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  description                  = "PostgreSQL from app tier"
}

resource "aws_db_instance" "main" {
  identifier     = "main"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t4g.medium"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  username = "dbadmin"

  # RDS generates the password, stores it in Secrets Manager and rotates it.
  # No password argument is set, so the value never passes through
  # Terraform, the plan or the state.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.key_id

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false
  multi_az               = true

  iam_database_authentication_enabled = true
  deletion_protection                 = true
  backup_retention_period             = 7
  copy_tags_to_snapshot               = true
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "main-final"
  auto_minor_version_upgrade          = true

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  enabled_cloudwatch_logs_exports = ["postgresql"]
}

# Only the secret's ARN is exposed, never the password itself.
output "db_master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret RDS created for the master user password."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}
```

**How Terraform never sees the password:**
- There's no `password` argument, no random-password resource and no variable holding it. With `manage_master_user_password = true`, RDS creates the password inside AWS, stores it in Secrets Manager under the KMS key above, and rotates it there.
- The state only records the secret's ARN, never the password. Marking something `sensitive` would only hide it from output, and here there's no password to hide.
- Apps and people get the password from Secrets Manager using their own IAM permissions. IAM database authentication is also turned on, so most connections won't need the password at all.

**Choices worth knowing:**
- The KMS key policy only lets your own account use the key, and only through RDS and Secrets Manager. Account administration stays with the account root, the usual pattern.
- The database isn't publicly reachable. It runs in private subnets and only accepts connections on port 5432 from the app's security group.
- You need AWS provider 5.0 or later for these arguments. I used `~> 6.0`, which matches how `data.aws_region.current.region` is written; on 5.x, use `.name` instead. Commit `.terraform.lock.hcl` after `init`.

**Problem in your existing code:** `infra/main.tf:8` opens SSH (port 22) on the bastion host to `0.0.0.0/0`, meaning anyone on the internet. Limit that to known IP ranges, or remove the bastion and use SSM Session Manager.

**Before merging:** save the file as `infra/rds.tf`. Then, in a sandbox, run `terraform fmt -recursive -check -diff`, `terraform init -backend=false && terraform validate`, and `tflint`, plus `trivy config`/`checkov` if you use one. Finally, run `terraform plan` with read-only credentials and confirm no password appears in it.
