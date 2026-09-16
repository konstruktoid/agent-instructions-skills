Confirmed: the new test fails against the old script and passes with the fix. Full suite is green now.

**Changed files:**
- `bin/mkbackup.sh` — added a `--exclude=*` case that extracts the value after `=`, matching the behavior of the space-separated `--exclude PATTERN` form.
- `test/test_mkbackup_basic.sh` — added a regression case exercising `--exclude=skipme`, which fails on the old parsing (verified) and passes now.
