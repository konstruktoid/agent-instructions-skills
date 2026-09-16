Clean shellcheck run (no output, no issues). Fixture directories are untouched — all testing ran against a scratch temp copy.

Files changed: `bin/clean-workspaces.sh`, `README.md`.

- Root and age threshold are now `--root`/`--days` flags (defaulting to `workspaces` and `7`), plus `--dry-run`.
- Rewrote the iteration to use a `*/` glob with quoted variables instead of unquoted `ls` word-splitting, which was silently broken on the `old build 2024` fixture directory (space in name).
