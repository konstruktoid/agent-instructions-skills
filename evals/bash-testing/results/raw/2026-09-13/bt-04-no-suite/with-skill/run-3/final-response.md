Files changed: `bin/prune-artifacts.sh` (missing directory now returns 1 with a stderr message instead of silently exiting 0; entry point guarded so the script can be sourced by tests), new `test/prune-artifacts_test.sh` (plain-script tests, no framework existed), and `README.md` updated to point at it.

Verification: `shellcheck` and `bash -n` clean on both files; `test/prune-artifacts_test.sh` passes against the fix and was confirmed to fail against the pre-fix version (caught the exit-0 bug). Not committing — that's your call.
