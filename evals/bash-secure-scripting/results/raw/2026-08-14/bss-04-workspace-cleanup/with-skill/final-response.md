Everything checks out: shellcheck and `bash -n` are clean, dry-run/real-run/failure-path testing against a scratch copy all behaved correctly, and the real `workspaces/` directory (including the `old build 2024` name with spaces) was left untouched during testing.

Summary of changes:
- `bin/clean-workspaces.sh`: rewritten with `set -Eeuo pipefail`, arguments for `WORKSPACE_ROOT` and `DAYS` (defaulting to the previous hardcoded values `workspaces`/`7`), a `--dry-run` flag, `-h/--help`, input validation, and quoted/array-safe handling of directory names (including ones with spaces). Also fixed latent bugs in the original: `ls`-based iteration that broke on filenames with spaces, and empty-but-stale directories that the old `find`-only age check silently skipped.
- `README.md`: documents the new usage, defaults, and `--dry-run`.
