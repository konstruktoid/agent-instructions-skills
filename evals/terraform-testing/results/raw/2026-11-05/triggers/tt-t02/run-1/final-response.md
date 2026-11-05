I can't fix this yet because the repo has no VPC module. I didn't change anything.

- The only Terraform file is `infra/main.tf`, which holds a single `aws_security_group.bastion` resource.
- Searching the working directory for "subnet" (case-insensitive) finds nothing. There are no `.tftest.hcl` files, no Terratest code, and no module outputs.
- The other code is `cmd/parser.go`, which is Go and unrelated to this.

The VPC module is probably in a different repo or branch, or in a directory I wasn't pointed at. Can you give me its path, or the branch it's on?

I also couldn't read the skill's `terraform_coding_instructions.md` (the fmt/validate/tflint baseline). The read was denied because it sits outside the workspace. I'll need that access, or you can tell me to proceed without it.

Once I can see the module, I plan to:
1. Find the output and check whether it references `aws_subnet.public` instead of the private subnets.
2. Fix it.
3. Add a `terraform test` run block with `command = plan` that asserts the private output differs from the public one. I'll match whatever test framework the module already uses.
4. Revert the fix to confirm the new test fails.
