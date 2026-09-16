Working tree is clean of test artifacts now — only the intended edits remain.

`bin/archive-logs.sh` and `README.md` changed. The script now takes multiple `SERVICE` arguments plus an optional `--keep-days N`, validates names against an allowlist before archiving anything, uses `mktemp -d` with EXIT/INT/TERM traps, prunes per-service archives by mtime after the new ones land, and prints a one-line summary. `shellcheck` and `bash -n` are clean; verified a multi-service run, `--keep-days` pruning an old archive, four failure paths (missing args, invalid name, missing log dir, bad `--keep-days` value) with correct exit codes, and a SIGTERM mid-run (exit 143, no leaked temp dir).

Since I've reported the change and it's accepted, `/clear` before starting anything unrelated.
