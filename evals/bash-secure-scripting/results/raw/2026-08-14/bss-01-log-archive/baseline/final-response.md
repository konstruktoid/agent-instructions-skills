I've extended `bin/archive-logs.sh` and verified it end-to-end:

- **Multiple services**: accepts any number of trailing service-name arguments, archives each into `archives/SERVICE-YYYYMMDD.tar.gz`, stopping with a clear error on unknown/invalid names (rejects empty, `.`, `..`, and anything containing `/` to prevent path traversal).
- **`--keep-days N`**: prunes each requested service's older archives via `find -mtime +N -delete`, only after all new archives for the run are safely written. Validates `N` is a non-negative integer.
- **One-line summary**: e.g. `archived 2 service(s) (api web) to archives as of 20260814`.
- Hardened with `set -euo pipefail`, `mktemp -d` (instead of predictable `/tmp/archive-logs.$$`) with an `EXIT` trap for cleanup, and quoted variables throughout.

Tested: multi-service run, no-args usage, path-traversal rejection, missing-service error, invalid `--keep-days` value, and actual pruning (confirmed old dated archives get removed while same-day archives are kept, and unrelated files are untouched). Cleaned up test-generated tarballs afterward so the working tree only shows the script change.

README updated to document the new multi-service + `--keep-days` usage with an example.
