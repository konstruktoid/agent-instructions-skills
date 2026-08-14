## bats-core

- **Style**: Custom `.bats` file syntax with `@test "description" { ... }` blocks — not plain shell, needs the `bats` interpreter to run.
- **Isolation**: Each test runs in its own subshell, so state doesn't leak between tests by default.
- **Ecosystem**: Rich helper libraries — `bats-support`, `bats-assert`, `bats-file` — for assertions, mocking file state, etc.
- **Output**: TAP-compliant, integrates well with CI systems that parse TAP.
- **Shell support**: Bash-specific (leans on bash features like arrays, `[[ ]]`).
- **Install**: Via package manager, npm, brew, or vendored as a git submodule.

## shunit2

- **Style**: Plain shell script — you write regular `sh`/`bash` functions named `testXxx()` and source `shunit2` at the end. No special file format or separate interpreter needed.
- **Isolation**: All tests run in the same shell process (with `setUp`/`tearDown` hooks between them), so isolation is weaker than bats-core's subshell model.
- **Ecosystem**: Minimal — just xUnit-style `assertEquals`, `assertTrue`, etc. No plugin ecosystem to speak of.
- **Output**: Simple pass/fail text, not TAP by default.
- **Shell support**: POSIX-portable — works under `sh`, `dash`, `ksh`, `zsh`, not just bash, which matters if scripts need to run on minimal/non-bash shells.
- **Install**: Single script, easy to vendor directly in-repo with no dependency manager.

## When each tends to win

- **bats-core**: better fit for bash-specific scripts, CI-heavy projects wanting TAP output, and teams that want richer assertion/mocking helpers.
- **shunit2**: better fit when scripts must stay POSIX-portable across shells, or when you want zero external tooling — just a shell script.

If you want, I can check whether this repo already leans toward one of these (e.g., via existing test files or CI config) before you decide anything.
