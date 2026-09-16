Confirmed: the new test fails on the old script and passes with the fix.

Root cause: `--exclude=node_modules` matched the generic `--*)` catch-all before the parser ever checked for `--exclude`, so it was silently discarded. Fixed by adding a `--exclude=*)` case in `bin/mkbackup.sh` that splits the value off the flag.

Files changed:
- `bin/mkbackup.sh` — added `--exclude=*` handling
- `test/test_mkbackup_basic.sh` — added a regression case for the `=` form

`make test` passes; the new assertion was verified to fail against the pre-fix script. Run `/clear` before starting anything unrelated.
