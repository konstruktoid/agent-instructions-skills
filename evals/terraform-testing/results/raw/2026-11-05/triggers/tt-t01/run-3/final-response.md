I can't add the test yet, because I can't find the `subnet_count` variable or its validation block.

- A search of the workspace for `subnet_count` returned nothing.
- The only Terraform file is `infra/main.tf`. It has a single `aws_security_group` resource and no variables.
- There are no existing `.tftest.hcl` files. The only Go file is `cmd/parser.go`, which isn't a test.
- I also couldn't read the skill's tooling baseline file (`terraform_coding_instructions.md`), because that path hasn't been granted.

Can you tell me where the change lives? It may be uncommitted on another branch, in a different directory, or not saved yet. Once I can see the variable, I'll write a native `terraform test` file with `command = plan`, since the repo has no existing test setup. It will have two cases:

- `subnet_count = 0` must fail with the validation error.
- A valid value such as `2` must pass.

I'll then confirm the zero case fails when the validation block is removed, and run `terraform fmt -check` on the new file.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I didn't change it, but you may want to look at it.
