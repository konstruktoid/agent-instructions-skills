`bin/clean-workspaces.sh` now takes the root and the age threshold as options, and it has a `--dry-run` mode. The README documents all three.

```
bin/clean-workspaces.sh [-n|--dry-run] [-r|--root DIR] [-d|--days N]
```

- **Defaults:** the root is still `workspaces` and the threshold is still 7 days, so a call with no arguments behaves as before.
- **Dry run:** `--dry-run` prints `would remove <dir> (age Nd)` for each workspace and deletes nothing.
- **Bad input:** a non-numeric `--days`, a missing root directory, or an unknown option exits with status 2 and an error message.

I also fixed several problems in the old script while I was in it. It would have been unsafe to build the new options on top of them.
- **Quoting:** the old script didn't quote its variables. The repo's own `workspaces/old build 2024` would have been split into several words.
- **Failed `cd`:** it ran `cd` without checking the result. If the root was missing, it would have run in whatever directory the caller was in.
- **Removal:** it deleted with `rm -rf $dir/*`, which skipped dotfiles, followed by `rmdir`. It now uses `rm -rf -- "$dir"`.
- **Empty workspaces:** a workspace with no files made the old age calculation fail. It now uses the directory's own modification time.
- **Symlinks:** symlinked workspaces are now skipped.

I tested it in a temporary directory with an old workspace whose name contains a space, a fresh one and an empty old one. The dry run listed the two old ones and removed nothing. A real run removed those two and kept the fresh one. `--days 30` removed nothing. `--root=DIR` and `--days x` also behaved as expected. A dry run against the repo's real `workspaces/` listed nothing, because all three entries are recent. I didn't run a real deletion there.
