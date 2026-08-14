Done. Summary of changes to `bin/archive-logs.sh`:

- **Multiple services per run**: accepts any number of `SERVICE` operands (`archive-logs.sh web api db`), each validated against an allowlist pattern before anything is touched.
- **`--keep-days N`**: after all requested services are archived, prunes each of those services' archives older than N days (via `find -mtime`, NUL-delimited, no `xargs`/shell re-parsing).
- **One-line summary**: prints `archived N service(s): path1, path2, ...` after a successful run.
- Hardened per the bash-secure-scripting baseline: `set -Eeuo pipefail` + `inherit_errexit`, cron-safe `PATH`/`umask`, `mktemp -d` with an `EXIT` trap (plus `INT`/`TERM` handlers) so no temp directory is ever left behind, quoted expansions/arrays throughout, and deliberate exit codes (64 usage, 65 invalid service, 66 missing directory).
- `--help`/`-h` and usage text, with help on stdout and errors on stderr.

Verification: `shellcheck` and `bash -n` both clean with zero suppressions; ran the script against scratch copies (never the real fixture data) covering the happy multi-service path, `--keep-days` pruning (confirmed old archives removed, new ones kept), invalid service name, missing log directory, bad `--keep-days` value, unknown option, and `--help` — checking exit codes, stdout/stderr separation, and confirming no leftover temp files after any path including failures.

README updated with the new usage, an example invocation, and a description of `--keep-days` semantics.
