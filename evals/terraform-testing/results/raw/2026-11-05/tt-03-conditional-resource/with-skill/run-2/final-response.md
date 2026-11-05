I added the optional audit record, and the new tests pass: `terraform test` reports 2 passed, 0 failed.

- **Resource:** `terraform_data.audit` in `main.tf` uses `count = var.enable_audit ? 1 : 0`, so it is only created when the flag is true. I set its `input` to `var.name`, matching the existing `service` resource. Because of `count`, you refer to it as `terraform_data.audit[0]`.
- **Variable:** `enable_audit` in `variables.tf` is a `bool` with default `false`.
- **Output:** `audit_enabled` in `outputs.tf` is `length(terraform_data.audit) > 0`.
- **Tests:** the repo had none, and `required_version` is `>= 1.7.0`, so I added `tests/audit.tftest.hcl` using native `terraform test`. Both runs are plan-only, so nothing is created. One run checks the default (no resource, `audit_enabled` is false). The other sets `enable_audit = true` (one resource, `audit_enabled` is true).

I also ran the other checks:
- `terraform fmt -check` and `terraform validate` are clean.
- With the condition reverted to always create the resource, the default-case test fails as it should. I then restored the condition and the tests passed again.
- I removed `.terraform/` and the lock file afterwards. The working tree now holds only the three edited files and `tests/`.

I didn't run `tflint` because it isn't installed here. I didn't commit anything.
