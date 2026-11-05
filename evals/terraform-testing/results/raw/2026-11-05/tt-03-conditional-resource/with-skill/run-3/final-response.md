I added the optional audit record, the `audit_enabled` output, and a test for both. `terraform test` passes (2 runs, both plan-only), and `terraform fmt -check` and `terraform validate` are clean. `tflint` isn't installed here, so I didn't run it.

- **`variables.tf`:** new `enable_audit` boolean, default `false`.
- **`main.tf`:** `terraform_data.audit` uses `count = var.enable_audit ? 1 : 0` and takes `var.name` as its input.
- **`outputs.tf`:** `audit_enabled` is `length(terraform_data.audit) > 0`.
- **`tests/audit.tftest.hcl`:** a new test file. The repo had no tests, so I used native `terraform test`, which fits `required_version >= 1.7.0` and the Terraform 1.17.1 installed here. One run checks the default creates no record and `audit_enabled` is false. The other sets `enable_audit = true` and checks one record exists and `audit_enabled` is true.

To confirm the test checks what it claims, I temporarily forced `count = 1`. The default-case run then failed, as it should. I restored the original line and the suite passed again.

I removed `.terraform` and the lock file afterwards, so the working tree only has the three edited files and `tests/`. Nothing is committed.
