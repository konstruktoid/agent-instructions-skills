`bin/clean-workspaces.sh` now takes the root and age threshold as options and has a `--dry-run` mode. I haven't committed anything.

- **Options:** `-r`/`--root DIR` (default `workspaces`), `-d`/`--days N` (default `7`), `-n`/`--dry-run` and `-h`/`--help`. Dry-run prints `would remove <dir> (age Nd)` and deletes nothing.
- **Validation:** `--days` must be a non-negative integer, and the root must exist and not resolve to `/`. Bad input exits with 64 or 66, and the README lists the exit codes.
- **Rewrite:** The old script would have broken on the `old build 2024` workspace, whose name has spaces. It parsed `ls`, left variables unquoted and had no strict mode. It now has strict mode and a fixed `PATH`. It also lists directories with `find -print0`, quotes everything, and calls `rm -rf --` on each one. A failed removal is reported, the run continues, and it exits 1 at the end.
- **Behaviour changes:**
  - Symlinks in the root are skipped, so a link can't send the deletion outside the root.
  - An empty workspace is aged by its own mtime. Before, it produced an error.
- **Checks:** `shellcheck -x` and `bash -n` are clean. There's no `shfmt` installed and the repo has no formatter config, so I didn't run one. I ran the script against a scratch directory, not the real `workspaces/`:
  - Dry-run removed nothing.
  - `--days 40` kept everything.
  - A real run removed the old directory with spaces in its name and the empty old one.
  - It left alone a recent directory and a symlink pointing at an old directory outside the root.
  - Bad `--days`, a missing root and a missing option value each exited non-zero.
- **README:** It now documents the options, defaults, examples and exit codes. It no longer says each worker needs its own copy.

The three fixture workspaces in the repo all have today's mtime, so the real `workspaces/` has nothing stale. I tested on scratch copies with backdated files instead.
