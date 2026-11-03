Both are unit-testing frameworks for shell scripts. They differ in how you write tests, which shells they support, and how much tooling comes with them.

## bats-core (Bash Automated Testing System)

- **Syntax:** It adds its own syntax on top of Bash. Test files (`*.bats`) contain `@test "description" { ... }` blocks, and bats rewrites them into Bash functions before running them.
- **Shell:** Bash only. Tests run under Bash, though they can call scripts written for any shell.
- **Assertions:** Any command that exits non-zero fails the test, so plain `[ "$x" = y ]` works. The helper libraries `bats-support`, `bats-assert` and `bats-file` add `assert_success`, `assert_output --partial`, `assert_file_exists` and similar.
- **The `run` helper:** `run cmd` captures `$status`, `$output` and `${lines[@]}` without stopping the test. This makes it easy to check exit codes and output.
- **Isolation:** Each test runs in its own subshell. It has `setup` / `teardown` and `setup_file` / `teardown_file` hooks, plus temp directories like `$BATS_TEST_TMPDIR`.
- **Output and tooling:** TAP output, JUnit output via `--formatter junit`, parallel runs with `--jobs` (needs GNU parallel), filtering by name or tag, and `skip`.
- **Ecosystem:** Actively maintained, common in CI, and available as a GitHub Action and a Docker image.

```bash
@test "fails on missing arg" {
  run ./myscript.sh
  [ "$status" -eq 2 ]
  [[ "$output" == *"usage"* ]]
}
```

## shunit2

- **Syntax:** Plain shell, modeled on xUnit/JUnit. You define functions named `test*`, then source `shunit2` at the end of the file. It finds and runs those functions itself.
- **Shell:** POSIX-portable. It runs under `sh`, dash, ksh, zsh and Bash, so you can test code under the shell it will actually run in.
- **Assertions:** Built in: `assertEquals`, `assertTrue`, `assertNull`, `assertContains`, `fail` and others, with an optional message as the first argument. A failed assertion does **not** stop the test unless you add something like `|| return`.
- **Exit codes and output:** No `run` equivalent. You capture them yourself, for example `out=$(cmd 2>&1); rc=$?`.
- **Isolation:** Tests run in the same shell process, not separate subshells, so global state can leak between tests. Hooks are `oneTimeSetUp`, `oneTimeTearDown`, `setUp` and `tearDown`. `SHUNIT_TMPDIR` gives you a temp directory.
- **Output and tooling:** Simple text output, with JUnit XML only through community add-ons. No built-in parallelism or filtering beyond running a subset of functions.
- **Dependencies:** One file you can vendor into the repo with no dependencies. Releases are slower than bats-core's, but it is stable.

```sh
testFailsOnMissingArg() {
  out=$(./myscript.sh 2>&1); rc=$?
  assertEquals 2 "$rc"
  assertContains "$out" "usage"
}
. shunit2
```

## Choosing between them

| Concern | bats-core | shunit2 |
|---|---|---|
| Target shell is Bash | ✅ natural fit | works |
| Must test under POSIX sh, dash or ksh | ❌ | ✅ |
| Checking exit codes and output | `run` makes it easy | manual capture |
| Isolation between tests | subshell per test | shared process |
| CI reports and parallel runs | built in | limited |
| Zero dependencies, vendor one file | core plus helper libraries | ✅ single file |

**In short:** bats-core is the more common choice for testing Bash scripts and CLIs, because of the `run` helper, per-test isolation and better CI tooling. shunit2 is the better pick when portability across POSIX shells matters, or when you want one plain-shell file with no extra syntax.

If you later want tests added to this repo, the usual approach is to match whatever framework it already uses rather than bring in a second one. I haven't looked at the repo yet; I can check which one it uses when you're ready.
