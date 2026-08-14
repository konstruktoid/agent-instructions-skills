Fixed and verified.

**Root cause**: `bin/mkbackup.sh`'s arg parser only matched the literal `--exclude` (space-separated value); `--exclude=node_modules` fell through to the generic `--*)` catch-all, which silently discards unknown long options — so the exclude was dropped and everything got archived.

**Fix**: added a `--exclude=*)` case that extracts the value via parameter expansion, so both spellings now behave identically.

**Regression coverage**: extended `test/test_mkbackup_basic.sh` with an `--exclude=skipme` case alongside the existing `--exclude skipme` one. Verified it fails on the pre-fix script (confirmed via `git stash`) and passes with the fix; ran the full suite (`test/run-tests.sh`) plus `shellcheck` and `bash -n` on all touched files — all clean.
