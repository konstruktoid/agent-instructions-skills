`--exclude=PATTERN` now behaves the same as `--exclude PATTERN`. `make test` passes with the fix.

**Cause:** `bin/mkbackup.sh` only matched the exact string `--exclude`. `--exclude=node_modules` fell into the catch-all `--*)` branch, which skips unknown long options. The exclude pattern was dropped without any error, so everything got archived.

**Fix:** I added an `--exclude=*)` case in `bin/mkbackup.sh` that sets `exclude="${1#--exclude=}"`.

**Regression test:** `test/test_mkbackup_exclude.sh` builds a small tree and archives it once with each spelling. For both, it checks that `keepme/file.txt` is in the archive and that nothing from `skipme` is. `make test` picks it up automatically. With the `bin/` change stashed, the test fails with `--exclude (equals) left skipme in the archive`; with the fix it passes.

I left the silent skipping of unknown options alone because the script comments say it's there for older callers. It is also how this bug stayed hidden, so you may want it to warn on stderr instead.
