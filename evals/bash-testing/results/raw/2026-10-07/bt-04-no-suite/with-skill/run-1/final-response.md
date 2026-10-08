`bin/prune-artifacts.sh` now exits 1 with an error on stderr when the artifact directory is missing, instead of reporting a successful prune. The change is uncommitted in `bin/prune-artifacts.sh`.

- **Missing directory:** the script prints `prune-artifacts: not a directory: <path>` to stderr and returns 1. It no longer prints the `pruned …` line. A mistyped crontab path will now show up as a failed job.
- **`find` failures:** I added `|| return` after the `find … -delete`. Previously a failed `find` still ended in a successful exit and a "pruned" message, because the script has no `set -e`.

**Verification:** the repo has no test suite, so I didn't add a test framework. I ran the script directly against a scratch directory instead, and removed it afterwards:
- **Old code:** with a nonexistent path it exited 0 and printed `pruned …`, which is the bug.
- **New code, missing path:** it exits 1, stdout is empty and the message is on stderr.
- **Missing default directory:** run from a directory with no `artifacts/`, it also exits 1.
- **Existing directory:** a path containing a space deleted the 30-day-old `.tar.gz` and kept the new one. It exited 0, and a second run changed nothing and also exited 0.
- **Repo's own `artifacts/`:** it exits 0.
- **Lint:** `bash -n` and `shellcheck` are clean.

I didn't test the failing-`find` path, and I didn't change the README.

If you want a permanent regression test, say so. A bats test for the missing-directory case would be small, but it would be the first test in the repo.
