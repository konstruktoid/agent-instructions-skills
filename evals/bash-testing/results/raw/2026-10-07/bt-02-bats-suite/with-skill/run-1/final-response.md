`bin/report.sh --json FILE` now prints `{"total":3,"passed":2,"failed":1}` for `data/sample.csv`. Without the flag the output is byte-for-byte what it was. `make test` passes all 8 tests, and `bash -n` and `shellcheck` are clean on the script and `test/test_helper.bash`. I didn't run `shellcheck` on `test/report.bats` itself, because it only accepted the `.bats` file with `-s bash`, which I used before the last edit.

- **Flag position:** `--json` works before or after the file. Any other argument is treated as the file name, so there is no unknown-option check.
- **Usage text:** it now reads `usage: report.sh [--json] FILE`. That is a change to the existing usage message on stderr, though the exit codes (64 and 66) are unchanged.
- **Errors in JSON mode:** the usage and unreadable-file errors still go to stderr with the same exit codes, and stdout stays empty. The dashboard never gets partial JSON.
- **Tests:** I added five tests to `test/report.bats`. They cover:
  - the JSON output;
  - `--json` after the file;
  - a path containing a space;
  - `--json` with no file;
  - `--json` with a missing file.

  The original three tests are unchanged and still pass.
- **Verification:** with the script change stashed, 4 of the new tests fail. The fifth, `--json` with a missing file, passes either way, because the old script also rejected that path.
- **Other edits:** I added `bats_require_minimum_version 1.5.0` to the test file, which `run --separate-stderr` needs. I also added a line to `README.md` mentioning `--json`.

I haven't committed anything.
