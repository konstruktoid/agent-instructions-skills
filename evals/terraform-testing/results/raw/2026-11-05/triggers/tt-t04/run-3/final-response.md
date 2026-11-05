I haven't written any tests, because I can't find your change in the workspace.

- `infra/main.tf` is the only Terraform file. It has a single `aws_security_group.bastion` with an SSH ingress rule.
- It has no `allow_egress` variable, no egress rule and no `count` conditional.
- A search for `allow_egress` across the workspace returns nothing.
- The repo has no existing Terraform tests (no `.tftest.hcl` files, no Terratest, no plan-and-policy scripts).
- The skill's tooling-baseline file (`instructions/terraform_coding_instructions.md`) sits outside the workspace. I wasn't granted permission to read it, so I haven't applied that baseline.

Two things I'd need from you:
1. Where is the modified module? It may be uncommitted work on another branch or in another directory, or it may not have been saved.
2. Which test style should I use? With no existing tests, I'd default to native `terraform test`, using `command = plan` and a mock provider. That avoids creating real infrastructure. It also needs Terraform 1.7 or later, so tell me if you're on an older version.

Once I can see the change, I'd cover three cases:
- `allow_egress = true` plans exactly one egress rule.
- `allow_egress = false` plans none.
- The default value behaves as you intend.

I'd also revert the change to confirm the tests fail without it.
