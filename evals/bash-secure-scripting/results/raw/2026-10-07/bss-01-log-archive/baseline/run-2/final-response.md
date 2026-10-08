`bin/archive-logs.sh` now takes several service names and a `--keep-days N` option, and prints a one-line summary. I tried it on a few test archives, then deleted them, so only the script and the README are changed.

- **Usage:** `bin/archive-logs.sh [--keep-days N] SERVICE [SERVICE...]`. Every service name and the `--keep-days` value are checked before anything is archived, so a bad argument stops the run with nothing written.
- **Pruning:** after the new archives are in place, `--keep-days N` deletes archives older than N days. It only touches files named `SERVICE-YYYYMMDD.tar.gz` for the services named in that run, so other services' archives and unrelated files are left alone. If you'd rather prune every archive in `archives/`, say so and I'll widen it.
- **Summary:** the output looks like `archived 2 service(s): api web; pruned 1 archive(s) older than 30 days`. The "pruned" part only appears when `--keep-days` is given.
- **Test run:** with a 40-day-old `api` archive and a 5-day-old `web` archive, `--keep-days 30 api web` removed only the old one. A bad name like `../x` was rejected with exit code 2.
- **Other changes:**
  - The script now stops on errors (`set -euo pipefail`).
  - Variables are quoted.
  - It uses a private temp directory that is cleaned up on exit.
  - Service names are restricted to letters, digits, `.`, `_` and `-`.
  - It creates `archives/` if it's missing.
- **README:** it now describes the new usage, the pruning scope and an example.

Running the same service twice in one day still overwrites that day's archive, as before.
