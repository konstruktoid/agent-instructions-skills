I couldn't add the test, because the repo doesn't match what you described.

- **No `retention_days` output.** `infra/main.tf` has one resource, an `aws_security_group` named `bastion`. It has no outputs, variables, or retention setting.
- **No Terratest.** There's no `test/` directory, no `_test.go` file, and no `go.mod`. The only Go file is `cmd/parser.go`, and the only Terraform tests anywhere are none. The one test file, `tests/test_balance.py`, is Python and covers the ledger code.
- **Possible wrong checkout.** The module with the Terratest suite may be in another repo or on another branch. The change adding `retention_days` may also not be committed yet.

I also couldn't read the skill's tooling baseline file (`terraform_coding_instructions.md`). The read permission was denied. I haven't relied on it, but the `fmt`, `validate` and `tflint` checks it defines haven't been applied.

If I wrote a Terratest case now, I'd be inventing the module path, the output's type and the existing test helpers. It would also bring in a Go test setup this repo doesn't have, which is the opposite of matching what you already use.

Could you tell me where the module and its Terratest files are, or point me at the branch with the `retention_days` change? Once I can see them, I'll add the case in the same style. It will use `terraform.InitAndPlan` or the existing helper, so nothing gets applied without your approval. I'll also confirm that it fails with the output removed.
