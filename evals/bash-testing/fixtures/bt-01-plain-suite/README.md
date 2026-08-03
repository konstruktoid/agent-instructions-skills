# backup-tools

`bin/mkbackup.sh [--exclude PATTERN] SOURCE ARCHIVE` packs a directory into a gzipped tar
archive.

Tests are plain Bash scripts under `test/`, one file per area, named `test_*.sh`. Each one
sources `test/helpers.sh` and exits non-zero on the first failure. `make test` runs the
whole suite through `test/run-tests.sh`.
