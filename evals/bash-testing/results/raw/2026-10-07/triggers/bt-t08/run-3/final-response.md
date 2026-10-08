**bats-core** and **shunit2** both test Bash code, but they differ in how you write tests and how much tooling they bring.

| | bats-core | shunit2 |
|---|---|---|
| **Test format** | Its own `.bats` syntax: `@test "name" { ... }`. A preprocessor turns this into Bash. | Plain Bash functions named `test*`, in an ordinary `.sh` file. |
| **Running** | You run the `bats` executable on files or directories. | The test file sources `shunit2` as its last line, so the file runs itself. |
| **Assertions** | `run cmd` captures `$status`, `$output` and `$lines`. You then use plain `[ ... ]` checks or the helper libraries `bats-assert`, `bats-support` and `bats-file`. | Built-in `assertEquals`, `assertNull`, `assertTrue` and similar. |
| **Setup and teardown** | `setup` and `teardown` run per test. `setup_file` and `teardown_file` run per file. | `setUp` and `tearDown` run per test. `oneTimeSetUp` and `oneTimeTearDown` run per file. |
| **Isolation** | Each test runs in its own subshell. Failures are caught through Bash's `errexit` behavior. | Tests run in the same shell process, so state can leak between tests unless you reset it. |
| **Output** | TAP, plus pretty, JUnit and other formatters. It supports parallel runs, tags and filtering. | Simple text output, with no built-in parallelism or rich formatters. |
| **Shell support** | Bash only. | POSIX sh, Bash, ksh and zsh. |
| **Maintenance** | Actively maintained (bats-core is the community fork of the original Bats). | Stable and mature, with slower development. |

**Choosing between them**
- **bats-core** suits most modern Bash projects. It is good at testing a script as a black box (exit code, stdout, stderr). It also has the larger ecosystem and better CI integration, including TAP and JUnit output and parallel runs.
- **shunit2** fits xUnit-style unit tests and code that must stay portable across shells such as `sh`, `dash` or `ksh`. It needs no preprocessor, so it is easy to vendor as a single file.

**Practical gotchas**
- With bats, `run` executes in a subshell. Variables set by the function under test won't be visible afterward. If you need them, call the function directly instead of through `run`.
- With shunit2, a script that calls `exit` or changes shell options can break the test run, because tests share one shell. You often need to wrap the call in a subshell.
- With either one, the script must be sourceable without side effects, so its logic should live in functions and the entry point should sit behind a `main` guard.

If you later want to add tests to a specific repo, the usual rule is to use whatever framework it already has. Otherwise bats-core is the default I'd pick.
