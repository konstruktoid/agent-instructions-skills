`bin/prune-artifacts.sh` now exits 1 and prints `prune-artifacts: directory not found: <path>` to stderr when the directory is missing. A mistyped path in the crontab will now fail visibly instead of looking like a successful prune. I haven't committed the change.

I also made it exit 1 with a message if `find` itself fails. It used to ignore that. The success line `pruned …` now prints only after a real prune.

I checked it by running the script by hand, since the repo has no test suite and I didn't add one:
- **Missing directory:** exits 1 with the error message.
- **Path that is a file, not a directory:** exits 1 with the same message.
- **Existing directory:** exits 0. In a temp directory, a `.tar.gz` backdated 30 days was deleted and a fresh one was kept.
- **Repo's own `artifacts/` directory:** exits 0.

I did not run it under cron itself. Cron only mails or logs the error if the host is set up to do that (for example `MAILTO` in the crontab).
