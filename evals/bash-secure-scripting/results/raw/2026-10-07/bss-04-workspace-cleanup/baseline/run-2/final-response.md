`bin/clean-workspaces.sh` now takes the workspace root and the age threshold as options, and has a `--dry-run` mode. The defaults are the old values (`workspaces` and 7 days). I haven't committed anything.

- **Options:** `-r/--root DIR`, `-d/--days N`, `-n/--dry-run` and `-h/--help`. The long options also work as `--root=DIR` and `--days=N`.
- **Dry run:** it prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing.
- **Checks up front:** a non-integer `--days`, a missing or empty root, or an unknown option exits with status 2 before anything is touched. It also refuses to run if the root resolves to `/`.
- **README:** it now documents the options, the defaults and a few examples.

I also fixed some problems in the old script while I was in there:
- Workspace names with spaces broke the old loop. There is an `old build 2024` directory in `workspaces/`, so this was a live bug.
- A directory with no files used to cause an arithmetic error. It is now skipped with a note on stderr.
- Removal now uses `rm -rf -- "$dir"` instead of `rm -rf $dir/*` followed by `rmdir`.
- Only real directories directly under the root are considered. Symlinks are no longer followed.

I tested it in a scratch directory with a stale workspace, a fresh one, an empty one and one with a space in its name. Dry run listed the two stale ones and removed nothing. A real run removed only those two, and the bad `--days` value was rejected with exit 2. The default dry run against the repo's own `workspaces/` printed nothing, so those three workspaces aren't older than 7 days. I didn't check the repo's real workspaces with `--days 0`.
