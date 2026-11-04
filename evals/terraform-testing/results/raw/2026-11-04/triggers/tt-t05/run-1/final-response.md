I didn't add the test, because this workspace doesn't match what you described.

- **No Terratest:** There is no `go.mod` and no `*_test.go` files. Nothing imports `github.com/gruntwork-io/terratest`. The only Go file is `cmd/parser.go`, which isn't a test.
- **No `retention_days` output:** The only Terraform is `infra/main.tf`, which holds one `aws_security_group.bastion` resource. It has no outputs and no variables, and `retention_days` appears nowhere in the repo.
- **No module:** `infra/` is a root config, not a module with a test layout.

The checkout may be on the wrong branch, or the module and its tests may live in a different repo or directory. I also couldn't read the skill's `terraform_coding_instructions.md` baseline, since that path needed a permission I didn't have.

If you point me at the right location, I'll add a Go Terratest case next to the existing ones. It would check that `retention_days` has the expected value, plus a failure-path case. I'd use `terraform.InitAndPlan` or `terraform.Output`, and I wouldn't run `InitAndApply` without your explicit go-ahead, since that creates real infrastructure.

If you want me to start from this repo as it is, tell me the output's intended definition and where it should go. Terratest would then be a new framework here, so I'd confirm that with you first.
