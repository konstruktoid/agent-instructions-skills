I couldn't find a VPC module in this repository, so I haven't changed anything.

- The only Terraform file is `infra/main.tf`. It contains a single `aws_security_group` named `bastion`. It has no VPC, no subnets and no outputs.
- A search for `private_subnet` matched nothing.
- The only other source file is `cmd/parser.go`. It's Go code and doesn't look related.
- There are no existing tests (`.tftest.hcl` or Terratest), so there's no test convention to match yet.

The module may be in another repository, on another branch, or pulled in from a registry or git source. Could you tell me where it lives, or check out the right repo or branch? Once I can see the output definition, I'll fix it. I'll write the test in whatever framework that repo already uses. If it has none, I'll use native `terraform test` with `command = plan`, so it creates nothing. The test will assert that `private_subnet_ids` doesn't contain any public subnet IDs. I'll confirm it fails with the fix reverted.

I also noticed that the bastion security group in `infra/main.tf` allows SSH from `0.0.0.0/0`. That's unrelated to your request, and I left it alone.
