All tests pass, including the new regression test for the `--exclude=PATTERN` spelling.

**Root cause:** the `case` statement in `bin/mkbackup.sh` only matched the literal `--exclude`; `--exclude=node_modules` fell through to the generic `--*)` catch-all, which silently discards unrecognized long options — so the exclude pattern was dropped and everything got archived.

**Fix:** `bin/mkbackup.sh:15-21` — added a `--exclude=*)` case that extracts the value after `=`.

**Regression coverage:** `test/test_mkbackup_basic.sh` now also runs `--exclude=skipme` and asserts the excluded directory is absent from the archive, alongside the existing `--exclude skipme` case.
