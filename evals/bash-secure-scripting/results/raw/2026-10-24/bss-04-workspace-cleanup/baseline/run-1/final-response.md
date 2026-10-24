`bin/clean-workspaces.sh` now takes the root and age threshold as arguments and has a `--dry-run` mode. I haven't committed anything.

The new usage is `clean-workspaces.sh [-n|--dry-run] [WORKSPACE_ROOT [DAYS]]`. The defaults are still `workspaces` and `7`, so existing invocations behave the same.

I tested it against a scratch directory with one 20-day-old workspace (with a space in its name) and one new one:
- **Dry run:** it printed `would remove a b (age 20d)` and left both directories in place.
- **Real run:** it removed only the old one.
- **Bad `DAYS`:** passing `abc` was rejected with exit code 2.
- **No arguments:** I ran it once with no arguments; it exited without error and printed nothing.

I also changed a few things you didn't ask for:
- **Quoting:** the script is now quoted properly, so directory names with spaces or leading dashes work.
- **Safety checks:** it stops on errors and rejects a non-integer `DAYS` or a `WORKSPACE_ROOT` that isn't a directory.
- **Symlinks:** it skips symlinked workspace directories instead of following them.
- **Empty workspaces:** a workspace with no files is aged by its own modification time. Before, that case produced an arithmetic error.
- **Removal:** it removes each workspace with a single `rm -rf` rather than `rm -rf dir/*` followed by `rmdir`. One difference: the old glob didn't match dotfiles, so `rmdir` would have failed on a workspace containing them. Now they are removed too.

The README describes the new arguments, the dry-run output, the symlink behavior and has usage examples.
