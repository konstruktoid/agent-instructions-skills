`--exclude=node_modules` now behaves the same as `--exclude node_modules`. `make test` passes with the fix.

**Cause:** the option parser in `bin/mkbackup.sh` only matched the exact string `--exclude`. `--exclude=...` fell into the catch-all `--*` branch, which skips unknown long options, so the exclusion was dropped without any message.

**Fix:** I added an `--exclude=*` case that takes the value after the `=`.

**Regression test:** the new `test/test_mkbackup_exclude.sh` builds an archive with each spelling. It checks that `keepme/` is kept and `skipme/` is left out. I stashed the fix and reran the suite to confirm the test catches the bug. The `--exclude=skipme` case failed, and the separate-argument case passed.

The catch-all that silently skips unknown `--*` options is still there. I left it because its comment says it keeps older callers working. It is also how this bug stayed hidden, so you may want it to warn on stderr.
