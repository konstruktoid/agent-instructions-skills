I haven't added any tests, because the change you describe isn't in this repository.

- **No `allow_egress`:** searching the whole workspace finds no `allow_egress` variable and no egress rule.
- **No egress resource:** the only Terraform file is `infra/main.tf`. It defines one `aws_security_group.bastion` with an inline SSH ingress block, and it has no `variable` blocks and no `aws_vpc_security_group_egress_rule` or `aws_security_group_rule` resource.
- **No existing tests:** there are no `.tftest.hcl` files or Terratest files. The only other source file is `cmd/parser.go`, which is Go but unrelated to Terraform.
- **Git status:** the only untracked entry is the parent directory, so your change doesn't appear to be sitting uncommitted either.

The change may be on another branch, in a different directory, or not saved yet. If you point me to it, I'll write the tests against the real code.

My plan is a native `terraform test` file, since the repo has no existing test setup. It would use `command = plan` with a mocked AWS provider, so nothing real gets created. The cases would be:
- With `allow_egress = true`, the plan contains exactly one egress rule.
- With `allow_egress = false`, the plan contains no egress rule.
- The default value behaves as your change intends.

I'd also revert the change to confirm the tests fail without it.

I couldn't read the shared `terraform_coding_instructions.md`, because the read permission wasn't granted. I'd need that access to follow the `fmt`, `validate` and `tflint` baseline.
