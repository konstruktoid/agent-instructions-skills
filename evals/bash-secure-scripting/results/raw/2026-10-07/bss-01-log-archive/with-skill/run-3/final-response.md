`bin/archive-logs.sh` now takes several service names in one run, accepts `--keep-days N`, and prints a one-line summary. The README describes the new usage. I tested it in a scratch copy of the repo. `shellcheck -x` and `bash -n` were clean. I didn't run `shfmt` and didn't test the signal-handling path (the INT/TERM traps).

**What it does**
- **Usage:** `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`.
- **Checks first:** every service name and its `logs/SERVICE` directory is checked before anything is written. One bad name means no archives at all.
- **Pruning:** `--keep-days` runs only after all the new archives are in place. It removes only archives of the services named on that run, matching `SERVICE-YYYYMMDD.tar.gz`. Other services' archives are left alone.
- **Output:** one line, for example `archived 2 service(s): api web; pruned 3 archive(s) older than 30 days`. The `pruned` part appears only with `--keep-days`.
- **Exit codes:** 64 for usage errors, 66 for a missing log or archive directory.

In the scratch run, a 40-day-old `api` archive was pruned and the old `web` and `other` archives stayed. A missing service, `../x`, `--keep-days 0`, no arguments and an unknown option each failed with the right exit code.

**Behaviour changes from the original**
- **Scratch directory:** the old script's `mkdir /tmp/archive-logs.$$` is gone. Archives are built in a `mktemp -d` directory inside `archives/`, so the final `mv` is atomic, and a trap removes the directory on exit or on INT/TERM.
- **Unquoted variables:** these are now quoted, and the script sets its own `PATH` and `umask`.
- **Bash version:** it now needs Bash 4.4 or later, and the README says so.

Decision for you: I scoped pruning to the named services because the request didn't say. If you want `--keep-days` to prune every archive in `archives/`, say so and I'll change it.

Nothing is committed.
