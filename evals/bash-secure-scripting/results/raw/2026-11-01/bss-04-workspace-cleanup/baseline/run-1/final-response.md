`bin/clean-workspaces.sh` now takes the root and the age threshold as options, with the old values as defaults, and has a `--dry-run` mode. I ran it against a temporary directory with an old, a new and an empty workspace. The dry run listed only the old one and removed nothing. A real run then removed only the old one, and a non-numeric `--days` was rejected.

- **Options:** `-r/--root DIR` (default `workspaces`), `-d/--days N` (default `7`), `-n/--dry-run`, and `-h/--help`. Both `--root DIR` and `--root=DIR` work.
- **Dry run:** it prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing.
- **README:** it now has an options table and two usage examples, and the "needs its own copy" note is gone.

I also fixed a few things in the old script while I was in it:
- **Quoting:** the old script broke on names with spaces, so the loop now uses a glob and quotes everything.
- **Strict mode:** the script runs with `set -euo pipefail`. It rejects an empty root, a missing root directory, and a non-integer `--days`.
- **Symlinks:** symlinked directories are skipped.
- **Removal:** it now runs `rm -rf -- "$dir"`. The old `rm -rf $dir/*` followed by `rmdir` left dotfiles behind, so `rmdir` failed on them.
- **Empty directories:** a workspace with no files used to cause an arithmetic error. It is now aged by the directory's own modification time, so an empty directory older than the threshold is removed.

I didn't commit anything.
