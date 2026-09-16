All clean: `bash -n` and `shellcheck` pass with no findings, and `make test` runs both the existing `lib/format.sh` coverage and the new `bin/mkuser-config.sh` coverage to a green result.

**Files changed:**
- `bin/mkuser-config.sh` — rejects an empty `--name` with a stderr message and exit 64 (matching the script's existing usage-error convention), before any file is touched.
- `bin/mkuser-config_test.sh` (new) — subprocess-level coverage following the repo's plain-script `*_test.sh` convention: asserts non-zero exit, non-empty stderr, and no output file on empty `--name`; asserts the existing valid-name path still writes the correct line. Confirmed to fail against the pre-fix script.

Note: `bin/` had no test coverage before this (README said "Only `lib/` is covered today"); you may want to update that line.
