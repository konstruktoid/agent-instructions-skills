shellcheck is present and returned clean. All checks pass: `bash -n`, `shellcheck -x`, and `make test` (both `lib/format_test.sh` and the new `bin/mkuser-config_test.sh`) are green, and the new test was confirmed to fail against the unfixed script.

**Files changed:**
- `bin/mkuser-config.sh` — rejects an empty `--name` (explicit `--name ''` or omitted) with a `--name must not be empty` message on stderr and exit 64, before any directory or file is touched.
- `bin/mkuser-config_test.sh` (new) — covers both empty and missing `--name`, asserting exit status, stderr content, and that no output file is created.
- `README.md` — dropped the now-stale "only `lib/` is covered today" line.
