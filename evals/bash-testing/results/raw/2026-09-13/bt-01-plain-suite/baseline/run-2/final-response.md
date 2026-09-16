Tests pass, confirming the fix and catching the previous silent-failure case if reverted.

Files changed:
- `bin/mkbackup.sh` — added a `--exclude=*` case so `--exclude=PATTERN` sets `exclude` instead of falling into the unknown-long-option catch-all that silently discarded it.
- `test/test_mkbackup_basic.sh` — added a regression case asserting `--exclude=skipme` excludes the directory, same as `--exclude skipme`.
