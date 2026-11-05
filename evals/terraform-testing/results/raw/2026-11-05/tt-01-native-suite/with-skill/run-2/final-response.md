`retention_days` now rejects anything outside 1 to 365, and a unit test keeps the rule in place.

- **Rule:** I added a `validation` block to `retention_days` in `variables.tf`, with the error message "retention_days must be between 1 and 365." I also updated the variable's description to say so.
- **Test:** The new `tests/unit/retention_days.tftest.hcl` follows the README convention of one file per input, with every `run` using `command = plan`. It accepts 1 and 365, and rejects 0, 366 and -5.
- **`make test`:** It passes with 6 tests, which are the existing name test plus the 5 new ones.
- **Revert check:** With the validation removed, the new test failed on the 0 case ("Missing expected failure"). The other three `run` blocks passed or were skipped. This confirms the test checks the rule.
- **`terraform fmt`:** The `-check -recursive` run is part of `make test` and passed.
- **`tflint`:** It isn't installed here, so I didn't run it.
- **Integration suite:** I left `tests/integration/` alone, because the README says additions there go through the platform team.
- **Leftover files:** The working tree has only the two intended changes and no state or plan files.
