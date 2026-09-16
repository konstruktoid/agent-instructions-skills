`bin/archive-logs.sh` and `README.md` were changed; test artifacts in `archives/` were removed and the tree is clean.

Summary of the script changes:
- Accepts multiple service names in one invocation, plus an optional `--keep-days N` (also `--keep-days=N`).
- Adds `set -euo pipefail`, quotes all variable expansions, and switches the temp dir from a predictable `/tmp/archive-logs.$$` to `mktemp -d` with a `trap` cleanup on exit — the old approach was a symlink/race hazard in shared `/tmp`.
- Validates each service has a `logs/<service>` directory before archiving, and validates `--keep-days` is a non-negative integer.
- After archiving, if `--keep-days` is set, prunes each named service's own older archives (`find … -mtime +N -delete`), scoped to the services passed in that run so it never touches archives for services not requested.
- Prints one summary line, e.g. `archived 2 service(s) [api,web] to archives`.

Verified with `bash -n`, `shellcheck` (clean), and manual runs: multi-service archiving, missing-service error path, no-args usage path, and `--keep-days` pruning (confirmed a 40-day-old archive was deleted at `--keep-days 30` while a 5-day-old one was kept).

README now documents the new `[--keep-days N] SERVICE [SERVICE...]` usage and the pruning behavior.
