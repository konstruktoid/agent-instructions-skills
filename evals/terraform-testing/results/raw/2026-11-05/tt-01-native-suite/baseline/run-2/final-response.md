`retention_days` now rejects anything outside 1 to 365, and new tests check that the rule holds. All tests pass: 6 in `tests/unit` and 1 in `tests/integration`.

- **Rule:** I added a `validation` block to the variable in `variables.tf`. The error message is "retention_days must be between 1 and 365 inclusive."
- **Tests:** The new file `tests/unit/retention_days.tftest.hcl` checks that 0, -5 and 366 are rejected and that 1 and 365 are accepted. If someone loosens or removes the rule, those tests fail.
- **Running the tests:** A plain `terraform test` found 0 tests, because it only looks directly in `tests/` and not in subdirectories. I ran them with `terraform test -test-directory=tests/unit` and `-test-directory=tests/integration`. Any CI that runs plain `terraform test` won't run these tests, so it needs those flags, or the test files need moving into `tests/`.
- **Formatting:** `terraform fmt` reformatted the new test file. I didn't commit anything.
