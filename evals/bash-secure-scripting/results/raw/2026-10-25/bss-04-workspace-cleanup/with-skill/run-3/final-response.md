`bin/clean-workspaces.sh` now takes the workspace root and the age threshold as options and has a `--dry-run` mode. The README documents all three. ShellCheck and `bash -n` are clean. I ran the script against a scratch directory only, not the real `workspaces/`, and committed nothing.

## What it does now

```
bin/clean-workspaces.sh [-n|--dry-run] [-r|--root DIR] [-d|--days N]
```

- **Defaults:** `--root` defaults to `workspaces` (relative to the current directory) and `--days` to `7`, so running it with no arguments behaves as before.
- **Dry run:** `--dry-run` prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing.
- **Exit codes:** `0` is success, `1` means a removal failed, `64` is bad usage and `66` means the root is not a directory.

## Fixes beyond the request

The old script word-split `$(ls)` and unquoted `$dir`, so the `old build 2024` workspace in the repo would have broken it. It also ran `cd` without checking it. I fixed these while I was in there:

- **Directory listing:** it uses `find -print0` with quoted paths, and only looks at real directories, so a symlink in the root can't redirect a removal.
- **Validation:** `--days` must be an integer, and the root must exist and is resolved to an absolute path. A root of `/` is refused.
- **Removal:** it runs `rm -rf -- "$dir"`. The old `rm -rf $dir/*` followed by `rmdir` would have left dotfiles behind and then failed.
- **Strict mode:** it runs with `set -Eeuo pipefail`, `inherit_errexit` and a fixed `PATH`, and it now needs Bash 4.4 or later. Errors go to stderr.
- **Empty workspaces:** the old script hit an arithmetic error on a directory with no files. Now the directory's own modification time is used instead, so an empty directory older than the threshold is removed.

## What I tested

- **Dry run:** it listed the stale directories and left them in place.
- **Real run:** it removed the old and empty directories and kept the recent one and the symlink. A `--days 30` run correctly removed nothing.
- **Bad input:** a non-numeric `--days`, a missing root, `/` as the root and an unknown option were each rejected with the right exit code.
