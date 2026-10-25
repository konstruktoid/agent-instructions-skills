`bin/archive-logs.sh` now takes several service names in one run and has a `--keep-days N` option. It also prints a one-line summary. I tested it in a scratch copy of the repo, not on the real `archives/`, and `shellcheck` and `bash -n` are clean. There is no `shfmt` on this host, so the formatter check was not run.

- **Several services:** every name is checked against `^[a-z0-9][a-z0-9_-]{0,63}$` before anything is archived, so a bad name stops the run with nothing written. Archives keep the old `SERVICE-YYYYMMDD.tar.gz` naming.
- **`--keep-days N`:** `--keep-days=N` works too. After all the new archives are in place, it deletes files older than N days (by modification time) that match `SERVICE-YYYYMMDD.tar.gz` directly inside `archives/`. Other files are left alone. If any service fails to archive, the script exits non-zero and does not prune.
- **Summary line:** for example `archived 2 service(s): web api; pruned 1 archive(s) older than 30 day(s)`. The pruned part only appears when `--keep-days` is used.
- **README:** it now describes the usage, the pruning rules, the exit codes and the Bash 4.4 requirement.

I also hardened the script while I was in it:
- **Strict mode and environment:** it runs in strict mode with its own `PATH` and `umask`.
- **Working directory:** it uses a `mktemp` directory inside `archives/` instead of `/tmp/archive-logs.$$`, so the final move is a rename. A trap removes that directory on exit, error or signal.
- **Exit codes:** 64 for a usage error and 65 for an invalid service name or `--keep-days` value.

**Test results:**
- Archiving two services, and pruning, behaved as intended. A 40-day-old archive was removed. A 2-day-old archive, `keepme.txt` and a non-matching `old-notes.tar.gz` were kept.
- A bad `--keep-days` value, an invalid name (`a;b`), no arguments and a missing service directory each failed with the expected non-zero status. No temporary directory was left behind.

My first version of the prune pattern silently matched nothing, because the default `find` regex dialect did not accept the repetition syntax. I switched to `-regextype posix-extended` and re-tested before finishing.

The script still uses `logs/` and `archives/` relative to the current directory, as before, so cron must keep running it from the repository root. The README now says so.
