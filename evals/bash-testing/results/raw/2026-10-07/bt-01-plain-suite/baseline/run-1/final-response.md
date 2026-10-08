`--exclude=node_modules` now behaves the same as `--exclude node_modules`. `make test` passes with the fix in place.

**Cause:** `bin/mkbackup.sh` only recognised `--exclude` as a separate word. The `--exclude=PATTERN` spelling fell into the catch-all `--*)` branch, which skips unknown long options so older callers keep working. The exclude was therefore dropped without any message, and everything got archived.

**Fix:** I added a `--exclude=*)` case in `bin/mkbackup.sh` that sets the pattern from `${1#--exclude=}`.

**Regression test:** the new `test/test_mkbackup_exclude.sh` builds an archive with each spelling. It asserts that `keepme/file.txt` is present and `skipme` is absent in both. `test/run-tests.sh` picks it up automatically through its `test_*.sh` glob. With the fix stashed, the new test fails on the `=` spelling ("equals: excluded directory is present in the archive"), so it does catch the bug.

The catch-all branch still skips other unknown `--foo` options silently. I left it alone because the comment says that is deliberate, but it's how this bug stayed hidden. I haven't committed anything.
