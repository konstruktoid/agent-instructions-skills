`bin/clean-workspaces.sh` now takes the root and age threshold as arguments and has a `--dry-run` mode, and the README documents all three. I tested it on a temporary copy of `workspaces/` with some files back-dated 30 days. I haven't committed anything.

**Usage**
```
bin/clean-workspaces.sh [-n|--dry-run] [-r|--root DIR] [-d|--days N]
```
- `--root` defaults to `workspaces` and `--days` defaults to `7`, so running it with no arguments behaves as before. `--root=DIR` and `--days=N` work too, and `-h` prints usage.
- `--dry-run` prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing.
- Bad input exits with status 2 and a message: a non-integer `--days`, a root that isn't a directory, or an unknown option.

**Test results**
- **Dry run:** it listed the two back-dated workspaces and left all four directories in place.
- **`--days 100`:** it removed nothing.
- **Real run:** it removed only the two stale workspaces, and the fresh one and the empty one were kept.
- **Checked-in `workspaces/`:** a dry run listed nothing, because those files are recent.

**Other changes to the script**
- It now uses `set -euo pipefail` and quotes every path. The old version split on whitespace, so it would have broken on the existing `old build 2024` directory.
- It deletes each stale workspace with `rm -rf -- "$dir"`. The old `rm -rf $dir/*` followed by `rmdir` left a workspace behind if it held dotfiles.
- It only looks at real directories, so it never follows a symlink.
- It skips directories with no files, because there is nothing to date them by. The old script threw an arithmetic error on those.
