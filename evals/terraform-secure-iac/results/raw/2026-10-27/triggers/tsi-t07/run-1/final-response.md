I didn't add the test file. The only Terraform module in the workspace is `infra/main.tf`, and it has no `subnet_count` variable. It contains just one resource, `aws_security_group.bastion`, with no `variable` blocks. A test that expects zero to be rejected would fail because there's nothing to reject it. I also don't have a file-writing tool in this session, so I couldn't create the file anyway.

Here are two ways forward:

1. **If the variable lives somewhere else** (another branch, another module path), point me to it and I'll write the test against its real definition.
2. **If you want the variable added too**, it needs a validation rule first, then the test. For example:

   ```hcl
   # infra/variables.tf
   variable "subnet_count" {
     type = number

     validation {
       condition     = var.subnet_count > 0
       error_message = "subnet_count must be greater than zero."
     }
   }
   ```

   ```hcl
   # infra/tests/subnet_count.tftest.hcl
   run "rejects_zero_subnet_count" {
     command = plan

     variables {
       subnet_count = 0
     }

     expect_failures = [
       var.subnet_count,
     ]
   }
   ```

   This needs Terraform ≥ 1.6. Because the run uses `command = plan`, the AWS provider still has to be configured. If you don't want real credentials involved, add a `mock_provider "aws" {}` block (Terraform ≥ 1.7).

Separately, `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`. You may want to restrict that.
