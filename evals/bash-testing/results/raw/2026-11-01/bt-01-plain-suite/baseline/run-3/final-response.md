`--exclude=PATTERN` now behaves the same as `--exclude PATTERN`. `make test` passes with the fix, and the new test fails against the old script.

**Cause:** `bin/mkbackup.sh` only matched the exact word `--exclude`. A `--exclude=node_modules` argument fell into the `--*` catch-all, which skips unknown long options without a warning, so nothing was excluded.

**Changes:**
- **`bin/mkbackup.sh`:** I added an `--exclude=*` case that takes the value after the `=`. I also made a bare trailing `--exclude` with no value print the usage message and exit 64. Before, it silently used an empty pattern.
- **`test/test_mkbackup_exclude.sh`** (new): it builds an archive with each spelling and checks that `skipme` is left out and `keepme` is kept. It also checks the exit-64 case. `make test` picks it up automatically.

The catch-all that silently ignores unknown options is still there, because the script keeps it on purpose for older callers. A misspelled option will still be ignored without an error.
