# buildreport

`bin/report.sh FILE` summarizes a CSV of build results as one line of counters.

Tests use bats-core. Files live in `test/` as `*.bats` and load `test/test_helper.bash`.
Run them with `make test`, which calls `bats test/`.
