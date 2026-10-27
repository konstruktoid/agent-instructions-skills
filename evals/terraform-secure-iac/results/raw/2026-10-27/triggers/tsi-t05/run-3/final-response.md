I don't have file-write or shell tools in this session, so I couldn't save this to `infra/` or run the checks. Here is the configuration to add, for example as `infra/rds.tf` and `infra/versions.tf`.

### The approach

The password is never set in Terraform. `manage_master_user_password = true` has RDS generate the master password itself and store it in AWS Secrets Manager, encrypted with your KMS key. Terraform only gets the secret's ARN back, so the password is never in your config, variables, plan, or state. RDS also rotates the password for you (every 7 days by default).

The alternatives are weaker:
- `random_password` puts the password into state.
- A `password` variable puts it into state and usually into a `.tfvars` file.
- `password_wo` (the write-only argument) keeps it out of state, but Terraform still handles the value.

### `versions.tf`

```hcl
terraform {
  required_version = ">= 1.11.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.17.0" # pin exactly; commit .terraform.lock.hcl for every CI platform
    }
  }
}
```

### `rds.tf`

```hcl
data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

variable "db_identifier" {
  description = "Name of the RDS instance. Also used as the prefix for the KMS alias and the final snapshot name."
  type        = string
}

variable "db_subnet_group_name" {
  description = "Name of an existing DB subnet group made of private subnets. The instance is placed in these subnets."
  type        = string
}

variable "vpc_security_group_ids" {
  description = "IDs of the security groups attached to the instance. They control which sources can reach the database port."
  type        = list(string)
}

variable "engine_version" {
  description = "PostgreSQL major or major.minor version. Minor upgrades are applied automatically during the maintenance window."
  type        = string
  default     = "17"
}

variable "instance_class" {
  description = "RDS instance class, which sets the instance's CPU and memory."
  type        = string
  default     = "db.t4g.medium"
}

resource "aws_kms_key" "rds" {
  description             = "Encrypts ${var.db_identifier} storage, Performance Insights, and its managed master-user secret"
  enable_key_rotation     = true
  rotation_period_in_days = 365
  deletion_window_in_days = 30

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AccountAdministration"
        Effect    = "Allow"
        Principal = { AWS = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "UseViaRdsAndSecretsManagerOnly"
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
  name          = "alias/${var.db_identifier}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_instance" "this" {
  identifier     = var.db_identifier
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  # RDS generates the password and stores it in Secrets Manager.
  # Terraform never receives it, so it is not in plan or state.
  username                      = "dbadmin"
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.arn

  iam_database_authentication_enabled = true

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = var.vpc_security_group_ids
  publicly_accessible    = false
  multi_az               = true

  backup_retention_period    = 7
  copy_tags_to_snapshot      = true
  deletion_protection        = true
  skip_final_snapshot        = false
  final_snapshot_identifier  = "${var.db_identifier}-final"
  auto_minor_version_upgrade = true

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

output "master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret that holds the master credentials. Applications and operators read the password from here, subject to IAM."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}
```

### Other security choices
- **KMS key:** automatic key rotation is on, and there is a 30-day deletion window. Apart from administration by the account root, the key can only be used through RDS and Secrets Manager in this account and region. The same key encrypts the database storage, Performance Insights data, and the password secret.
- **Who can read the password:** this is now a matter of IAM permissions. Only principals with `secretsmanager:GetSecretValue` on the secret, plus `kms:Decrypt` through Secrets Manager, can read it. Grant that narrowly.
- **Access:** the database is not publicly accessible. IAM database authentication is on, so applications can use short-lived tokens instead of the master user.
- **Data loss protection:** deletion protection is on, a final snapshot is taken on delete, and backups are kept for 7 days.
- **Output:** it exposes only the secret's ARN, which is not secret, so it doesn't need `sensitive`.

### Not done
- **Not verified:** I couldn't run `terraform fmt`, `init -backend=false`/`validate`, `tflint`, or a scanner here. Check that `aws_region`'s `.region` attribute matches the provider version you pin. Older providers call it `.name`.
- **Separate issue:** `infra/main.tf:8` opens SSH on the `bastion` security group to `0.0.0.0/0`. Restrict it to known address ranges, or replace the bastion with SSM Session Manager.
- **State backend:** `infra/` has no backend configured. Even with the password out of state, state should live in an encrypted, access-controlled, versioned backend with locking.
