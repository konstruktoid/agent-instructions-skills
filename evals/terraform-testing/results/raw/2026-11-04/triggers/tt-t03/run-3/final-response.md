The tests you don't recognise aren't Terraform tests, and the repo has no Terraform test setup yet.

- **No `test/` directory.** The only test directory is `tests/`, and it holds one file, `tests/test_balance.py`. That's a pytest test for a Python `ledger.balance` helper, so it has nothing to do with your module.
- **No Terraform testing found.** I searched the whole repo and found no `.tftest.hcl` files, no Terratest (the only Go file is `cmd/parser.go`), no plan-and-policy scripts, no `examples/` roots, and no Terraform step in CI. The only workflow is `.github/workflows/deploy.yml`, which just echoes the PR title.
- **No module yet.** `infra/main.tf` is a single `aws_security_group` with no variables, and there's no `required_version` or provider pin. I couldn't find your new module input here, so it may be on another branch or not committed.

**Where to put the test:** since nothing exists to match, use native `terraform test`. Put a `.tftest.hcl` file in the module's own directory, either beside the `.tf` files or in a `tests/` folder inside the module. For example: `infra/tests/<input_name>.tftest.hcl` for a module in `infra/`. Don't put it in the top-level `tests/` folder, which belongs to the Python package.

**What to assert:**
- Use `command = plan` so nothing real is created. Add a `mock_provider` block if you don't want to need AWS credentials.
- Add one `run` block that passes a good value and checks the attribute or output the input drives.
- Add one `run` block that passes a bad value and uses `expect_failures = [var.<name>]`, if the input has a `validation` block.

**Version check:** native tests need Terraform 1.6 or later, and `mock_provider` needs 1.7 or later. Nothing pins a version today. Set `required_version` in the module first, and make sure the version CI uses is at least that.

Separately, `deploy.yml` has `permissions: write-all` and puts the PR title straight into a `run:` step. That's a script-injection risk. It's outside what you asked, so I haven't touched it.

If you tell me which branch or path has the module, I can write the test, run `terraform test`, and confirm it fails with the change reverted.
