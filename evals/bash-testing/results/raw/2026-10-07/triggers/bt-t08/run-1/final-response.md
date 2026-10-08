# bats-core vs. shunit2

Both test Bash code. They differ in style, tooling, and how much they assume about your scripts.

| | **bats-core** | **shunit2** |
|---|---|---|
| **Test format** | Its own `.bats` syntax: `@test "name" { ... }`. A preprocessor rewrites it into Bash functions. | Plain shell. Tests are functions named `test_*` in an ordinary `.sh` file. |
| **How you run it** | Through the `bats` executable: `bats tests/`. | You source `shunit2` at the bottom of your test file and run the file itself. |
| **Assertions** | Mostly plain shell. A test fails if any command returns non-zero (it runs with `set -e`-like behavior). The `run` helper captures `$status`, `$output`, and `$lines`. Richer assertions such as `assert_output` and `assert_success` come from the add-on libraries bats-assert, bats-support, and bats-file. | Built in: `assertEquals`, `assertNull`, `assertContains`, `assertTrue`, and so on. |
| **Setup and teardown** | `setup`, `teardown`, `setup_file`, `teardown_file`, `setup_suite`. | `setUp`, `tearDown`, `oneTimeSetUp`, `oneTimeTearDown`. |
| **Output** | TAP by default, with pretty, JUnit, and TAP13 formatters. This suits CI. | Simple text output that lists the assertions that failed. |
| **Parallelism** | Built in, via `--jobs` (needs GNU parallel or a compatible tool). | None built in. |
| **Isolation** | Each test runs in its own subshell or process, so state doesn't leak between tests. | Tests run in the same shell process, so state can leak unless you reset it. |
| **Test selection** | Filter by name (`--filter`) or tag (`--filter-tags`). | Limited. You can pick a function through the suite setup, but there are no tags. |
| **Skipping** | `skip "reason"`. | `startSkipping`, or `assertSkip`-style helpers. |
| **Shell support** | Bash only. | Bourne shell, Bash, dash, ksh, and zsh. |
| **Ecosystem** | Larger and more active, with many helper libraries and wide CI adoption. | Smaller and stable, with little ongoing change. |

## Practical differences

- **bats-core** is usually the default pick for Bash projects. Its tests read clearly, `run` makes it easy to check exit codes and output, and test isolation and CI reporting are good. The costs are a custom syntax and an extra dependency, and assertion helpers need separate installs.
- **shunit2** fits when you need portability across POSIX shells, such as testing `sh` or `dash` scripts. It also fits when you want xUnit-style assertions in plain shell files with no preprocessing step. The cost is weaker isolation, so a test that changes variables or `cd`s can affect later tests. It also has fewer modern conveniences such as parallel runs and filtering.

## Shared pitfalls

- To unit-test functions, both need the script to be sourceable without side effects. The usual pattern is `main "$@"` behind a guard like `[[ ${BASH_SOURCE[0]} == "$0" ]]`.
- For commands that hit the system, you'll want to stub or mock them (via `PATH` overrides or function overrides) in either framework.

Before choosing, check what the repo already uses, because matching an existing framework is usually better than adding a second one. I haven't looked at this repo, and I can do that when you're ready to move forward.
