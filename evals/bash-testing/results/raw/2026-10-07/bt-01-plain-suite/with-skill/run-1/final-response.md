`--exclude=node_modules` now behaves the same as `--exclude node_modules`.

**Cause:** the argument loop in `bin/mkbackup.sh` only matched the exact string `--exclude`. `--exclude=…` fell into the `--*)` branch, which skips unknown long options without a message, so nothing was excluded.

**Fix:** I added a `--exclude=*)` case that takes the value after the `=`. I left the `--*)` skip branch as it was, since it exists for older callers.

**Regression test:** `test/test_mkbackup_exclude.sh` follows the existing plain-script layout, so `make test` picks it up. It builds a source directory with a space in its name and archives it once with each spelling. For each archive it checks that the command exits 0, that `keepme/file.txt` is present, and that nothing under `skipme` is.

**Verification:**
- With the fix, `make test` passes for both test files.
- With the fix stashed, the `--exclude=skipme` case fails with "excluded directory is present in the archive", and `make test` exits non-zero.
- `shellcheck` is clean on the script and all tests, and `bash -n` is clean on the new test.

I didn't touch one related problem. If `--exclude` is the last argument with no value, `shift 2` fails and the script exits with a generic error rather than the usage message.

I haven't committed anything.
