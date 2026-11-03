`--exclude=node_modules` now behaves the same as `--exclude node_modules`. I haven't committed anything.

**Cause:** `bin/mkbackup.sh` only matched the exact string `--exclude`. The `--exclude=PATTERN` form fell into the `--*)` branch, which skips unknown long options. So the exclude was dropped without any warning and everything was archived.

**Fix:** I added a `--exclude=*)` case in `bin/mkbackup.sh` that sets the pattern from `${1#--exclude=}`. The existing catch-all for unknown options is unchanged.

**Regression test:** I added a case to `test/test_mkbackup_basic.sh`. It runs `--exclude=skipme` and checks that `skipme` is absent from the archive and `keepme/file.txt` is still there. `make test` passes with the fix. With the fix stashed, the new test fails with "--exclude=PATTERN did not exclude the directory", so it does catch the bug.

I didn't touch the catch-all that silently skips unknown `--` options. That is how this bug stayed hidden, but the script comment says it is deliberate for older callers.
