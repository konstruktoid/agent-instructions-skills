I added the optional audit record. `terraform fmt -check` and `terraform validate` both pass. I didn't run a plan or apply, so I haven't checked the resource count with `enable_audit` set to true or false.

- **`variables.tf`:** new `enable_audit` boolean, default `false`.
- **`main.tf`:** new `terraform_data.audit` with `count = var.enable_audit ? 1 : 0`. Its `input` is `var.name`, the same as the `service` resource. You didn't say what the record should hold, so change that if you want something else.
- **`outputs.tf`:** new `audit_enabled` output, set to `length(terraform_data.audit) > 0`. It is `true` only when the resource was created.

The changes are uncommitted in the working tree.
