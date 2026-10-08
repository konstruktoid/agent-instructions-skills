`bin/report.sh --json FILE` now prints the counters as JSON, for example `{"total":3,"passed":2,"failed":1}`. The text output is unchanged. `make test` passes all 8 tests (the 3 existing ones plus 5 new). `bash -n` and `shellcheck` are clean on the script and the test file.

- **Argument handling:** `--json` can come before or after the file. The usage message is now `usage: report.sh [--json] FILE`, and the exit codes are the same as before (64 for no file, 66 for an unreadable one).
- **New tests in `test/report.bats`:** these cover the JSON output, the flag after the file, a path containing a space, and the usage and missing-file failures. The failure cases also check that stdout stays empty. I added `bats_require_minimum_version 1.5.0` to the file because the stderr checks need it.
- **Without the change:** the new tests fail against the old script (4 failures when I stashed the script change, so one of the five happens to pass either way). The 3 original tests are untouched and still pass.
- **README:** I added one line mentioning `--json`.

I didn't commit anything.
