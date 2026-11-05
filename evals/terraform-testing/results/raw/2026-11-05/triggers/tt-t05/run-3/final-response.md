I can't add this test yet, because the repository doesn't contain what your request describes.

- **No Terratest.** There are no `_test.go` files and no `go.mod`. The only Go file is `cmd/parser.go`, and the repo has no `test/` directory.
- **No `retention_days` output.** A search for `retention_days` finds nothing. The only Terraform is `infra/main.tf`, which defines a single `aws_security_group` called `bastion`. It has no outputs, variables, or module structure.
- **Other tests are unrelated.** The only test is `tests/test_balance.py`, a Python test for the ledger code.

I didn't invent a Terratest suite or a stand-in output to test, since either would be a made-up test of something that doesn't exist.

I also couldn't read the skill's tooling baseline file (`terraform_coding_instructions.md`) because the read permission was denied. That means I haven't applied its `fmt`, `validate`, and `tflint` requirements.

Which of these is the situation?
1. Your module is on another branch or in another directory. If so, point me to it, or check out the branch that has the `retention_days` change.
2. The `retention_days` output hasn't been written yet. If so, I can add it, but I'd need to know which resource it should expose. Retention settings usually sit on something like a log group or backup resource.

Once I can see the module and its existing Terratest layout, I'll add the case in the same style, without adding another framework. I'll use `terraform.InitAndPlan` or `terraform.Output` only if the existing tests already apply real infrastructure. I'd rather not run `InitAndApply` without your explicit go-ahead and a safe target.
