I haven't written any tests, because your change isn't in this workspace.

- `infra/main.tf` is the only Terraform file. It holds one `aws_security_group.bastion` with an SSH ingress rule. It has no `allow_egress` variable, no egress rule and no `count` or `for_each` gating.
- A case-insensitive search for `egress` and `allow_egress` finds nothing anywhere in the repo.
- The git status shows no modified tracked files, so the change isn't sitting uncommitted either.
- The repo has no Terraform tests today, no `.tftest.hcl` files and no Terratest. The only test is the Python `tests/test_balance.py`.

The change may be unsaved, on another branch, or in a different checkout. Can you point me to it?

Once I can see it, I plan to use native `terraform test`, since the repo has no existing convention. The tests would use `command = plan` and a mocked AWS provider, so nothing real gets created. They would cover two cases:
- `allow_egress = true` plans exactly one egress rule.
- `allow_egress = false` plans none.

I'd also check that the tests fail when the change is reverted. One thing to confirm first is the Terraform version. Native tests need 1.6 or later, and `mock_provider` needs 1.7 or later. I'd check both against `required_version` and what CI runs.

I also couldn't read the skill's `terraform_coding_instructions.md` baseline, because the read permission was denied. I'll need that permission, or the file contents, to apply its `fmt`/`validate`/`tflint` baseline.
