`--exclude=node_modules` now behaves the same as `--exclude node_modules`. `make test` passes, and `shellcheck` and `bash -n` are clean.

**Cause:** the parser only matched the exact word `--exclude`. `--exclude=…` fell into the "unknown long option, skip it" branch, so the exclude was dropped and everything was archived.

**Fix, in `bin/mkbackup.sh`:**
- I added an `--exclude=*` branch that takes the value after the `=`.
- A bare trailing `--exclude` with no value now prints the usage message and exits 64. Before, it died on a failed `shift 2` with exit 1.

**Regression test:** the new `test/test_mkbackup_exclude.sh` is picked up by `make test` through the existing `test/test_*.sh` runner. It checks that both spellings:
- exit 0,
- keep `keepme/file.txt` in the archive,
- leave out `skipme`.

It also uses a source path with a space in it, covers `--exclude=` with an empty value (exit 0, no exclude), and covers the missing-value case (exit 64).

I ran the new test before the fix and it failed on the `--exclude=skipme` case, as expected.

One thing I left alone: the parser still silently skips any other unknown `--option`, a deliberate choice for older callers. A typo like `--exlcude=x` would therefore still archive everything.
