`bin/clean-workspaces.sh` now takes the root and the age threshold as arguments, and has a `--dry-run` mode. I tested it against a temp directory with an old workspace, a fresh one and an empty one.

- **Arguments:** `-r/--root DIR` defaults to `workspaces`, and `-d/--days N` defaults to `7`, so running it with no arguments behaves as before. `-h/--help` prints usage.
- **Dry run:** `-n/--dry-run` prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing. I checked that the directories were still there afterwards.
- **Real run:** it removed only the old workspace (whose name had a space) and the old empty one, and kept the fresh one. A non-numeric `--days` exits with status 2 and an error.
- **Not run:** I ran the dry run once with the defaults against the repo's `workspaces/`, but that printed nothing, so the age check there is untested. The three workspaces in the repo are unchanged.
- **README:** it now documents the options, defaults and examples.

I also fixed some problems in the old script while rewriting it:
- Workspace names with spaces or glob characters are handled properly. The old unquoted `$dir` and `$(ls)` would have broken on `workspaces/old build 2024`.
- Each workspace is now removed with `rm -rf -- "$dir"`. The old `rm -rf $dir/*` followed by `rmdir` left dotfiles behind and then failed.
- An empty workspace no longer causes an arithmetic error. It is aged by the directory's own modification time instead.
- The script refuses to run with an empty root or `/`.
- It now stops on errors (`set -euo pipefail`).

Absolute paths are now printed, because the root is resolved before scanning (the old script printed bare directory names). Say if you'd rather keep the short names.

I haven't committed anything.
