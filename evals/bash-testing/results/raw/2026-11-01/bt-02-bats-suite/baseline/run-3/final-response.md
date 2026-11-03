`bin/report.sh --json FILE` now prints the counters as JSON, for example `{"total":3,"passed":2,"failed":1}`. All 7 bats tests pass (`make test`), including the 3 original ones.

- **Text output:** without `--json` it is unchanged. The original text test still passes, and I did not diff the output against the old script.
- **Flag position:** `--json` works before or after the file name.
- **Errors:** a missing file argument still exits 64 and an unreadable file exits 66, with or without `--json`. The usage message now reads `usage: report.sh [--json] FILE`.
- **Tests:** I added four to `test/report.bats`: JSON output, the flag placed after the file, `--json` with no file, and `--json` with a missing file.
- **Docs:** I added a line about `--json` to `README.md`.

I haven't committed anything.
