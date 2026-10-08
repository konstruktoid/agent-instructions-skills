`--exclude=PATTERN` now behaves the same as `--exclude PATTERN`.

**Cause:** `bin/mkbackup.sh` only recognised the two-word form. `--exclude=node_modules` fell through to the "unknown long option, skipped" branch. The exclude was dropped without any warning, so everything got archived.

**Fix:** I added a `--exclude=*)` case in `bin/mkbackup.sh` that takes the pattern from after the `=`.

**Regression test:** I added a case to `test/test_mkbackup_basic.sh`. It runs `--exclude=skipme` and checks that `keepme/file.txt` is in the archive and `skipme` is not. `make test` passes with the fix. With the fix stashed, the new test fails with "`--exclude=PATTERN` left excluded directory in the archive", so it catches the bug.

The catch-all that silently skips unknown `--*` options is still there. That is how this bug stayed hidden, but I left it because the comment says older callers depend on it.
