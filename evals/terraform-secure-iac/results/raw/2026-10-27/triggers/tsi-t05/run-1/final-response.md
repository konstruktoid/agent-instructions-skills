I couldn't create a file because this session has no write or shell tool. That also means I didn't run `terraform fmt`, `validate`, `tflint` or a plan, so none of the configuration below is verified. I also couldn't read the skill's `references/secrets.md` (permission was declined), so this follows the skill's main checklist only. The only Terraform in the repo is `infra/main.tf`, so this is meant to go next to it, for example as `infra/rds.tf`.

**How the password stays out of Terraform:** with `manage_master_user_password = true`, RDS generates the master password itself and stores it in Secrets Manager, encrypted with your KMS key. No password argument exists anywhere, so the password never appears in config, variables, plan or state. State only holds the secret's ARN.

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.80.0" # exact pin; commit .terraform.lock.hcl with every CI platform
    }
  }
}

data "aws_caller_identity" "current" {}

variable "db_subnet_ids" {
  description = "Private subnet IDs the DB subnet group places the instance in."
  type        = list(string)
}

variable "db_security_group_ids" {
  description = "Security group IDs attached to the instance. Ingress should come from application security groups only."
  type        = list(string)
}

resource "aws_kms_key" "rds" {
  description             = "Encrypts the RDS instance storage and its RDS-managed master user secret."
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
      }
    ]
  })
}

resource "aws_kms_alias" "rds" {
  name          = "alias/app-rds"
  target_key_id = aws_kms_key.rds.key_id
}

resource "aws_db_subnet_group" "app" {
  name       = "app-db"
  subnet_ids = var.db_subnet_ids
}

resource "aws_db_instance" "app" {
  identifier     = "app-db"
  engine         = "postgres"
  engine_version = "16.4"
  instance_class = "db.t4g.medium"

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  db_name  = "app"
  username = "app_admin"

  # RDS generates the password and stores it in Secrets Manager. It never reaches config, plan or state.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.key_id

  db_subnet_group_name   = aws_db_subnet_group.app.name
  vpc_security_group_ids = var.db_security_group_ids
  publicly_accessible    = false

  iam_database_authentication_enabled = true
  backup_retention_period             = 7
  deletion_protection                 = true
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "app-db-final"
  copy_tags_to_snapshot               = true
  auto_minor_version_upgrade          = true
  performance_insights_enabled        = true
  performance_insights_kms_key_id     = aws_kms_key.rds.arn
}

output "db_master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret that holds the RDS-generated master credentials."
  value       = aws_db_instance.app.master_user_secret[0].secret_arn
}
```

**Design choices:**
- **No `password` and no `random_password`:** either one would put the password in state. The output only shows a secret ARN, which isn't sensitive, so it isn't marked `sensitive`.
- **Same KMS key for storage and the secret:** this is a simplification. Use two separate keys if you want the people who can decrypt the secret to be different from the people who can decrypt storage or snapshots.
- **Key policy:** it only grants account-root administration, so IAM policies decide who can use the key. You could restrict this further to named admin and user roles.
- **Version numbers:** the provider version, engine version and instance class are placeholders. Replace them with the versions your repo uses.

**Unrelated problem in `infra/main.tf`:** the `bastion` security group allows SSH (port 22) from `0.0.0.0/0`, meaning the whole internet. I didn't change it, but it should be limited to known address ranges or replaced with SSM Session Manager.

**To finish:** save the file, then run `terraform fmt -recursive -check -diff`, `terraform init -backend=false && terraform validate`, and `tflint`. Run these in a sandbox with no credentials, because `init` downloads provider plugins that run as native code. If you can save the file and give me shell access, I'll run that loop myself.
