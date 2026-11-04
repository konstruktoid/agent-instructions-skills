I didn't add the test, because I couldn't find what you described in this repository.

- **No Terratest.** There are no Go test files and no `go.mod`. The only Go file is `cmd/parser.go`, and nothing in the repo mentions `terratest`. The only test file is `tests/test_balance.py`, which is Python for the ledger code.
- **No `retention_days` output.** The string doesn't appear anywhere. `infra/main.tf` is a single `aws_security_group.bastion` resource with no outputs, variables, or `retention_days` setting.
- **Possible cause.** The module and its tests may be on another branch, in another checkout, or not committed yet. The working tree's only change is an untracked directory.

I also couldn't read the skill's `terraform_coding_instructions.md`, because the read permission wasn't granted. I haven't applied its `fmt`, `validate` and `tflint` baseline. I'd want that before finishing.

I'd rather not write a Terratest case against an output I can't see. I'd be guessing the module path, the output's type and what it should equal.

Could you point me to the right branch or path, or give me the module's `retention_days` definition and an existing Terratest file to follow? Once I have those, I'll add the case in the same style. It would be plan-only (`terraform.InitAndPlan` plus `terraform.Output`), so it creates no infrastructure. It would cover a passing value and a bad-input case if there's a validation block. I'd then run it with `go test` under a timeout and confirm it fails with the output reverted.
