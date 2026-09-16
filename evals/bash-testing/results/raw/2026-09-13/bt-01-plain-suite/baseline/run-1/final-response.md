Tests pass, including the new `--exclude=PATTERN` case.

**Files changed:**
- `bin/mkbackup.sh` — added an `--exclude=*)` case before the generic `--*)` catch-all so `--exclude=node_modules` is parsed instead of silently discarded.
- `test/test_mkbackup_basic.sh` — added a regression check that `--exclude=skipme` excludes the directory, same as `--exclude skipme`.
