`bin/archive-logs.sh` now takes several service names and has a `--keep-days N` option. It prints a one-line summary when it finishes. I ran it in a scratch copy of the repo and it behaved as expected. I haven't run it from cron.

The README describes the new usage, with examples.

- **Several services:** `bin/archive-logs.sh api web` writes one dated tarball per service, as before.
- **Pruning:** `--keep-days 30` runs after the new archives are written. It deletes files in `archives/` named like `*-YYYYMMDD.tar.gz` that are more than 30 days old, judged by modification time. Without the option nothing is pruned.
- **Summary:** the output looks like `archived 2 service(s): api web; pruned 1 archive(s) older than 30 days`. The "pruned" part only appears when `--keep-days` is given.
- **Whole directory:** pruning covers every service's archives in `archives/`, not only the services named on that run. If you'd rather limit it to the named services, say so and I'll change it.
- **Validation first:** all service names are checked before anything is archived. A name that is invalid (such as `../x`) or has no `logs/<service>` directory makes the script exit non-zero without archiving any service. `--keep-days` must be a non-negative integer.
- **Not requested:** the old script left the temp directory behind and ran with no error handling. It now stops on the first error and cleans up its temp directory on exit. Paths are quoted, so names with unusual characters can't cause trouble.

In the test I made a 40-day-old archive. `--keep-days 30` with `api web` created both tarballs and removed the old one. Passing `nope` and `../x` was rejected.
