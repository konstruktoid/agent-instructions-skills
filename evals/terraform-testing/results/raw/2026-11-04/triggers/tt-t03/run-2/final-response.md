Your repo doesn't have a Terraform test convention yet, so I can't point you to an existing place for your test.

- **The tests you don't recognise aren't Terraform tests.** There is no `test/` directory. The only test directory is `tests/`, and it holds one file, `tests/test_balance.py`. That's a pytest test for the Python `ledger.balance` helper in `src/ledger/`.
- **No Terraform tests exist anywhere.** I found no `.tftest.hcl` files, no Terratest (the Go files are just `cmd/parser.go`), and no plan-and-policy scripts.
- **The Terraform is minimal.** It's a single file, `infra/main.tf`, with one `aws_security_group` resource. It isn't a module yet: it has no `variable` blocks, no `required_version` and no `terraform` block. I haven't seen your new module input, so it may be uncommitted or live somewhere I haven't looked.
- **CI wiring is unchecked.** I haven't read the CI files (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `Jenkinsfile`), so I don't know whether any of them run `terraform validate` or `plan`.

**Where I'd put it:** native `terraform test` is the usual default when a repo has nothing, because it needs no extra language or dependency. The test would go in `infra/tests/<name>.tftest.hcl`, next to the code it covers. Two conditions apply:

- It needs Terraform 1.6 or later (1.7 or later if you use `mock_provider`).
- Both your `required_version` and the version CI runs must meet that.

I'd use `command = plan` so nothing gets created. The test should cover both a valid value being accepted and an invalid one being rejected, using `expect_failures` if the input has a `validation` block.

I also couldn't read the shared `terraform_coding_instructions.md` baseline for `fmt`, `validate` and `tflint`. That read was blocked by a permissions prompt I couldn't get past, so I haven't applied that baseline.

If you tell me where the new input lives, or share the diff, I can check the Terraform version constraints and write and run the test.
