I couldn't add the test, because the `subnet_count` variable isn't in this workspace.

- **No `subnet_count`:** a search for it across the whole workspace found nothing. The only Terraform file is `infra/main.tf`, which holds a single `aws_security_group.bastion` resource. It has no variables and no `validation` block.
- **No Terraform tests:** there are no `.tftest.hcl` files, no Terratest Go files, and no plan-and-policy scripts. The only other tests are Python ones in `tests/test_balance.py`.
- **Skill baseline unread:** I tried to read `terraform_coding_instructions.md`, the tooling baseline the skill points to, but the read was denied. I haven't applied that baseline.

Your change may be uncommitted, on another branch, or in a different directory. I didn't want to invent a variable and test it, because the test would then check something that isn't your code.

Can you tell me where the change lives, or commit or copy it into this workspace? Once I can see the variable, I'll add a native `terraform test` file. It will use `command = plan` so nothing is created. It will have one run asserting that `subnet_count = 0` fails validation, and one asserting that a valid value passes. I'll also check that the zero-value test fails if the validation block is removed. First I'll check that the module's `required_version` and the CI Terraform version are at least 1.6, which native tests need.

If you'd like me to read the instructions file, you can approve that read.
