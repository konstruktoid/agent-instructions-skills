Fixed and verified. Files changed:

- `bin/prune-artifacts.sh` — missing directory now prints an error to stderr and returns 1 instead of exiting 0 silently.
- `test/prune-artifacts_test.sh` (new) — plain-script test (no framework existed; repo has none installed and README said so), covering missing dir, missing dir with a space, and the existing-directory happy path.
- `README.md` — pointed at the new test instead of claiming none exist.

Verification: test fails against the pre-fix script (confirmed via `git stash`), passes against the fix, and `shellcheck`/`bash -n` are clean on both files.
