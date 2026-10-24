`bin/archive-logs.sh` now takes several services, supports `--keep-days N`, and prints a one-line summary. I ran it in a scratch copy and the checks below behaved as expected. I haven't committed anything.

The new usage is `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`. `--keep-days` has to come before the service names, and `--keep-days=N` also works.

- **Several services:** each one gets its own `SERVICE-YYYYMMDD.tar.gz` in `archives/`. All names are checked before anything is archived, so an invalid name or a missing `logs/SERVICE` directory aborts the whole run.
- **Pruning:** after all the new archives are written, it deletes archives older than N days. It only considers files named `SERVICE-YYYYMMDD.tar.gz` for the services given in that run. Other services' archives and any other files in `archives/` are left alone.
- **Summary:** a run prints something like `archived 2 service(s): api web; pruned 1 archive(s) older than 5 days`. The pruned part only appears when `--keep-days` is given.
- **README:** it now describes the usage, the validation, the pruning rules and the summary line.

I also fixed some problems in the original script while I was in there:
- **Service names:** the original passed them straight into paths, so a name like `../x` could reach outside `logs/`. Names are now restricted to letters, digits, `.`, `_` and `-`.
- **Temp directory:** it was a predictable `/tmp/archive-logs.$$`. It's now a private `mktemp` directory inside `archives/`, removed on exit, so the final move is an atomic rename.
- **Errors:** the script now stops on the first error instead of carrying on.
- **Quoting:** variables are quoted throughout.

I ran it on a copy with `api` and `web`. Both archives were created and a 10-day-old `api` archive was pruned. An old `other-*` archive survived, as intended. `../x` and a non-numeric `--keep-days` were both rejected with exit code 2. I didn't test a missing log directory or `--keep-days=N`.
