`terraform validate` and `terraform test` check different things.

**`terraform validate`** is a static check.
- It looks at the configuration only. It checks syntax, references between resources, variable and output types, and whether the arguments match the provider schemas.
- It doesn't create infrastructure, read state, or contact remote APIs. It needs `terraform init` first so the provider schemas are available.
- It can tell you the configuration is well-formed. It can't tell you the configuration does what you want.

**`terraform test`** is a behavioral check.
- It runs `.tftest.hcl` (or `.tftest.json`) files. Each file has one or more `run` blocks, and each block executes a `plan` or an `apply` against your configuration.
- Each `run` block can have `assert` blocks. These check conditions on resource attributes, outputs, and computed values after the plan or apply.
- It can check that a `variable` validation rejects bad input. A `run` block with `expect_failures` does this.
- It can override variables per run and mock providers (`mock_provider`, `override_resource`). That lets you test logic without real credentials or cloud resources.
- In `apply` mode (the default) it creates real resources, then destroys them when the test ends. In `plan` mode, or with mocked providers, nothing real is created.
- It can also test module outputs, `for_each` and `count` logic, conditionals, and `locals`. `validate` can't evaluate any of these with real values.

**Key differences**

| | `validate` | `test` |
|---|---|---|
| Kind of check | Static, structural | Dynamic, behavioral |
| Evaluates real values | No | Yes |
| Needs credentials or APIs | No | Yes, unless mocked or plan-only |
| Can create resources | No | Yes, in apply mode |
| Verifies your intent | No | Yes, through assertions |
| Cost and speed | Fast and free | Slower, and may cost money |

In practice, run `validate` first because it's cheap and catches typos and schema errors. Use `terraform test` to lock in behavior, such as "this input is rejected" or "this output equals X".
