Everything checks out. Summary:

**Fix** (`bin/prune-artifacts.sh`): a missing/mistyped artifact directory now prints `prune-artifacts: <dir>: no such directory` to stderr and returns exit code 1, instead of silently printing `pruned ...` and exiting 0. `main` is guarded with a `BASH_SOURCE`/`$0` check so it stays sourceable for testing without executing.

**Tests** (`test/prune-artifacts_test.sh`): since the repo had no test framework (README said so explicitly) and `bats`/`shunit2` aren't installed in this environment, I used a minimal plain-script suite that runs the script as a subprocess and asserts on exit code, stdout, and stderr — matching the "plain scripts that exit non-zero on failure" style the skill allows. Covers:
- missing directory → non-zero exit, stderr message, no `pruned` on stdout
- missing default `artifacts` dir (no args) → non-zero exit
- existing directory → exit 0, old `.tar.gz` deleted, recent one kept, success message
- directory path containing a space → handled correctly

Verified the new tests fail against the pre-fix script (via `git stash`) and pass against the fix. `shellcheck` and `bash -n` are clean on both the script and the test file. README updated to reflect that tests now exist and how to run them.
