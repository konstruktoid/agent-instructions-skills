`terraform validate` and `terraform test` check different things.

**`terraform validate`** is a static check of your configuration.
- It checks syntax, references between resources, and whether argument names and types match the provider and module schemas.
- It makes no remote calls and creates no infrastructure. It doesn't read state or evaluate real values, so it can't tell you what the configuration will do.
- It can only catch things like a misspelled attribute, a missing required argument, or a reference to an undeclared variable.

**`terraform test`** is a behavioral check. It runs your configuration and asserts on the results.
- It executes `.tftest.hcl` (or `.tftest.json`) files made up of `run` blocks. Each block does a `plan` or an `apply` of the module, with variables you set for that scenario.
- `assert` blocks check conditions on the resulting values: outputs, resource attributes, and computed expressions.
- `expect_failures` lets you confirm that a variable `validation`, `precondition`, or `postcondition` rejects bad input. This verifies that your guardrails work.
- By default, `command = apply` creates real resources in a temporary state and destroys them when the test ends. `command = plan` avoids creating anything. Since Terraform 1.7, `mock_provider` and `override_*` blocks let you run tests without real credentials or infrastructure.
- Multiple `run` blocks run in sequence and share state, so you can test multi-step scenarios such as create, then update.

**In practice**
- `validate` answers "Is this configuration well-formed?" It's fast and free, and it fits in pre-commit hooks and early CI.
- `test` answers "Does this module behave as intended?" It is slower, and it may need provider credentials unless you mock the providers.
- Passing `validate` says nothing about whether outputs are correct, whether defaults are sensible, or whether input validation rejects what it should. Those are the gaps `terraform test` covers.
- Most pipelines run both: `terraform fmt -check`, then `validate`, then `test`.
