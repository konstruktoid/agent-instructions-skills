`retention_days` now rejects anything outside 1 to 365. The new tests and the existing ones all pass.

- **Rule:** I added a `validation` block to `retention_days` in `variables.tf`. It also rejects fractional values like 1.5, which you didn't ask for. If you'd rather allow them, drop the `floor` check.
- **Tests:** The new `tests/unit/retention_days.tftest.hcl` accepts 1 and 365. It expects failures for 0, -5, 366 and 1.5, so loosening the rule later makes a test fail.
- **Results:** The unit directory passes 7 tests and the integration directory passes 1.
- **Running the tests:** A plain `terraform test` reports "0 passed, 0 failed" because it doesn't look in `tests/unit` or `tests/integration`. Run each directory with `terraform test -test-directory=tests/unit` and `terraform test -test-directory=tests/integration`. Without that, nothing enforces the rule, including in CI. You could move the test files up into `tests/` to fix this, but I left the layout alone.

I haven't committed anything.
