The module now rejects any `retention_days` outside 1 to 365. I ran the tests and all 7 pass: 6 in `tests/unit` and 1 in `tests/integration`.

- **The rule:** I added a `validation` block to `retention_days` in `variables.tf`. The error message is "retention_days must be between 1 and 365 inclusive."
- **The tests:** the new `tests/unit/retention_days.tftest.hcl` checks that 0, -5 and 366 are rejected and that 1 and 365 are accepted. If someone loosens or removes the validation, those tests fail.
- **Running the tests:** plain `terraform test` found 0 tests, because the files sit in subdirectories rather than directly in `tests/`. To run them, use `terraform test -test-directory=tests/unit` and `terraform test -test-directory=tests/integration`. If CI uses plain `terraform test`, it will skip this rule and the existing tests.

I haven't committed anything.
