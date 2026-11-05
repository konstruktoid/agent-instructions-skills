I can't add the test yet, because I can't find the `subnet_count` variable or its validation block anywhere in the workspace.

- The only Terraform file is `infra/main.tf`. It contains a single `aws_security_group.bastion` resource and no variables.
- A search for `subnet_count`, and for "subnet" in any case, finds nothing in the workspace.
- There are no existing `.tftest.hcl` files and no Terratest. `cmd/parser.go` is the only other source file.

You may have the change uncommitted in another directory, or on a different branch. The git status only shows an untracked parent directory.

I also couldn't read the skill's tooling baseline file (`terraform_coding_instructions.md`) because the permission was denied. That doesn't block the test itself.

Where is the module with `subnet_count`? If you point me to it, I'll do the following:

1. Add a native `terraform test` file in the repo's layout, using `command = plan` so it creates nothing.
2. Add one run that expects the validation to reject `0`, and one that accepts a valid value such as `1`.
3. Confirm the rejection run fails when the validation block is reverted.

If you meant for me to write the variable and validation as well, tell me the intended minimum value. I'd assume `>= 1`.
