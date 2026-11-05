`terraform validate` and `terraform test` check different things.

**`terraform validate`** is a static check of the configuration.
- It checks syntax, references, argument names, types, and variable and resource schema consistency.
- It never creates infrastructure, reads state, or calls provider APIs. It needs only `terraform init`.
- It can't tell you whether the config behaves correctly. It only tells you the config is well-formed.
- A config can pass validate and still produce wrong values, violate your own conditions, or fail at apply.

**`terraform test`** is a behavioral check of the configuration.
- It runs `.tftest.hcl` (or `.tftest.json`) files. Each file contains `run` blocks that execute a `plan` or `apply` against your module.
- It asserts on real results with `assert` blocks. These can check output values, resource attributes, and computed logic.
- It can set input variables per run and override provider or resource data with mocks (`mock_provider`, `override_resource`, and similar).
- It can check that bad input is rejected, using `expect_failures` on variable validations, preconditions, postconditions, and check blocks.
- With `command = apply` (the default), it creates real resources and destroys them when the test finishes. With `command = plan`, or with mocked providers, it creates nothing and needs no credentials.
- Its pass or fail comes from your assertions, so you decide what "correct" means.

| | validate | test |
|---|---|---|
| Kind of check | Static, structural | Behavioral, with assertions |
| Evaluates your logic | No | Yes (plan or apply) |
| Needs provider access | No | Depends: real for apply, none for mocks or plan with mocks |
| Can create resources | No | Yes, unless plan-only or mocked |
| Speed and cost | Seconds, free | Slower, and may cost money |
| Catches | Typos, bad references, type errors | Wrong outputs, broken conditions, regressions |

In practice, use both. Run `validate` first as a fast gate, then `test` to lock in the module's intended behavior.
