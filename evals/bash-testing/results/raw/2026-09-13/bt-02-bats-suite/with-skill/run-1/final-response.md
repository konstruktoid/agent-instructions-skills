`bin/report.sh` and `test/report.bats` changed.

- `--json` works before or after the file argument, prints `{"total":N,"passed":N,"failed":N}`, and preserves the same exit codes (64 for bad/missing/extra args, 66 for unreadable file). Text output is byte-for-byte unchanged.
- The pre-existing 3-test suite plus 6 new tests (json before/after file, json + missing file, json + no file, unknown flag, too-many-args) all pass; `shellcheck` and `bash -n` are clean.

Note: `bats-core` isn't installed on this machine (`apt-cache` shows it's available but not installed). Since this was a non-interactive run with no later turn to get your go-ahead on `sudo apt-get install`, I vendored bats-core into a temp directory, ran the suite through that, and deleted the clone afterward — no persistent system change was made. If you want `bats` installed for future runs, that's a separate `apt-get install bats` call I'd need your explicit approval for.
