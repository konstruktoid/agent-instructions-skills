**Files changed:**
- `bin/prune-artifacts.sh` — missing artifact directory now prints an error to stderr and returns 1 instead of silently exiting 0; `main` is guarded behind a `BASH_SOURCE`/`$0` check so the script can be sourced for testing.
- `tests/prune-artifacts_test.sh` (new) — plain-script test suite (no framework existed in the repo, matching its "there are no automated tests" state), covering: missing directory → exit 1 + stderr message, existing directory → exit 0 with old `.tar.gz` files pruned and newer ones kept (fixture directory name includes a space).

Verification: `bash -n` and `shellcheck` clean on both files; test suite passes against the fix (6/6); confirmed by temporarily swapping in the pre-fix script that the same suite fails (2/6) in exactly the way the bug predicts — silent exit 0, empty stderr.

Task accepted and reported — recommend `/clear` before starting anything unrelated.
