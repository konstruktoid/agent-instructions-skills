I couldn't find a VPC module in this repo, so I haven't changed anything.

- **Terraform files:** the only one is `infra/main.tf`. It defines a single `aws_security_group` named `bastion` and has no VPC, subnets, or outputs.
- **Subnet references:** searching the whole workspace for "subnet" (case-insensitive) returned nothing.
- **Existing tests:** there are no `.tftest.hcl` files. The only Go file is `cmd/parser.go`, which isn't a test.
- **Baseline file:** I tried to read the skill's `terraform_coding_instructions.md`, but the read was denied. I didn't work around that.

The module may be on another branch, in another repo, or pulled in remotely. Can you tell me where it lives, or give me its path? Once I can see it, I'll:

1. Find the bad output, probably a `private_subnet_ids` output that points at the public subnet resource.
2. Fix it.
3. Add a native `terraform test` file with `command = plan` and a mock provider, so nothing real gets created. It would assert that the private IDs aren't the public ones.
4. Revert the fix to confirm the test fails without it.

One caveat: the mock provider needs Terraform 1.7 or later, so I'd check the module's `required_version` first.
