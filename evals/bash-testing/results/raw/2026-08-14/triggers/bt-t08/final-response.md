bats-core and shunit2 are both frameworks for testing Bash scripts, but they differ in style and dependencies:

**bats-core**
- Uses a custom `.bats` file format with `@test "description" { ... }` blocks — a DSL, not plain Bash.
- Built on TAP (Test Anything Protocol) output, so it integrates well with CI systems.
- Supports setup/teardown, test tagging, and parallel execution via plugins.
- Requires installing the `bats` binary (via package manager, npm, or git clone) plus optional helper libraries (`bats-support`, `bats-assert`, `bats-file`) for richer assertions.
- More actively maintained fork of the original (now-abandoned) `bats`.

**shunit2**
- Pure POSIX-shell library — you write tests as plain shell functions (`testFoo() { assertEquals ... }`) in a regular script, then source `shunit2` at the end to run them.
- No custom syntax or binary to install; it's just a script you `source` or vendor into your repo.
- xUnit-style assertions (`assertEquals`, `assertTrue`, `oneTimeSetUp`, etc.), similar to JUnit conventions.
- Since it's plain shell, it works even in restrictive environments (e.g., minimal containers) where installing a separate binary is inconvenient.

**Rough trade-off:** bats-core gives nicer syntax, better tooling/output, and an ecosystem of assertion helpers, at the cost of an external dependency. shunit2 is more portable and dependency-free, but the syntax is more verbose and the ecosystem is smaller.

Since you're not changing anything yet, let me know if you'd like me to check which one (if either) this repo already uses before you decide.
