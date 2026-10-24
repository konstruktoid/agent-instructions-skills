I've extended `bin/archive-logs.sh` to take several services and a `--keep-days N` option, and it now prints a one-line summary. I also updated the README.

I tested it by hand. `bin/archive-logs.sh --keep-days 30 api web` created both archives and deleted a 40-day-old test archive I'd planted. The output was `archived 2 service(s): api web; pruned 1 archive(s) older than 30 days`. A bad name like `../x` was rejected with exit code 2. I removed the test files afterwards and didn't test a failing archive.

- **Several services:** `bin/archive-logs.sh api web` archives each one. Archives are still named `SERVICE-YYYYMMDD.tar.gz` under `archives/`.
- **Pruning:** after the new archives are written, `--keep-days N` deletes `*-YYYYMMDD.tar.gz` files in `archives/` older than N days. This covers all services, not only the ones named in that run. If any service fails to archive, pruning is skipped.
- **Summary line:** without `--keep-days` the line is just `archived 2 service(s): api web`.
- **Exit code:** it exits non-zero if any service failed, and 2 for usage errors.
- **README:** it now describes the new usage, the pruning rule, the summary line and the exit codes.

I also tightened a few things beyond what you asked, since this runs from cron:

- **Name checks:** service names are validated before anything runs. Only letters, digits, `.`, `_` and `-` are allowed, and the service's `logs/` directory must exist.
- **Temp directory:** it uses `mktemp -d` and removes it on exit.
- **Quoting:** all variables are quoted.
