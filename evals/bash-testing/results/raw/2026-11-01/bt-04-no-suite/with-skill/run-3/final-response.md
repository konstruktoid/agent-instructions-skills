`bin/prune-artifacts.sh` now exits non-zero when the artifact directory is missing, so a mistyped crontab path shows up as a failed job. I verified this by running the script directly against scratch directories, not with an automated test. I didn't add a test because the repo has none (the README says so) and I didn't want to introduce a framework unasked.

**What changed**
- If the directory doesn't exist, or the path is a file, the script prints `prune-artifacts: artifact directory not found: <dir>` to stderr and exits 2. It no longer prints the "pruned" line in that case.
- If `find` itself fails, the script now prints an error and exits 1. Before, it ignored that failure and still printed "pruned".
- The "pruned …" line prints only after a successful run.

**What I ran**
- **Missing directory:** exit 2, empty stdout, error on stderr.
- **Path is a file:** exit 2.
- **Normal run:** in a directory with a space in its name, the 30-day-old file was deleted, the new file stayed, and the exit code was 0.
- **Rerun:** a second run exited 0 and changed nothing.
- **Before the fix:** the committed script, given a missing directory, printed "pruned …" and exited 0, so the new behavior is the fix and not something that was already true.
- **Checks:** `bash -n` and `shellcheck` are clean.

I did not run the `find`-failure branch (exit 1).

If you want this to stay checked, I can add a small bats test, since `bats` is installed here. That would be the repo's first test file.
