`bin/clean-workspaces.sh` now takes the root and age threshold as arguments and has a `--dry-run` mode. I tested it on a temp copy of the workspaces with one file backdated 30 days.

- **Options:** `-r/--root DIR` (default `workspaces`), `-d/--days N` (default `7`) and `-n/--dry-run`. It also accepts `--root=DIR` and `--days=N`, and `-h` prints usage. With no arguments it behaves as before.
- **Dry run:** it prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing. In my test it listed only the backdated directory and left everything in place. A real run then removed only that one.
- **Argument checks:** a non-numeric `--days` or an unknown option exits with status 2 and a usage message. I checked the non-numeric `--days` case and not the others.
- **README:** it now documents the options, their defaults and an example.

I also changed some behavior while rewriting the loop:
- **Names with spaces:** the old script split directory names on whitespace, so a directory like `old build 2024` would have been mangled. It now handles them, and the test above used that exact name.
- **Symlinks:** symlinked directories are skipped instead of followed.
- **Empty workspaces:** directories with no files are skipped. Before, they caused an arithmetic error.
- **Deletion:** it now runs `rm -rf -- "$dir"` in place of the old `rm -rf $dir/*` followed by `rmdir`.

I haven't committed anything.
