`bin/archive-logs.sh` now takes several service names in one run. It also has a `--keep-days N` option and prints a one-line summary. I haven't committed anything.

I checked it with `shellcheck` and `bash -n`, both clean. I ran it in a scratch copy:
- **Success path:** it archived two services and pruned one backdated archive. A fresh archive was kept.
- **Failure paths:** an invalid name, a non-numeric `--keep-days` value, no arguments and a missing log directory each stopped with an error and a non-zero exit. No temp directories were left behind.
- **Not run:** `shfmt` isn't installed here, and the repo has no formatter config or tests.

- **Usage:** `archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`.
- **Pruning:** `--keep-days N` runs only after every new archive is in place, and it deletes `archives/*.tar.gz` files whose modification time is more than N days old. It deletes archives for any service, not only the ones named in that run. Without the option nothing is deleted.
- **Summary line:** for example `archived 2 service(s): api web; pruned 1 archive(s) older than 30 day(s)`. The `pruned` part appears only with `--keep-days`.
- **Exit codes:** 64 for bad usage or invalid input, 1 for other failures such as a service with no log directory.
- **Hardening:** all names are validated before anything is written, so one bad name archives nothing. The script now has strict mode and its own `PATH` and `umask`, and it cleans up its temp directory when interrupted. The old `/tmp/archive-logs.$$` and unquoted variables are gone. The temp directory is now inside `archives/` so the final move is atomic.
- **README:** it describes the new usage, options, summary line and exit codes.

`logs/` and `archives/` are still relative to the current directory, as before, so cron must start the script from the repo root. The README says so.

If one service fails partway through a multi-service run, the services already archived stay in place. Nothing is pruned, and the script exits non-zero.
