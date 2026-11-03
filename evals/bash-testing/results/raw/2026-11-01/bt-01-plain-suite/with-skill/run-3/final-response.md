`--exclude=node_modules` now works the same as `--exclude node_modules`.

**Cause:** the parser only matched `--exclude` exactly. `--exclude=PATTERN` fell into the catch-all `--*)` branch, which skips unknown long options, so no exclusion was applied.

**Fix:** I added an `--exclude=*)` case to `bin/mkbackup.sh` that takes the value after the `=`.

**Regression test:** the new `test/test_mkbackup_exclude.sh` follows the style of the existing plain-script suite and is picked up by `make test`.
- It builds an archive with each spelling, using a source path that contains a space. It checks that the exit status is 0, that `keepme/file.txt` is present, and that `skipme` is absent.
- It also checks that `--exclude=` with an empty value excludes nothing.

**Verification:**
- `make test` passes, including the existing test.
- With the fix stashed, the new test fails on the `=` spelling ("equals: excluded directory is in the archive"), so it catches the original bug.
- `shellcheck` is clean on the script and all test files, and `bash -n` is clean on the new test.

Unknown long options are still silently skipped, which is the same cause as this bug. I left that alone because the script's comment says it is deliberate for older callers. A typo like `--exclud=x` will still archive everything without a warning, so you may want to make it warn.
