`terraform validate` checks a configuration statically. `terraform test` runs the configuration and checks what it actually does.

**`terraform validate`**
- It checks syntax, internal consistency, and types. For example, it catches unknown attributes, references to undeclared variables, and wrong argument types.
- It never contacts providers or remote state, and it creates no resources. It does need `terraform init` first so provider schemas are available.
- It does not evaluate your intent. A configuration can pass validate and still produce the wrong names, counts, or tags.
- It also doesn't know variable values. Beyond type checks, it can't tell whether a `validation` block rejects a bad input.

**`terraform test`**
- It discovers `.tftest.hcl` (and `.tftest.json`) files and runs each `run` block, which is a scenario with its own variable values.
- Each `run` block executes either `plan` (the default) or `apply`. It then evaluates `assert` conditions against real planned or applied values, such as outputs, resource attributes, and counts.
- It can test failure paths. `expect_failures` lets you confirm that a variable validation, precondition, postcondition, or check block rejects bad input.
- With `command = apply`, it creates real infrastructure and destroys it when the test finishes. That requires credentials and can cost money. With `command = plan`, it creates nothing.
- Mocking (`mock_provider`, `override_resource`, and similar) lets you run tests without real infrastructure or credentials.
- Run blocks can share state and chain, so a later block can use the outputs of an earlier one. Tests can also target modules in other directories.

**In practice**
- `validate` is a fast, cheap gate. It suits pre-commit hooks and early CI, and it asks "is this well-formed?"
- `terraform test` is a behavioral check. It asks "does this module do what I intend for these inputs?" It's slower, and it needs credentials unless you mock.
- They complement each other. A common CI order is `fmt -check`, then `validate`, then `test`.
