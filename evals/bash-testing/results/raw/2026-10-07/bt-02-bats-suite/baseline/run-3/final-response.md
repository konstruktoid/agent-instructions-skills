`bin/report.sh` now takes `--json`. On `data/sample.csv` it prints `{"total":3,"passed":2,"failed":1}`. All 7 bats tests pass with `make test`: the 3 existing ones and 4 new ones.

- **Flag position:** `--json` works before or after the file argument.
- **Text output:** The text line is unchanged, and the existing text-mode test still checks it exactly.
- **Usage message:** It now reads `usage: report.sh [--json] FILE`, so the stderr text differs from before. The exit codes are the same (64 for no file, 66 for an unreadable file).
- **New tests:** In `test/report.bats` they cover JSON output, the flag after the file, `--json` with no file (exit 64), and `--json` with a missing file (exit 66).
- **README:** It gets one line mentioning `--json`.

I haven't committed anything.
