`bin/clean-workspaces.sh` now takes the workspace root and the age threshold as options and has a `--dry-run` mode. The README documents all of it. I tested it against a temporary directory, not your real `workspaces/`. The `--dry-run` run with the defaults on `workspaces/` printed nothing, so none of its three directories counted as stale.

- **Options:** `-r/--root DIR` defaults to `workspaces`, `-d/--days N` defaults to `7`, `-n/--dry-run` and `-h/--help`. Both `--root DIR` and `--root=DIR` forms work. With no arguments it behaves as before.
- **Dry run:** it prints `would remove <dir> (age Nd)` for each stale directory and deletes nothing.
- **Bad input:** a non-integer `--days`, a missing root directory or an unknown option exits with status 2 and an error message.

In my temporary-directory test, the dry run listed the 20-day-old directories without touching them. A real run then removed them and left the fresh directory and the symlink alone. A bad `--days` value exited with status 2.

I also fixed three problems in the original script along the way:
- **Names with spaces:** it looped over `ls` output, so a directory like `old build 2024` in your `workspaces/` would have been split into separate words. It now uses `find -print0`.
- **Empty workspaces:** an empty workspace crashed the age calculation. It now falls back to the directory's own modification time.
- **Symlinks:** symlinks under the root are now skipped, and removal is `rm -rf -- "$dir"`.

One behaviour changed: the old script removed `dir/*` and then ran `rmdir`, which left a directory behind if it held dotfiles. It now removes the whole directory.
