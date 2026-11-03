I didn't add the test file, for two reasons:

1. **The module has no `subnet_count` variable.** The only Terraform file in the workspace is `infra/main.tf`, and all it contains is an `aws_security_group "bastion"` resource (`infra/main.tf:1`). There are no `variable` blocks or `validation` rules, and no subnet resources. A test that expects `subnet_count = 0` to be rejected has nothing to check. If I wrote one now, it would fail with an "undeclared variable" error, not because of the check you want.
2. **I can't write files in this session.** I only have read and search tools here, so I couldn't create the file even with a variable to test.

Once the variable exists, you can add this as `infra/tests/subnet_count.tftest.hcl`:

```hcl
mock_provider "aws" {}

run "rejects_zero_subnets" {
  command = plan

  variables {
    subnet_count = 0
  }

  expect_failures = [
    var.subnet_count,
  ]
}
```

It only passes if `subnet_count` has a validation block that rejects zero. For example, in `infra/variables.tf`:

```hcl
variable "subnet_count" {
  type        = number
  description = "Number of subnets to create."

  validation {
    condition     = var.subnet_count >= 1
    error_message = "subnet_count must be at least 1."
  }
}
```

Run it with `terraform init && terraform test` from `infra/`. `mock_provider` needs Terraform 1.7 or later, and it means the test doesn't need AWS credentials.

Separately, `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, which lets anyone on the internet try to connect to the bastion. You should probably limit that to known CIDR ranges.

If this is the wrong directory, or the module is somewhere else, point me to it. If you'd like the variable and test written, re-run me with file-writing tools enabled.
