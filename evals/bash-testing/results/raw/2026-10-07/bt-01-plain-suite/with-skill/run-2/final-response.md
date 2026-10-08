`--exclude=node_modules` now behaves the same as `--exclude node_modules`. The full suite passes with the fix, and `shellcheck` and `bash -n` are clean.

**Cause:** the parser only matched `--exclude` as a separate word. `--exclude=PATTERN` fell into the `--*` branch, which skips unknown long options, so no exclude was set and everything was archived.

**Fix:** I added an `--exclude=*` case to `bin/mkbackup.sh` that takes the value after the `=`.

**Regression test:** the new `test/test_mkbackup_exclude.sh` follows the style of the existing tests, so `make test` picks it up. It runs both spellings against a source directory whose name contains a space. It asserts exit status 0, that `keepme/file.txt` is in the archive, and that the excluded directory is not.

I also stashed the fix and reran the suite. The new test failed on the `=` spelling ("equals: excluded directory is present in the archive") and the old test still passed, so the new test does catch the bug.

I left the "skip unknown long options" behaviour as it was. That means a misspelled flag such as `--exlcude=x` is still silently ignored, which is the same kind of problem. I didn't change it because older callers may rely on it.
