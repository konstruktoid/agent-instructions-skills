bats-core and shunit2 both test shell scripts, but they work differently.

## bats-core (Bash Automated Testing System)

- **Its own file format.** Tests live in `.bats` files and use a special `@test "description" { ... }` block. bats preprocesses these into Bash before running them, so a `.bats` file is not plain Bash.
- **Bash only.** It needs Bash 3.2 or newer and can't test POSIX `sh`, dash or ksh behaviour directly.
- **The `run` helper.** `run my_command args` captures `$status`, `$output` and the `${lines[@]}` array, so you can check the exit code and output without `set -e` stopping the test.
- **Assertions:**
  - Core bats uses plain `[ ... ]` / `[[ ... ]]` tests. Any command that fails fails the test.
  - Richer assertions like `assert_success`, `assert_output --partial` and `assert_line` come from the separate `bats-assert`, `bats-support` and `bats-file` libraries, loaded with `load`.
- **Isolation.** Each `@test` runs in its own subshell, so state doesn't leak between tests. It has `setup`/`teardown` per test and `setup_file`/`teardown_file` per file.
- **Tooling:**
  - Output is TAP by default, with pretty and JUnit formatters.
  - `--filter` selects tests by name, `--jobs` runs them in parallel (needs GNU parallel), and `skip` skips a test.
  - It has helpers like `$BATS_TEST_TMPDIR`.
- **Ecosystem.** It's actively maintained and is the de facto standard in many modern projects, often added as a git submodule or installed from a package manager.

## shunit2

- **Plain shell.** It follows the xUnit style and is a single sourced file. Tests are ordinary functions whose names start with `test`, and the file ends with `. shunit2`. The test file is a valid shell script that you run directly.
- **Portable.** It works under POSIX `sh`, dash, Bash, ksh and zsh, so it suits scripts that have to run under `/bin/sh`.
- **Built-in assertions.** `assertEquals`, `assertTrue`, `assertNull`, `assertContains` and `fail` are included. The optional first argument is a message, and the argument order is *expected, actual*.
- **Fixtures.** It has `oneTimeSetUp`/`oneTimeTearDown` and `setUp`/`tearDown`.
- **Less isolation.** Tests run in the same shell process, so global variables, `cd` and traps can leak between tests unless you reset them yourself.
- **Capturing results.** There's no `run` equivalent. You capture output and status yourself, e.g. `out=$(cmd); rc=$?`, and need to be careful with `set -e`.
- **Simpler tooling.** Output is plain text, with no TAP or parallel runs. Development is slower, but it's stable and has no dependencies.

## Rule of thumb

| Choose | When |
|---|---|
| **bats-core** | Bash scripts, you want readable tests, `run`-style capture, TAP/JUnit for CI, or per-test isolation |
| **shunit2** | Portable `sh` scripts, multiple shells to test, a single dependency-free file, or a familiar xUnit style |

In practice, the best choice in an existing repo is whichever framework it already uses. Switching or mixing frameworks usually costs more than any difference between them. When you're ready to add tests, I can check which framework (if any) this repo uses.
