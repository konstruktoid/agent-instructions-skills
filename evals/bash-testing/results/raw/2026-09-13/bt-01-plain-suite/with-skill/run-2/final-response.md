Full suite passes, shellcheck is clean, `bash -n` is clean, and the new assertion fails against the unfixed script and passes with the fix.

**Files changed:**
- `bin/mkbackup.sh` — added an `--exclude=*` case so `--exclude=PATTERN` extracts the value instead of falling into the unknown-long-option branch that silently discards it.
- `test/test_mkbackup_basic.sh` — extended the existing exclude coverage (per repo convention, updating rather than adding a parallel test file) to assert `--exclude=skipme` also excludes the directory.

Following this repo's `CLAUDE.md`: no commit was made, per the version-control rule that requires explicit request. `/clear` before starting anything unrelated.
