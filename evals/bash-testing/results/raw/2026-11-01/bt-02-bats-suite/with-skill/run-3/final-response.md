`bin/report.sh --json FILE` now prints `{"total":3,"passed":2,"failed":1}` for `data/sample.csv`. All 7 tests pass under `make test`, and `shellcheck` and `bash -n` are clean.

- **Text output:** unchanged. The three existing tests pass as they were, and the text format is still `total=3 passed=2 failed=1`.
- **Flag position:** `--json` has to come before the file name.
- **Usage message:** it now reads `usage: report.sh [--json] FILE`. That is the only change to existing output.
- **Errors:** with `--json`, the usage error (exit 64) and the missing-file error (exit 66) still go to stderr. Nothing is written to stdout in those cases.
- **Tests:** I added four to `test/report.bats`:
  - the JSON output;
  - the usage error;
  - the missing-file error;
  - a path containing a space.
- **New tests fail without the change:** with the `report.sh` change stashed, 3 of the 4 new tests failed. The fourth (usage error with `--json` alone) was not counted separately.
- **bats version:** I added `bats_require_minimum_version 1.5.0` to the test file, because the stderr checks use `run --separate-stderr`.

Nothing is committed.
