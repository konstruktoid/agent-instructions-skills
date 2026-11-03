`bin/report.sh` now takes `--json` and prints `{"total":3,"passed":2,"failed":1}` for the sample data. `make test` passes all 8 tests (the 3 existing ones unchanged, 5 new). `shellcheck` and `bash -n` are clean. I didn't confirm the new tests fail against the old script.

- **Flag position:** `--json` works before or after the file argument.
- **Text output:** without the flag the output is byte-for-byte what it was, and the existing text-output test still passes.
- **Usage line:** the message now reads `usage: report.sh [--json] FILE`. The existing usage test only checks the exit code (64), so this wording change isn't covered by any assertion.
- **Errors:** a missing file or missing argument keeps exit codes 66 and 64 in JSON mode. Nothing goes to stdout, so the dashboard never receives half-formed JSON.
- **New tests:** in `test/report.bats` they cover:
  - JSON output
  - the flag after the file
  - a path containing a space
  - `--json` with no file
  - `--json` with a missing file
- **bats version:** I added `bats_require_minimum_version 1.5.0` to that file because one test uses `run --separate-stderr`.
