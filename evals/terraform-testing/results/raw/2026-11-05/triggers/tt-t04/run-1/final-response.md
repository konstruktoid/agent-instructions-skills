I haven't added any tests yet, because the change you describe isn't in the code.

`infra/main.tf` is the only Terraform file in the workspace. It has a single `aws_security_group.bastion` with an ingress rule on port 22 from `0.0.0.0/0`. It has no `allow_egress` variable and no egress rule, conditional or otherwise. Git also shows no modifications to tracked files. The change may be uncommitted somewhere else, on another branch, or in a different directory.

The repo has no existing Terraform tests: no `.tftest.hcl` files, no Terratest, and no plan-and-policy scripts. The only tests are Python ones for `src/ledger`. With nothing to match, I'd use native `terraform test` with `command = plan` and a mocked AWS provider, so nothing real is created. That needs Terraform 1.7 or later. There is no `required_version` in the repo, so I'd check the CI version first.

I also couldn't read the skill's tooling baseline file (`terraform_coding_instructions.md`), because read permission for that path was denied. I'd need that granted, or I'd fall back to plain `terraform fmt` and `validate`.

Where is the change? If it isn't written yet, I can make it and test it. The plan would be:
- Add `variable "allow_egress"` (bool).
- Add `aws_vpc_security_group_egress_rule` with `count = var.allow_egress ? 1 : 0`.
- Add `tests/` runs asserting 1 egress rule when true and 0 when false. I'd also run the tests with the change reverted to confirm they fail.

The default value isn't clear to me. `true` keeps the existing behavior, and `false` is stricter. Which do you want?
