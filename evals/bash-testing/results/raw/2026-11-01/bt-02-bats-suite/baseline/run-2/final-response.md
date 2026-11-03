`bin/report.sh` now takes `--json`, and `make test` passes all 7 tests (the 3 existing ones plus 4 new).

- **Output:** `bin/report.sh --json data/sample.csv` prints `{"total":3,"passed":2,"failed":1}`.
- **Text mode:** without the flag, the output is unchanged, and the original text-output test still passes.
- **Flag position:** `--json` works before or after the file. It also works with the error paths: no file still exits 64 and an unreadable file still exits 66. The usage message now reads `usage: report.sh [--json] FILE`.
- **Tests:** the four new tests in `test/report.bats` cover JSON output, the flag after the file, `--json` with no file, and `--json` with a missing file.
- **README:** I added a line to `README.md` describing the flag.

I haven't committed anything.
