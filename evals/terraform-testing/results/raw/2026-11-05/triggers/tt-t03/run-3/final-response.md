I couldn't find any Terraform tests in this repo, and there's no `test/` directory. Here's what's actually there:

- **`tests/test_balance.py`** is the only test file. It's a Python test for `src/ledger/balance.py`, so it has nothing to do with Terraform. The tests you don't recognise are probably these.
- **`infra/main.tf`** is the only Terraform. It's a single `aws_security_group.bastion` resource with no module, no `variable` blocks and no `required_version`.
- **No Terraform test framework is present.** There are no `.tftest.hcl` files and no Terratest. The only Go file is `cmd/parser.go`, which isn't a test.
- **CI** is `.github/workflows/deploy.yml`, plus Jenkins and GitLab files. I didn't open them, so I can't say whether they run `terraform validate` or `terraform test`.

So I can't point you to an existing convention for a test of your new module input. `infra/` isn't a module yet, and I can't see your new input anywhere in this checkout. It may be on another branch or not committed yet.

If you add one, I'd suggest this:

- **Framework:** native `terraform test`, with a `.tftest.hcl` file. It needs no extra language or dependency.
- **Version:** this only works if both `required_version` and the Terraform version CI runs are 1.6 or later. If you use `mock_provider`, they need to be 1.7 or later. I haven't checked either.
- **Location:** `infra/tests/<name>.tftest.hcl`, next to the module. Don't put it in the Python `tests/` directory.
- **Run blocks:** use `command = plan`, so nothing is created.
- **Assertions:** cover the failure path as well as the passing one. For a `validation` block, add a run that expects the bad input to fail (`expect_failures`) and one that accepts a good input.

If you tell me which input you added and where it lives, I can write the test. I'd also confirm it fails when the change is reverted.
