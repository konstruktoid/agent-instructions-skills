bats-core and shunit2 are both Bash unit testing frameworks, but they differ in style and mechanics:

**bats-core**
- Tests are written in `.bats` files using a Bash-derived DSL: `@test "description" { ... }` blocks.
- Each test runs in its own subshell/process, so tests are isolated from each other by default.
- Uses `run` to capture a command's exit status/stdout/stderr into `$status`, `$output`, `$lines`.
- Has a richer ecosystem: `setup`/`teardown`, `setup_file`/`teardown_file`, TAP-compliant output, and helper libraries (`bats-support`, `bats-assert`, `bats-file`) for nicer assertions.
- More actively maintained (bats-core is the community fork of the original bats), broader adoption in modern CI pipelines.

**shunit2**
- Pure POSIX shell library you `source` into a plain shell script; tests are just functions named `test*`.
- Uses xUnit-style assertions: `assertEquals`, `assertTrue`, `fail`, etc.
- No subshell isolation per test by default — tests share the script's environment unless you manage that yourself.
- Portable beyond Bash (works with `dash`, `ksh`, etc.), which matters if the scripts under test must stay POSIX-sh compatible.
- Single-file dependency, minimal footprint, no external runner binary needed beyond sourcing the library.

**Practical differences that usually drive the choice**
- If scripts are Bash-specific and you want isolated tests with good output/tooling, bats-core is the common pick.
- If scripts need to remain POSIX-sh portable, or you want zero external dependencies beyond one sourced file, shunit2 fits better.
- bats-core integrates more naturally with TAP consumers and CI reporting; shunit2's output is simpler/xUnit-style text.

Let me know if you'd like to see which one this repo already uses, or want help picking one for a specific script.
