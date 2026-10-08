`bin/prune-artifacts.sh` now exits 1 with an error on stderr when the artifact directory doesn't exist, so a mistyped crontab path will fail instead of looking like a successful prune. I haven't committed the change.

**What changed**
- **Missing or non-directory path:** the script prints `prune-artifacts: not a directory: <path>` to stderr and returns 1. It no longer prints the `pruned …` line in that case.
- **`find` failures:** I also made the script return 1 when `find` itself fails, for example when it can't delete a file. The old script ignored that and printed `pruned …`, which is the same kind of false success.

**How I checked it**
The repo has no tests and the README says so, so I didn't add a framework. I ran the script by hand against scratch directories, and `bash -n` and `shellcheck` are clean.
- **Before the change:** a nonexistent path returned exit 0 and printed `pruned …`.
- **Missing directory:** exit 1, nothing on stdout, the error on stderr.
- **A file passed as the directory:** exit 1.
- **Normal run:** the directory name contained a space. The 30-day-old archive was deleted and the fresh one kept, with exit 0.
- **Rerun:** exit 0, and the directory contents were unchanged.
- **`find` can't delete a file** (read-only directory): exit 1 with the error on stderr.

**One gap you should know about**
An empty first argument (`prune-artifacts.sh ""`) falls back to the default `artifacts` directory, because the script uses `${1:-artifacts}`. That's existing behavior and I left it alone.

The scratch directories are deleted, and the only modified file is `bin/prune-artifacts.sh`.
