`bin/report.sh` now takes `--json` and prints the three counters as JSON, e.g. `{"total":3,"passed":2,"failed":1}`. `make test` passes all 7 tests, the 3 existing ones and 4 new ones.

- **Text output:** it is unchanged. The existing test still checks the exact line.
- **Flag position:** `--json` works before or after the file argument.
- **Usage message:** it now reads `usage: report.sh [--json] FILE`. That text goes to stderr, so say if you want it left as it was.
- **New tests:** in `test/report.bats`, they cover the JSON output on `data/sample.csv` (checked with `jq`), `--json` after the file, `--json` with no file (exit 64), and `--json` with a missing file (exit 66).
- **README:** I added a line about the flag.

I haven't committed anything.
