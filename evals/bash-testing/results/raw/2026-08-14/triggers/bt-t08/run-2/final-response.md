bats-core and shunit2 are both frameworks for testing shell scripts, but they differ in syntax and approach:

**bats-core**
- Tests are written as `.bats` files using a TAP-based syntax: `@test "description" { ... }`
- Assertions typically use plain `[ ]`/`[[ ]]` or the `bats-assert`/`bats-support` helper libraries
- Each test runs in its own subshell/process, so tests are well-isolated from each other
- Produces TAP-compatible output, which integrates well with CI systems
- Actively maintained fork of the original (abandoned) `bats`; has a plugin ecosystem (`bats-file`, `bats-mock`, etc.)
- Requires installing the framework (via package manager, git submodule, or npm)

**shunit2**
- Tests are plain shell functions with an xUnit-style naming convention: `testSomething() { assertEquals ... }`
- Assertions mirror JUnit/xUnit style: `assertEquals`, `assertTrue`, `assertFalse`, etc.
- No subshell isolation by default — tests run in the same shell unless you engineer isolation yourself
- Portable across shells (sh, bash, dash, ksh, zsh), which matters if the scripts under test aren't bash-specific
- Single-file library, easy to vendor directly into a repo without a package manager
- Output is plain text, less CI-friendly than TAP without extra tooling

**When it matters for this repo:** if your scripts are bash-only and you want per-test isolation and TAP output for CI, bats-core is usually the better fit. If you need POSIX `sh` portability or want a zero-dependency single-file test lib, shunit2 fits better.

Since you said no changes yet, I haven't looked at what this repo actually uses — let me know if you want me to check the existing test setup before you decide.
