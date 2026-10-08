`bin/report.sh` now takes `--json` and prints the three counters as JSON, e.g. `{"total":3,"passed":2,"failed":1}`. All 7 tests pass under `make test`: the 3 existing ones and 4 new ones.

- **Text output:** without the flag, the output is unchanged. The existing text-output test still passes.
- **Flag position:** `--json` works before or after the file argument.
- **Errors:** missing-file and no-file errors behave the same with the flag, exiting 66 and 64 respectively. The usage message now reads `usage: report.sh [--json] FILE`.
- **Tests:** the new ones cover JSON output, the flag after the file, `--json` with no file, and `--json` with a missing file.
- **Docs:** I added a line about the flag to `README.md`.
- **Not committed:** I haven't committed anything.

I didn't add handling for unknown flags, so something like `--jsno` is treated as the filename and fails with the usual "cannot read" error (exit 66).
