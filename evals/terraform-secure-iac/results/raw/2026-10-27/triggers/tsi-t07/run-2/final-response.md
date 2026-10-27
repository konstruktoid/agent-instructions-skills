I didn't add the test file, because the module has no `subnet_count` variable to test.

The only Terraform file in the workspace is `infra/main.tf`. It contains a single `aws_security_group "bastion"` resource, with no `variable` blocks and no validation rules. I also don't have a file-writing tool in this session, so I couldn't have created the file anyway.

A `terraform test` that checks zero is rejected needs a `validation` block on the variable to trigger. Without one, `subnet_count = 0` would be accepted and the test would fail.

Do you want me to add the variable and its validation, or is the real module somewhere else? If I add it, the pair would look like this:

```hcl
# infra/variables.tf
variable "subnet_count" {
  type        = number
  description = "Number of subnets to create."

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

The test plans with `subnet_count = 0` and passes only if the variable's validation rejects it. You'd run it with `terraform init && terraform test` from `infra/`.

Separately, `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, meaning anyone on the internet. That's worth tightening, but it's outside what you asked, so I haven't touched it.
