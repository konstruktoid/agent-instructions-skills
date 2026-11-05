The module now rejects any `retention_days` outside 1 to 365. A new unit test enforces that rule. `make test` passes with 6 runs, 0 failed, and `terraform fmt -check` is clean.

- **Rule:** I added a `validation` block to `retention_days` in `variables.tf`. It requires a value from 1 to 365 inclusive, with the error message "retention_days must be between 1 and 365 inclusive."
- **Test:** `tests/unit/retention_days.tftest.hcl` follows the README convention of one unit-test file per input, with every run set to `command = plan`. It accepts 1 and 365 and rejects 0, 366 and -5.
- **Check that the test bites:** With the validation block reverted, the test fails ("Missing expected failure" on the zero case, the other two rejection cases skipped). So it does catch removal of the rule.
- **Integration tests:** I didn't touch `tests/integration/`. The README says only the platform team adds to it, and the new test doesn't need `apply`.
- **Not run:** I didn't run `tflint`, because the repo has no `.tflint.hcl`. I also didn't run `terraform validate` separately, but `make test` runs `terraform init` and the plan-based test runs.
- **Working tree:** It is clean apart from the two intended changes, with no state files or `.terraform/` left behind. Nothing is committed.
