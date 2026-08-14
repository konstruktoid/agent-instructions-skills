Everything looks clean. Summary of the work:

**Fix** (`bin/mkuser-config.sh`): moved the script body into a `main()` function (guarded so it only runs when executed directly, matching the skill's testability pattern) and added a check that rejects an empty `--name` — prints `mkuser-config: --name must not be empty` to stderr and exits 64, before any directory is created or line appended.

**Test** (`bin/mkuser-config_test.sh`, new): matches the repo's existing plain-script convention (`lib/format_test.sh`). Covers:
- empty `--name`: non-zero exit, no stdout, stderr message, no config file written
- missing `--name` (same empty-default path)
- valid `--name` still appends correctly (regression guard)

Verified the new test fails against the pre-fix script (`empty --name: expected non-zero exit, got 0`), confirming it actually catches the bug. `make test` now passes both `lib/format.sh` and `bin/mkuser-config.sh` suites, and `shellcheck`/`bash -n` are clean on all four shell files. Also updated the README line that said only `lib/` was covered.
