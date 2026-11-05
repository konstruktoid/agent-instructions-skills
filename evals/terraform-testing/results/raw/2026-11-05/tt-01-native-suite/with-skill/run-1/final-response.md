`retention_days` now has to be between 1 and 365, and a new unit test keeps that rule enforced. `make test` passes with 6 runs and 0 failures, and `terraform fmt -check` is clean. I didn't run `tflint`: it isn't installed here, and the repo has no `.tflint.hcl`. The changes are not committed.

- **The rule:** `variables.tf` has a `validation` block on `retention_days` that accepts 1 through 365 and rejects anything else, with a clear error message.
- **The test:** `tests/unit/retention_days.tftest.hcl` sits next to the existing `name.tftest.hcl` and uses the same native `terraform test` style.
  - **What it checks:** it accepts 1 and 365 and rejects 0, 366 and -5.
  - **No infrastructure:** every run is plan-only, so nothing is created.
- **The test catches a missing rule:** with the validation removed, the unit suite fails at the "zero rejected" run, and the later rejection runs are skipped.
- **Working tree:** no `.terraform` directory, state file or plan file is left behind.

I didn't run the integration suite. The default of 30 is within range, so it isn't affected.
