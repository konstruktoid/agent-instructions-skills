I can't add the test yet. This repository has no Terratest suite and no `retention_days` output.

- **Terraform:** the only Terraform file is `infra/main.tf`. It holds one `aws_security_group` resource and has no outputs or variables.
- **`retention_days`:** nothing in the repo mentions it, so the change you describe isn't on this branch.
- **Go:** the only Go file is `cmd/parser.go`. There is no `test/` directory, no `_test.go` file and no `go.mod`. Nothing imports `github.com/gruntwork-io/terratest`.
- **Other tests:** the only tests are Python ones, `tests/test_balance.py`.

Your module and its Terratest suite may be in another directory, repo or branch. The working tree also shows an untracked `../../../../`, so I may be in the wrong place.

I also couldn't read the skill's tooling baseline, `instructions/terraform_coding_instructions.md`, because the read wasn't permitted. I haven't applied the `fmt`/`validate`/`tflint` baseline.

What I need from you:
1. The path to the module and its Terratest files, or the branch that has the `retention_days` output.
2. Permission to read that instructions file, if you want me to follow the baseline.

Once I can see the existing tests, I'll add a Go test for `retention_days` in the same style. It will check the output's value and a failure case. I'll use `terraform.InitAndPlan`-style helpers unless you approve an apply against a non-production target. If the suite uses `InitAndApply`, I'll match it and add a deferred `Destroy`, but I won't run it without your approval.
