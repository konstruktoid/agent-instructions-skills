I added the optional audit record, and the new tests pass. I didn't run `tflint` because it isn't installed here.

- **Resource:** `main.tf` now has `terraform_data.audit`. It uses `count = var.enable_audit ? 1 : 0`, so it exists only when `enable_audit` is true. Its `input` is `var.name`. You didn't say what the record should hold, so tell me if you want something else there.
- **Variable:** `enable_audit` in `variables.tf` is a `bool` with default `false`.
- **Output:** `audit_enabled` in `outputs.tf` is `length(terraform_data.audit) > 0`.
- **Tests:** the module had none, so I added `tests/audit.tftest.hcl` using native `terraform test`. It runs in plan mode only, so nothing is created. It covers the default case, where the resource is absent and the output is `false`, and the enabled case, where one instance exists and the output is `true`.

**Verification**
- `terraform fmt -check` and `terraform validate` pass, and `terraform test` shows 2 passed, 0 failed.
- With the conditional temporarily forced to `count = 1`, the default-case test failed, so the test does catch that regression. I then restored the conditional and the tests passed again.
- I removed `.terraform` and the lock file, so the tree contains only the four changed or new source files.
