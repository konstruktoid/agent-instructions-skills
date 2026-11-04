I couldn't find a VPC module, so I haven't changed anything.

The only Terraform file in this workspace is `infra/main.tf`. It contains a single `aws_security_group.bastion` resource, with no VPC, no subnets and no outputs. I also found no `.tftest.hcl` files, Terratest, or other Terraform tests. The `tests/` directory holds only a Python test for the ledger code.

Because the module isn't here, I can't tell what the bug is or write a test that fails on it. I'd only be guessing at the code.

Some things that would help:
- Is the VPC module on another branch, in another repo, or in a path I haven't been pointed to? If so, give me the path or the checkout.
- Do you know which output is wrong? It may be `private_subnet_ids`, and the cause may be a wrong resource reference or a wrong `for` filter.

Once I can see the module, I'll fix the output. I'll follow whatever test approach it already uses. If it has none and its `required_version` is 1.6 or later, I'll add a native `terraform test` file. That test would use `command = plan` and a mocked provider. It would assert that the private IDs output matches the private subnets and doesn't include the public ones. I'd then confirm the test fails with the fix reverted.

I also couldn't read the skill's `terraform_coding_instructions.md` baseline. Permission to read that path wasn't granted. I'll need that read approved, or the file copied into the workspace, before I run the `fmt`/`validate`/`tflint` checks.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. That's outside this task, so I left it alone, but you may want to look at it.
