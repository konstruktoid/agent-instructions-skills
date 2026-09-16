All checks pass: full suite green, `bash -n` clean, `shellcheck` clean, and the new assertion fails without the fix / passes with it.

**Changed files:**
- `bin/mkbackup.sh` — added a `--exclude=*)` case that splits on `=`, so `--exclude=PATTERN` no longer falls through the unknown-long-option catch-all and gets silently dropped.
- `test/test_mkbackup_basic.sh` — added a case asserting `--exclude=skipme` excludes the directory, matching the existing plain-script test style (no new framework introduced).

The `--*)` catch-all in `bin/mkbackup.sh:27-30` still silently skips any other unrecognized `--foo` or `--foo=bar` option — that's pre-existing behavior, not something I touched, but worth knowing if `--exclude` is ever misspelled.
