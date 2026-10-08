`bin/report.sh` now takes `--json` before the file: `report.sh --json FILE` prints `{"total":3,"passed":2,"failed":1}` for `data/sample.csv`. The text output is unchanged.

`make test` passes all 7 tests, and `shellcheck` and `bash -n` are clean on the script and the test file. With the script change stashed, the four new tests failed and the original three passed.

- **Usage line:** the usage message on stderr now reads `usage: report.sh [--json] FILE`. The old text didn't mention the flag.
- **Error paths:** a missing file still exits 66 and no file still exits 64. In both cases stdout is empty, so the dashboard never gets partial JSON.
- **New tests:** I added four to `test/report.bats`. They cover the JSON output, a path with a space, `--json` with no file, and `--json` with a missing file. The last one asserts stdout is empty and stderr has the error.
- **Test header:** I added `bats_require_minimum_version 1.5.0` to that file. The `--separate-stderr` flag needs it, and without it bats printed a warning.

I didn't update the README. It still describes only the text output, so say if you want `--json` documented there.
