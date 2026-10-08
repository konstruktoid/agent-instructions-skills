`bin/prune-artifacts.sh` now exits 1 when the artifact directory doesn't exist. It prints `error: artifact directory not found: <path>` to stderr and no longer prints the "pruned" line. The edit is uncommitted.

I also made the script exit non-zero if `find` itself fails, so a failed delete can't report success either.

I checked it by running the script against temporary directories:
- **Missing directory:** exit code 1, with the error message.
- **Existing directory:** exit code 0. It deleted a 30-day-old `.tar.gz` and kept a fresh one.

I didn't add a test file to the repo, because it has no test suite. These were one-off manual runs.

Cron only emails or logs the failure if your crontab setup does that. If it discards output, the non-zero exit is still silent.
