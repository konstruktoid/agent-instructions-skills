I rewrote `bin/archive-logs.sh` and updated the README. `shellcheck -x` and `bash -n` are clean. I ran the script in a scratch copy and the checks below behaved as expected. `shfmt` isn't installed, so I didn't run it, and the repo has no formatter config.

**New usage**
```
bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]
```
- **Multiple services:** each name gets its own `archives/SERVICE-YYYYMMDD.tar.gz`. Repeated names are archived once.
- **`--keep-days N`:** after all new archives are in place, it deletes `archives/*.tar.gz` files older than N days. It also accepts `--keep-days=N`. Without the option nothing is deleted. If any archive fails, nothing is pruned.
- **Summary line:** on success it prints one line, for example `archived 2 service(s): api web; pruned 1 archive(s) older than 7 day(s)`.

**Other changes**
- Before anything is archived or deleted, it checks that `N` is a non-negative integer, that each service name is safe (`^[A-Za-z0-9][A-Za-z0-9._-]*$`) and that its log directory exists. Names like `../etc` are rejected.
- It exits 64 for bad usage or names and 66 for a missing log or archive directory. Errors go to stderr.
- It now runs with strict mode and a fixed `PATH`, and quotes everything the old version left unquoted.
- The temporary directory is now created inside `archives/` instead of `/tmp`, so the final move is an atomic rename. It is removed on exit and on INT/TERM.
- The README describes the usage, the options, the exit codes and the summary line.

**What I ran:** two services at once, a duplicate name, pruning that removed a 30-day-old file while keeping the new ones, `--` handling, and each failure path (bad name, bad N, missing service, no arguments). The failure paths exit non-zero with a message, and the archives directory held only the expected files afterwards.

**Things to know**
- `LOG_ROOT` and `RETENTION_DIR` are still relative to the working directory, as before. The cron job must `cd` to the repo first.
- Pruning looks at file modification time and covers every `*.tar.gz` in `archives/`, not just the services named in that run.
- I did not set a `umask`, so archive permissions are unchanged.
