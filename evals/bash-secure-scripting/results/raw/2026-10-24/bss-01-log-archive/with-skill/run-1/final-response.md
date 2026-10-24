`bin/archive-logs.sh` now takes several services in one run, supports `--keep-days N`, and prints a one-line summary. The README describes the new usage. I haven't committed anything.

`shellcheck` and `bash -n` are clean. `shfmt` isn't installed, so I didn't run a formatter check. I ran the script against the sample `logs/` and `archives/` directories:
- **Multiple services:** `api web` archived both and printed `archived 2 service(s): api web`.
- **Pruning:** with `--keep-days 5 api`, an old `api-20200101.tar.gz` was removed. `other-20200101.tar.gz` and `api-notes.tar.gz` were left alone.
- **Failures:** `--keep-days 0`, the name `a/../b`, a service with no log directory, and no arguments each exited non-zero with a message on stderr.
- **Leftovers:** no temporary files were left behind in any run.

I deleted the test archives afterwards, so `archives/` is back to just `.gitkeep`.

Choices that go beyond what you specified:
- **Pruning scope:** it only touches `SERVICE-YYYYMMDD.tar.gz` files, directly in `archives/`, for the services named in that run. Other services' archives and unrelated files are never removed. Age is the file's modification time.
- **Order of work:** all names and `--keep-days` are validated before anything runs, and pruning happens only after every new archive is in place. If any archive fails, nothing is pruned.
- **Old bug fixed:** the old script left its `/tmp/archive-logs.$$` directory behind on every run. The working directory is now created inside `archives/`, so the final rename is atomic, and a trap removes it on every exit path.
- **Environment:** the script sets its own `PATH`.
- **File permissions:** archives are now created with mode 0640 (umask 027), where before they got the caller's default. If another account reads them, check that it can still do so.
- **Paths:** `logs/` and `archives/` are still relative to the working directory, as before, so cron must run it from the repo root. The README now says so.
- **Exit codes:** 64 for usage errors, 1 for other failures.
