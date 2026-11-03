`--exclude=node_modules` now behaves the same as `--exclude node_modules`. `make test` passes, and `bash -n` and `shellcheck` are clean on the script and all test files.

**Cause:** `bin/mkbackup.sh` only recognised `--exclude` as a separate word. `--exclude=PATTERN` fell into the catch-all `--*)` branch, which skips unknown long options so older callers keep working. The pattern was dropped and everything was archived.

**Fix:** I added an `--exclude=*)` case in `bin/mkbackup.sh` that takes the pattern from `${1#--exclude=}`.

**Regression test:** `test/test_mkbackup_exclude.sh` follows the existing plain-script style, so `make test` picks it up. It covers:
- **Both spellings:** it checks that `skipme` is left out and `keepme/file.txt` is kept, using a source path with a space in it.
- **Empty value:** `--exclude=` excludes nothing and still exits 0.

I ran it before the fix and it failed on the `=` form (`equals-value: excluded directory is present in the archive`). After the fix it passes.

I left one thing alone: `--exclude` as the last argument with no value still hits `shift 2` and fails under `set -e`. That was already the case and is outside this bug.
