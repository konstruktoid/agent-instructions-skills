I couldn't find a VPC module in this repo, so I haven't changed anything.

- **Terraform:** the only file is `infra/main.tf`. It has one resource, a `bastion` security group. It has no VPC, no subnets and no outputs.
- **Search:** nothing in the workspace mentions `private_subnet`.
- **Tests:** there are no `.tftest.hcl` files and no Terratest code. `tests/test_balance.py` is the only test, and it is for the Python ledger code.
- **Skill baseline:** I couldn't read the skill's tooling-baseline file (`terraform_coding_instructions.md`) because the read was denied, so I haven't applied it.

The module may be in another repository or on another branch. It may also be a remote module that this repo only calls. Can you tell me where it lives, or give me the path?

Once I can see it, I'll fix the output so it returns the private subnet IDs. I'll then add a native `terraform test` with `command = plan` that asserts the private output doesn't match the public IDs. I'll also run it with the fix reverted to confirm it fails.
