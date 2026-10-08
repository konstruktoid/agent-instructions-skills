`bin/archive-logs.sh` now takes several service names in one run, and `--keep-days N` prunes old archives afterwards. I tried it by hand against the sample `logs/` directory. There's no test suite, so those runs are the only checking it has had. I haven't committed anything.

- **Usage:** `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`. `--keep-days=N` also works.
- **Summary line:** it prints something like `archived 2 service(s): api web; pruned 1 archive(s) older than 5 days`. The pruned part only appears when `--keep-days` is given.
- **Pruning:** it runs only after every new archive is in place. It deletes only files in `archives/` named `*-YYYYMMDD.tar.gz` that are older than N days by modification time. `.gitkeep` and anything else there are left alone.
- **Validation:** all service names and the `--keep-days` value are checked before anything is written. A bad name, a service with no logs, or a non-integer N stops the run with nothing archived. Names containing `/` or `..`, or starting with `-`, are rejected.
- **Failures:** the script stops at the first error and exits non-zero. The old script kept going after failures.
- **Temp files:** these are now created inside `archives/` instead of `/tmp`, and are cleaned up on exit. The old `rm -rf $TMP/*` is gone.

In my runs, two services archived together, a 10-day-old test archive was pruned with `--keep-days 5`, and `x`, `../x` and an empty N were all rejected. I removed the test archives afterwards.

The script still uses paths relative to the current directory, as before, so it has to run from the repo root. I noted that in the README.

The README now documents the new usage, the validation behaviour and the summary line.
