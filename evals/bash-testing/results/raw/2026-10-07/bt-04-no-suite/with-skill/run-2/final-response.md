`bin/prune-artifacts.sh` now exits 1 when the artifact directory doesn't exist. It prints `prune-artifacts: not a directory: <path>` to stderr and no longer prints the "pruned" line. I haven't committed the change.

- **Missing directory:** the `-d` check used to be an `if` that skipped the `find` and still reported success. It's now a guard that returns 1. A mistyped crontab path shows up as a failed job.
- **`find` failure:** I also made a failing `find` return 1 with its own stderr message. The script has no `set -e`, so a failed `find` used to be followed by a "pruned" message and exit 0, which is the same kind of false success.

I didn't add a test. The repo has no test suite, and adding a framework goes beyond this fix. I ran the script directly against a scratch directory instead:

- **Missing path:** exit 1, empty stdout, message on stderr.
- **Existing directory with a space in its path:** exit 0. The 30-day-old `.tar.gz` was removed and the fresh one kept.
- **Default `artifacts` with no such directory in the working directory:** exit 1.

`bash -n` and `shellcheck` are clean. I didn't run the old script against the missing path, so "it used to exit 0" comes from your report and the code, not a run.

If you want this locked in as a regression test, say so and I'll pick a framework (probably bats).
