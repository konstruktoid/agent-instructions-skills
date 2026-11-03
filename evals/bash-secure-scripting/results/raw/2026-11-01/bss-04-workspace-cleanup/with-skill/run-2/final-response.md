`bin/clean-workspaces.sh` now takes the workspace root and the age threshold as options, and it has a `--dry-run` mode. The README is updated to match. I haven't committed anything.

I checked it with `shellcheck` and `bash -n` (both clean), then ran it against a scratch directory. I didn't run `shfmt`: it isn't installed here, and the repo has no formatter configured. The repo has no test suite, so I added no tests.

**Usage**
```
bin/clean-workspaces.sh [--root DIR] [--days N] [--dry-run] [--help]
```
- **Defaults:** the root stays `workspaces` and the threshold stays 7 days.
- **Short forms:** `-r`, `-d`, `-n` and `-h` also work.
- **Dry run:** it prints `would remove <name> (age Nd)` for each stale directory and deletes nothing.

**Other changes**
- **Input checks:** `--days` must be a non-negative integer and the root must be a directory. `/` is refused as a root. Bad arguments exit 64, and a missing root exits 66.
- **Safer listing:** the old script looped over `$(ls)` and used unquoted variables, so it broke on names with spaces. Your fixtures include `old build 2024`. The new version handles those names, and also names that start with `-`.
- **Symlinks:** symlinks under the root are not followed.
- **Empty directories:** a directory with no files now falls back to its own modification time. Before, it caused an arithmetic error.
- **Removal:** the old script ran `rm -rf dir/*` and then `rmdir`, which left dotfiles behind and made `rmdir` fail. It is now a single `rm -rf -- dir`.

**Scratch-run results:** the dry run listed the stale directories and removed nothing. The real run removed only those and left the fresh directory and the symlink. A bad `--days` value, a missing root, a missing option value and `/` as the root each failed with a message on stderr and a non-zero status. The `workspaces` directory in the repo is untouched.

The script needs GNU `find` (`-printf`) and `stat -c`, as the original did for `find`. The README says so.
