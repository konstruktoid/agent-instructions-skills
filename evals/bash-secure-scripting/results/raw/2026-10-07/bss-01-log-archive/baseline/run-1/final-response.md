`bin/archive-logs.sh` now takes several service names and a `--keep-days N` option, and it prints a one-line summary. I ran it once with `--keep-days 30 api web`. It printed `archived 2 service(s): api web; pruned 0 archive(s) older than 30 days`, and both tarballs appeared in `archives/`. I deleted those two test tarballs afterwards. The pruning itself isn't tested, because no archive was old enough to delete.

- **Usage:** `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`.
- **Pruning:** it runs only after every new archive is in place, so a failed run never deletes old archives. It deletes files in `archives/` named `*-YYYYMMDD.tar.gz` that are older than N days by modification time. That covers archives for every service, not only the ones named in this run.
- **Summary:** without `--keep-days` the line has no pruning part, e.g. `archived 2 service(s): api web`.
- **Validation:** all names and N are checked before anything is archived. A name must be letters, digits, `.`, `_` or `-`, so `../x` is rejected with exit code 2. A service with no directory under `logs/` aborts the run with exit code 1.
- **Hardening:** I also rewrote the old script's fragile parts, which weren't part of your request. It now stops on the first error, quotes every variable and uses a private temp directory that is always cleaned up.
- **README:** it now describes the new usage, the pruning behaviour and the name rules, with an example.

If the nightly cron entry calls the script, it still works for one service. `--keep-days` is optional, so pruning stays manual until you add it.
