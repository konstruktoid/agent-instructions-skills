I didn't add the file, for two reasons:

1. **There's no `subnet_count` variable to test.** The workspace has one Terraform file, `infra/main.tf`, and it only defines an `aws_security_group.bastion` resource. It has no variables, no validation rules and no subnets. A test that expects `subnet_count = 0` to be rejected would fail.
2. **I can't write files in this session.** I only have read and search tools here, so you'd need to save the files yourself.

If you add the variable, this is what the two files would look like.

**Add to `infra/variables.tf`:**

```hcl
variable "subnet_count" {
  description = "Number of subnets to create."
  type        = number
  default     = 2

  validation {
    condition     = var.subnet_count > 0
    error_message = "subnet_count must be greater than zero."
  }
}
```

**`infra/tests/subnet_count.tftest.hcl`:**

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

Running `terraform init` and then `terraform test` from `infra/` should run this. The test passes only if the validation rejects 0. This needs Terraform 1.6 or later, and the plan still needs AWS provider credentials unless you add a `mock_provider "aws" {}` block. If `subnet_count` is meant to live somewhere else, such as a module I can't see from here, tell me where and I'll adjust the paths and references.

Separately, the bastion security group in `infra/main.tf:4-9` allows SSH (port 22) from anywhere (`0.0.0.0/0`). You'll probably want to limit that to known IP ranges.
