`bin/archive-logs.sh` now takes several service names, supports `--keep-days N`, and prints a one-line summary. The README describes the new usage. I ran it on a scratch copy and the checks passed; nothing is committed.

- **Checks run:** `shellcheck -x` and `bash -n` are clean. On the scratch copy I ran two services at once, then pruning with `--keep-days 7` and with `--keep-days=3`. I also tried no arguments, an unknown service, a bad or missing `--keep-days` value, `-rf`, `../etc`, and a mix of good and bad services. Each failure case exited non-zero with a message on stderr.
- **Usage:** `archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`.
- **Summary line:** for example `archived 2 service(s): api web; pruned 3 archive(s) older than 30 days`. The pruned part appears only when `--keep-days` is given.
- **Pruning:**
  - It deletes `*-YYYYMMDD.tar.gz` files in `archives/` by modification time, and only after every new archive is in place.
  - If any service fails, nothing is pruned.
  - `N` must be a positive integer, so `--keep-days 0` is rejected.
- **Input checks:** service names must match `^[a-z0-9][a-z0-9_-]{0,63}$` and have a directory under `logs/`. Everything is validated before anything is written. Bad usage exits 64 and a missing service exits 66.

The script was rewritten more than extended, to fix some existing problems:

- **Hardening:** it uses strict mode, a fixed `PATH` and locale, and every expansion is quoted. The `/tmp/archive-logs.$$` directory is replaced with a `mktemp` directory under `archives/`, which is removed on exit and on INT or TERM.
- **Atomic move:** staging inside `archives/` makes the final move an atomic rename.
- **Archive layout:** members are still stored as `logs/<service>/...`, as before.

**Behavior change:** paths are now resolved relative to the repository (the parent of `bin/`) instead of the working directory. This is the same result if cron already runs from the repo root, and it is safer if it doesn't. A service name given twice is archived twice, and the second run overwrites the first.

I didn't add a test suite because the repo has none.
