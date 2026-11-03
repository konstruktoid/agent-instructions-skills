I couldn't add the test, for two reasons:

1. **There's no `subnet_count` variable to test.** The workspace has only one Terraform file, `infra/main.tf`. It defines a single `aws_security_group "bastion"` resource with no `variable` blocks, so there's no `subnet_count` and no validation for a test to check.
2. **I can't create files in this session.** I can read and search files, but I don't have a write or shell tool, so I couldn't write the test file or run `terraform test`.

If you add the variable and enable file writes, this is what I'd add.

In `infra/variables.tf`:

```hcl
variable "subnet_count" {
  type        = number
  description = "Number of subnets to create."
  default     = 2

  validation {
    condition     = var.subnet_count > 0
    error_message = "subnet_count must be greater than zero."
  }
}
```

In `infra/tests/subnet_count.tftest.hcl`:

```hcl
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

`expect_failures = [var.subnet_count]` makes the test pass only if that variable's validation rejects the value. You'd run it with `terraform init && terraform test` from `infra/`. The plan also needs AWS provider credentials, or a `mock_provider "aws" {}` block in the test file to avoid them.

Separately, `main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. You probably want to restrict that to known IP ranges.
