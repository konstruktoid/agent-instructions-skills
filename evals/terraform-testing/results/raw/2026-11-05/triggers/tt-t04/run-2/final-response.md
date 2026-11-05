I can't add a test yet, because the change you describe isn't in this workspace.

- **No `allow_egress`:** `infra/main.tf` is the only Terraform file. It holds one `aws_security_group.bastion` resource with an inline ingress block. A search for `allow_egress` and for any egress rule found nothing.
- **No module:** there's no variable, no `count` or `for_each` on an egress rule, and no module directory. The git status shows only an untracked parent directory, so the change may be uncommitted somewhere else or on another branch.
- **No existing Terraform tests:** there are no `.tftest.hcl` files and no Terratest. The only Go file is `cmd/parser.go` and the only test is the Python `tests/test_balance.py`, so there's no convention to match yet.
- **Tooling baseline unread:** the skill's `terraform_coding_instructions.md` was blocked by a permission denial, so I haven't applied its fmt/validate/tflint baseline.

Please tell me where the modified module is, or commit or paste it. Once I can see it, I plan to write a native `terraform test` file. It would use `command = plan` with a mock provider, so nothing is created. It would cover two cases:
- `allow_egress = true` plans exactly one egress rule.
- `allow_egress = false` plans none.

I'd then confirm the false-case test fails when your change is reverted. That needs Terraform 1.7 or later for `mock_provider`, so I'd check the module's `required_version` first.
