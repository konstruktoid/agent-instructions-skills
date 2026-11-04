I couldn't find a VPC module to fix in this workspace, so I haven't changed anything.

- **Terraform:** the only file is `infra/main.tf`, which holds a single `aws_security_group` named `bastion`. It has no VPC, no subnets and no outputs. A search for "subnet" (case-insensitive) matched nothing anywhere in the workspace.
- **Tests:** there are no `.tftest.hcl` files and no Terratest. The only Go file is `cmd/parser.go`, which has nothing to do with Terraform.
- **Skill baseline:** I couldn't read `terraform_coding_instructions.md`, the file the skill points to for the fmt, validate and tflint baseline. The read permission was denied, so I haven't applied that baseline.

The module is probably in another repository or on another branch, or it's a registry or git-sourced module that isn't checked out here. Can you tell me where it lives, or give me its path or repo?

Once I have it, I'll fix the output and add a test in whatever framework that repo already uses. The test will assert that the private subnet IDs output matches the private subnets and doesn't overlap the public ones. I'll also run it against the old code to confirm it fails there.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group. I didn't touch it, but you may want to restrict it.
