I haven't written any tests, because I can't find your change in this workspace.

- `infra/main.tf` is the only Terraform file. It defines a single `aws_security_group.bastion` with an SSH ingress rule.
- Nothing in the repo mentions `allow_egress` or an egress rule. A case-insensitive search for both terms found no matches.
- There is no variable, no `aws_vpc_security_group_egress_rule` or `aws_security_group_rule` resource, and no `count` or `for_each` conditional. The repo has no `.tftest.hcl` files or Terratest suite either.
- `git status` shows no modified files, so the change isn't sitting uncommitted in this checkout. It may be on another branch, in another directory, or unsaved.

If I wrote tests now, they would assert behavior that doesn't exist yet, and I couldn't check that they fail without the change.

**What I need from you:** point me to the module (the path or branch with your change), or tell me to add `allow_egress` to `infra/main.tf` myself.

**Test plan once the change is there:**
- The repo has no existing test framework. The default would be native `terraform test` with `command = plan` and `mock_provider "aws"`. That needs Terraform 1.7 or later, so I'd check the module's `required_version` and the CI version first.
- Two runs would cover it. With `allow_egress = true`, the plan contains exactly one egress rule. With `allow_egress = false`, the plan contains none.
- I'd also cover the default value of `allow_egress`, and a non-bool input being rejected if the variable has validation.
- To confirm the tests work, I'd revert the conditional and check that the `false` case fails. I'd also run `terraform fmt -check` and `tflint`, and make sure no state or `.terraform/` files are left behind.

I also couldn't read `instructions/terraform_coding_instructions.md`, the tooling baseline the skill points to, because that path wasn't permitted. I'd need that access, or you could tell me the baseline directly.
