`bin/archive-logs.sh` now takes several service names, supports `--keep-days N`, and prints a one-line summary. The README describes the new usage.

`shellcheck -x` and `bash -n` are clean. `shfmt` isn't installed here, so I didn't run a format check. I ran the script in a scratch copy and all the paths below behaved as intended, with no temp directories left behind. I haven't run it from cron or against real logs.

- **Several services:** `bin/archive-logs.sh api web` archives both. It checks every name before archiving anything, and it ignores repeated names. Names must match `[a-z][a-z0-9_-]{0,63}`, which also rejects anything that could inject into a command or path. A service with no `logs/<service>` directory fails with status 66 instead of producing an empty archive.
- **Pruning:** `--keep-days N` (or `--keep-days=N`) deletes top-level `archives/*.tar.gz` files older than N days. It runs only after every new archive is in place, and it is skipped if any archive fails. It doesn't run at all without the option. N must be a positive integer, so `0` is rejected. In the test, `--keep-days 30` removed the two 40-day-old files and kept the 3-day-old one.
- **Summary:** it prints `archived 2 service(s): api web; pruned 2 archive(s) older than 30 days`, and drops the `pruned …` part when `--keep-days` isn't given.
- **Exit codes:** 64 for usage errors, 65 for an invalid name or `--keep-days` value, and 66 for a missing log directory.
- **Hardening:**
  - The script now sets `set -Eeuo pipefail`, quotes everything and sets its own `PATH`.
  - It builds archives in a `mktemp -d` directory inside `archives/` rather than the predictable `/tmp/archive-logs.$$`.
  - The directory is removed on exit or signal, and being on the same filesystem makes the final move atomic.

The script now needs Bash 4.2 or later and GNU `find`. It still expects to run from the repository root, since `logs/` and `archives/` are relative paths, and the README says so.

The old script saved archives with your default file permissions, and that hasn't changed. I didn't add a `umask`, so existing readers of `archives/` won't lose access.

I didn't commit anything.
