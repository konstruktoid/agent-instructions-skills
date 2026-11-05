I couldn't add the test, because I couldn't find the `subnet_count` variable or its validation block.

- **No match in the workspace:** searching the workspace for `subnet_count` returned nothing. The only Terraform file is `infra/main.tf`, which holds a single `aws_security_group` and no variables. There are no existing `.tftest.hcl` files or Terratest files either.
- **Possible causes:** your change may be uncommitted somewhere I can't see, on another branch, or in a different directory. Git status shows only an untracked parent path.
- **Blocked reads:** two reads were denied. One was the skill's tooling-baseline file, `terraform_coding_instructions.md`. The other was a wider search of the run directory. So I haven't applied that baseline.

I didn't want to guess at the variable's type, default, or error message. A test written against a guessed validation block could pass without protecting anything.

Where is the variable, or can you paste the block? Once I have it, I'll add a native `terraform test` file with `command = plan` runs. It will check that `subnet_count = 0` is rejected and that a valid value is accepted. I'll also revert the validation to confirm the test fails without it.
