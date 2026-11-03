`--exclude=PATTERN` now behaves the same as `--exclude PATTERN`.

**Cause:** `bin/mkbackup.sh` had no case for `--exclude=…`. It fell into the "unknown long option, skip it" branch, so the exclude value was dropped and everything was archived.

**Fix:** I added an `--exclude=*` case in `bin/mkbackup.sh` that takes the value after the `=`. The skip-unknown-options behaviour is unchanged.

**Regression test:** `test/test_mkbackup_exclude.sh` is new and follows the existing plain-script style, so `make test` picks it up. It archives a source directory whose name contains a space, using both spellings. It checks that `keepme/file.txt` is kept, `skipme` is left out, and the exit status is 0. It also checks that an empty `--exclude=` still exits 0.

**Verification:**
- With the fix, `make test` passes.
- With the old script restored, the new test fails with "equals: excluded directory is present in the archive", so it catches the bug.
- `shellcheck` and `bash -n` are clean on the script and the test files.

The fix and the new test are in the working tree and not committed.
