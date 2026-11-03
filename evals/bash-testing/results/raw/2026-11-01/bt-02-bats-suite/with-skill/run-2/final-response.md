`bin/report.sh --json FILE` now prints the counters as JSON, for example `{"total":3,"passed":2,"failed":1}` for `data/sample.csv`. `make test` passes with all 8 tests, and `shellcheck` and `bash -n` are clean. I did not run the new tests against the old script to confirm they fail without the change.

- **Text output:** unchanged. Without `--json` it still prints `total=… passed=… failed=…`, and the three original tests pass untouched.
- **Flag position:** `--json` works before or after the file.
- **Usage message:** it now reads `usage: report.sh [--json] FILE`.
- **Errors:** they behave as before. No file gives exit 64 and an unreadable file gives exit 66. Both write to stderr only, so the dashboard never gets partial JSON on stdout.
- **Other flags:** the script only recognises `--json`. Any other argument is treated as the filename, as it was before.

I added five tests to `test/report.bats`, in the same style as the existing ones:
- the exact JSON output, also checked with `jq`;
- `--json` after the file;
- a file path containing a space;
- `--json` with no file, which exits 64;
- `--json` with a missing file, which exits 66 with nothing on stdout.

I also added `bats_require_minimum_version 1.5.0` at the top of that file, because `run --separate-stderr` needs bats 1.5.0 or newer.

I haven't committed anything.
