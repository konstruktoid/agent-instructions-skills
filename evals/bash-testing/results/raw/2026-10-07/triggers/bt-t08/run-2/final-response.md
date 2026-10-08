**bats-core** and **shunit2** are both unit-test frameworks for shell code. They differ mainly in how you write tests.

## bats-core

- **Test syntax:** Tests are written in a Bash-like DSL, with `@test "description" { ... }` blocks. A preprocessor rewrites these into functions, so `.bats` files aren't valid plain Bash.
- **Assertions:** A test fails if any command in it returns non-zero, because bats runs each test with `set -e` semantics. You usually write `[ "$output" = "x" ]` or use helper libraries.
- **`run` helper:** `run cmd` captures `$status`, `$output`, and `$lines` without aborting the test. That makes it easy to assert on failing commands.
- **Isolation:** Each test runs in its own subshell or process. State doesn't leak between tests, and `setup` and `teardown` run around each one. There are also `setup_file` and `teardown_file` hooks.
- **Helper libraries:** The ecosystem includes `bats-assert`, `bats-support`, `bats-file`, and `bats-mock`. They give you `assert_success`, `assert_output`, `assert_file_exists`, and similar.
- **Output and tooling:** It produces TAP output by default. JUnit, pretty, and TAP13 formatters are available. It supports parallel runs (`--jobs`, with GNU parallel), test filtering and tags, and `skip`.
- **Requirements:** Bash only. Test files are run by bats, not sourced.

## shunit2

- **Test syntax:** Tests are plain shell functions named `testSomething`. The test file is a normal shell script that ends by sourcing `shunit2`, and that line runs the tests.
- **Assertions:** There are xUnit-style assertions: `assertEquals`, `assertNotEquals`, `assertTrue`, `assertFalse`, `assertContains`, `assertNull`, and so on. A failing assertion records the failure, and the test function keeps running unless you add a guard.
- **Isolation:** All tests run in the same shell process. Hooks are `setUp`/`tearDown` for each test and `oneTimeSetUp`/`oneTimeTearDown` for the file. Leaked variables or state can affect later tests unless you clean up.
- **Portability:** It targets POSIX `sh` and also works in Bash, ksh, and zsh. That is its main advantage if you need to test non-Bash scripts or run on minimal systems.
- **Output and tooling:** The output is simpler and the plugin ecosystem is smaller. It has no built-in parallelism or TAP-first reporting, and its mocking and file helpers are sparse.
- **Requirements:** It's a single script that you source or vendor into the repo.

## Practical differences

| Aspect | bats-core | shunit2 |
|---|---|---|
| Test file | `.bats` DSL | Plain shell script |
| Style | Command exit status, `run` | xUnit assertions |
| Isolation | Per-test subshell | Shared shell |
| Shell support | Bash | POSIX sh, Bash, ksh, zsh |
| Ecosystem and CI | Larger (helpers, TAP, JUnit, parallel) | Smaller |
| Testing functions in a script | Source the script in `setup` or the test | Source it in the test file |

## When to choose which

- **bats-core:** Good for testing CLI behavior and exit codes, since `run` captures `$status` and `$output`. It's also the more common choice for new Bash projects, and it works well in CI.
- **shunit2:** A better fit if you need POSIX or multi-shell coverage, prefer xUnit-style assertions, or want tests to be ordinary shell with no preprocessor.

If this is for a specific repo, the better choice is usually whichever framework it already uses. When you're ready, I can look at the repo's existing test layout to see what it uses.
