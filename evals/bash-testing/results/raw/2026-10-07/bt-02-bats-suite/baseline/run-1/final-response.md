`bin/report.sh` now has a `--json` flag. It prints the same three counters as `{"total":3,"passed":2,"failed":1}`, and `make test` passes all 7 tests (3 existing, 4 new).

- **Flag position:** `--json` works before or after the file argument.
- **Text output:** without the flag, the output is the same `total=… passed=… failed=…` line as before. I didn't touch that code path, and the existing text-output test still passes.
- **Usage message:** it now reads `usage: report.sh [--json] FILE`. That is a visible change to the usage line, so tell me if the dashboard parses it.
- **Tests:** the new tests in `test/report.bats` cover JSON output, `--json` after the file, `--json` with no file (exit 64), and `--json` with a missing file (exit 66).
- **README:** I added one line about the flag.

Any other argument is treated as the file name, and the last one wins, as before. I didn't add a check that rejects unknown flags.
