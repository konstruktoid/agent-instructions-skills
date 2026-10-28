I couldn't create or check any files. This session has no file-write or shell tool, and reading the skill's `references/secrets.md` was denied. The configuration is below for you to save as files. None of the checks the skill calls for have been run: `terraform fmt`, `validate`, `tflint` or a scanner.

**How Terraform never sees the password:** setting `manage_master_user_password = true` makes RDS generate the master password itself. RDS stores it in Secrets Manager, encrypted with the KMS key below, and rotates it. The password never appears in a variable, a `.tfvars` file, the plan or the state. The state only holds the secret's ARN (in `master_user_secret`). Because of that, there's no `password` argument, no `random_password` resource and no password variable anywhere.

### `versions.tf`
```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.82.2" # exact pin; commit .terraform.lock.hcl with every CI platform
    }
  }
}
```

### `variables.tf`
```hcl
variable "name" {
  description = "Name prefix applied to the KMS alias, the DB instance identifier, and the subnet group."
  type        = string
}

variable "db_subnet_ids" {
  description = "Private subnet IDs the DB subnet group spans. At least two Availability Zones are required."
  type        = list(string)
}

variable "vpc_security_group_ids" {
  description = "Security group IDs attached to the DB instance. These control which sources can reach the database port."
  type        = list(string)
}

variable "master_username" {
  description = "Master user name for the DB instance. RDS generates the password and stores it in Secrets Manager."
  type        = string
  default     = "dbadmin"
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.medium"
}
```

### `kms.tf`
```hcl
data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "rds_kms" {
  # Account root delegates to IAM so the key can't become unmanageable.
  statement {
    sid       = "AccountAdmin"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  # RDS and Secrets Manager may use the key only when called through those services in this account.
  statement {
    sid = "AllowRdsAndSecretsManagerViaService"
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
      variable = "kms:ViaService"
      values = [
        "rds.${data.aws_region.current.name}.amazonaws.com",
        "secretsmanager.${data.aws_region.current.name}.amazonaws.com",
      ]
    }
    condition {
      test     = "StringEquals"
      variable = "kms:CallerAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_kms_key" "rds" {
  description             = "${var.name} RDS storage and master user secret"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.rds_kms.json
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.name}-rds"
  target_key_id = aws_kms_key.rds.key_id
}
```

### `rds.tf`
```hcl
resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db"
  subnet_ids = var.db_subnet_ids
}

resource "aws_db_instance" "this" {
  identifier     = var.name
  engine         = "postgres"
  engine_version = "16.4"
  instance_class = var.instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  username                      = var.master_username
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.rds.arn

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = var.vpc_security_group_ids
  publicly_accessible    = false

  iam_database_authentication_enabled = true
  multi_az                            = true
  backup_retention_period             = 7
  copy_tags_to_snapshot               = true
  deletion_protection                 = true
  skip_final_snapshot                 = false
  final_snapshot_identifier           = "${var.name}-final"

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  enabled_cloudwatch_logs_exports = ["postgresql"]
  auto_minor_version_upgrade      = true
}
```

### `outputs.tf`
```hcl
output "kms_key_arn" {
  description = "ARN of the KMS key encrypting DB storage and the master user secret."
  value       = aws_kms_key.rds.arn
}

output "db_endpoint" {
  description = "Connection endpoint of the DB instance."
  value       = aws_db_instance.this.endpoint
}

output "master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the RDS-managed master password. Applications read the password at runtime through this ARN."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}
```

**Security choices worth noting:**
- **One key for storage, the secret and Performance Insights:** this keeps the module small. If you want those to have separate blast radii or separate access, split it into separate keys.
- **Key policy:** RDS and Secrets Manager can use the key only when the call comes through those services in this account. The account root statement is there so the key can't become unmanageable.
- **Outputs:** only the secret's ARN is exposed, never its value. A consumer needs `secretsmanager:GetSecretValue` on that ARN plus `kms:Decrypt` through Secrets Manager to read the password. Nothing secret flows through Terraform, so no output needs `sensitive`.
- **Executing identity:** the role that runs `apply` needs `rds:*` on this instance and `kms:CreateKey`/`PutKeyPolicy`. It also needs `secretsmanager:CreateSecret`/`TagResource`, because RDS creates the secret using the caller's permissions. It does **not** need `GetSecretValue`.
- **Backend:** none is included. If this goes into a repository, add a remote backend with encryption, locking and versioning. The state still holds infrastructure metadata, just not the password.

**Still to do before merging:**
1. Run `terraform fmt -recursive -check -diff`.
2. Run `terraform init -backend=false && terraform validate`.
3. Run `tflint` and any scanner the repo uses.
4. Commit `.terraform.lock.hcl`.
5. Check that the provider pin `5.82.2` and Postgres `16.4` match what your repo and region support.
