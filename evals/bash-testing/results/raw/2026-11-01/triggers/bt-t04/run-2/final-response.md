I didn't change anything, because I couldn't find a prune script in this workspace.

- **No match:** a case-insensitive search for "prune" across the workspace found nothing.
- **Only shell script:** `scripts/backup.sh` is a nightly tar-and-`scp` backup. It doesn't delete old files or take a target-directory argument, so it isn't the prune script.
- **No shell tests:** the only test file is `tests/test_balance.py`, a pytest test for the ledger code.
- **No edit tools:** I can read and search files here but can't write files or run commands. Even with the right script I couldn't apply the fix or run the tests.

The prune script may be in another repository or on a branch that isn't checked out (this workspace is on a detached HEAD). Could you tell me where it is, or paste it? Once I can see it, the fix and test would be:

1. **The fix:** check for the directory before pruning. If it's missing, print an error to stderr and exit non-zero, e.g. `[[ -d $dir ]] || { printf 'prune: %s: no such directory\n' "$dir" >&2; exit 1; }`.
2. **The test:** add it to whatever test setup the script's repo already uses (bats, shunit2, or pytest calling the script). It should check that a missing directory gives a non-zero exit and an error on stderr. It should also check that an existing scratch directory with a space in its name is still pruned correctly. Before keeping the fix, I'd confirm the test fails against the current code.

Separately, the bash-testing skill's example guard that lets a script be loaded by a test without running it is wrong: it reads `if [[ ${BASH_SOURCE[0]} == "The" ]]`. It should be `if [[ ${BASH_SOURCE[0]} == "$0" ]]; then main "$@"; fi`. As written, `main` would never run.
