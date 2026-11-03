I didn't change anything, because this repository has no prune script.

- **No prune script.** A case-insensitive search for "prune" across the workspace finds nothing. The only shell script is `scripts/backup.sh`, and it doesn't prune anything: it tars `/srv/ledger/data` and copies the archive to `archive.example.internal` with `scp`.
- **No shell tests.** There are no `.bats`, `*_test.sh` or shunit2 files. The only test is `tests/test_balance.py`, which covers Python code and doesn't run any scripts.
- **I can't edit or run anything here.** This session only gives me tools to search and read files. Even with the right script, I couldn't apply the fix, write the test, or run it to show it fails before the fix and passes after.

For when the script turns up, the fix would be a check early in the script:

```bash
if [[ ! -d ${target_dir} ]]; then
  printf 'prune: target directory does not exist: %s\n' "${target_dir}" >&2
  exit 1
fi
```

The test would point the script at a missing path inside a temporary directory. It would check four things: the exit code is non-zero, the error message goes to stderr, nothing is printed to stdout, and nothing else is deleted. A second case would use an existing directory whose name contains a space, to confirm normal pruning still works. Since the repository has no shell test framework, I'd ask before adding bats; otherwise I'd use a plain test script that exits non-zero on failure.

To go ahead, I need:
1. The path to the prune script, or the branch or repository it's in.
2. A session where I can edit files and run commands.

Separately, `backup.sh` has the same kind of problem. It has no `set -e` and its variables aren't quoted, so if `tar` fails it still runs `scp` and exits 0. Do you want that fixed and tested too?
