`bin/clean-workspaces.sh` now takes the workspace root and the age threshold as options. It also has a `--dry-run` mode, and the README documents all of it. I haven't committed anything.

- **Options:** `-r/--root DIR` defaults to `workspaces` and `-d/--days N` defaults to `7`, so running it with no arguments behaves as before. `-n/--dry-run` prints `would remove <name> (age Nd)` for each stale directory and removes nothing. `-h/--help` prints usage.
- **Validation:** `--days` must be a non-negative integer, and a missing or non-directory root is an error. A root of `/` is refused. Usage errors exit 64 and a bad root exits 66.
- **Strict mode:** the script now starts with `set -Eeuo pipefail`.

I also fixed some problems in the old logic while I was there:
- **Filenames:** the old `for dir in $(ls)` loop broke on names with spaces, like `old build 2024` in your own `workspaces/`. It now uses a quoted glob.
- **Hidden files:** the old `rm -rf $dir/*` followed by `rmdir` left directories behind if they held dotfiles. It now runs `rm -rf --one-file-system -- dir`.
- **Symlinks:** these are skipped, so a link can't send deletion outside the root.
- **Empty directories:** a directory with no files is now aged by its own modification time. Before, it caused an arithmetic error.

`shellcheck -x` and `bash -n` are clean. I didn't run a formatter check because `shfmt` isn't installed here, and the repo doesn't configure one.

I ran it against a scratch directory (since deleted). Dry-run listed the three old directories and removed nothing. The real run removed them, including `a b` and `-dash`, and left the fresh directory and the symlink. A non-numeric `--days`, a missing root and `--root` with no value each failed with a message on stderr and a non-zero exit. A dry-run against the repo's own `workspaces/` listed nothing, because those directories are all recent.

The README now has the usage, an options table, examples and exit codes. It also lists the new requirements: GNU `find` and Bash 4.4 or later.
