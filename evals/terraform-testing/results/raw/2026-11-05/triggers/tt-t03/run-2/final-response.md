Short answer: there's no Terraform test layout in this repo yet, so your new module input has no existing home. The tests you saw aren't Terraform tests.

**What I found**
- `tests/test_balance.py` is the only thing under a test directory. It's a pytest test for a Python `ledger.balance` helper and has nothing to do with Terraform. The directory is `tests/`, not `test/`.
- There are no `.tftest.hcl` files and no Terratest. The only Go file is `cmd/parser.go`, which isn't a test.
- There are no plan-and-policy scripts and no `examples/` roots.
- The only Terraform is `infra/main.tf`, and CI (`.github/workflows/deploy.yml`) doesn't run any Terraform checks.
- The README says this is a mixed sandbox repo used for trigger evals. The Python tests exist to give prompts something to point at.

**Where to put your test**
- With no existing convention, the default is native `terraform test`. Put a `.tftest.hcl` file next to the module, for example `infra/<module>.tftest.hcl`, or under `infra/tests/`. Don't add it to the Python `tests/` directory.
- Use `command = plan` runs, so nothing is created. Assert the new input's effect, and include a case where a bad value is rejected, using `expect_failures` on a `validation` block.
- Native tests need Terraform 1.6 or later (1.7 or later if you use `mock_provider`). I haven't checked `required_version` in `infra/main.tf` or which version CI would use, since CI doesn't run Terraform at all. Check that before committing to this approach.

**What I couldn't do**
- I couldn't read the skill's tooling baseline file (`terraform_coding_instructions.md`) because the read was denied. So I haven't applied its `fmt`/`validate`/`tflint` checks.
- I haven't written or run anything yet.

If you tell me the input's name and what it should do, I can write the test and run it with a revert check.
