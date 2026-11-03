`bin/prune-artifacts.sh` now fails loudly when the artifact directory doesn't exist. It prints `error: artifact directory not found: <path>` to stderr and exits 1, so cron will report the failure. It no longer prints the "pruned …" line in that case.

I also made it exit 1 with an error message if `find` itself fails, for example on a permissions problem. Before, that failure would still have ended in a "pruned" message and exit 0. The change is uncommitted.

I ran the script against a temporary directory to check it, since the repo has no tests:
- **Missing directory:** it printed the error and exited 1.
- **Path that is a file, not a directory:** it printed the error and exited 1.
- **Existing directory:** a 30-day-old `.tar.gz` was deleted and a fresh one was kept. It printed "pruned …" and exited 0.
- **Default `artifacts` directory:** it exited 0 and deleted nothing, since those files are new.

I didn't add a test file, because the README says the repo has no automated tests. I can add a small bash test script if you want one.
