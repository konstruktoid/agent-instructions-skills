`bin/clean-workspaces.sh` now takes the workspace root and age threshold as options, and has a `--dry-run` mode. `shellcheck -x` and `bash -n` both pass. I ran the script only against a scratch directory I created and then deleted, not against the repo's own `workspaces/` fixtures. There is no `shfmt` on this machine, so I did not check formatting.

- **Options:** `-r/--root DIR` defaults to `workspaces`. `-d/--days N` defaults to `7`. `-n/--dry-run` prints `would remove <name> (age Nd)` and deletes nothing. `-h/--help` shows usage. The README documents all of these, with examples and exit codes.
- **Fixes alongside the options:** the old script broke on directory names with spaces, such as `old build 2024`, and on names starting with `-`. It also followed symlinks and would have failed on a workspace with no files. It now handles names safely, ignores symlinks and warns and skips empty workspaces.
- **Safety checks:** `--days` must be a non-negative integer. The root must be an existing directory, and `/` is refused.
- **Strict mode and PATH:** it runs in strict mode and sets its own `PATH`.
- **Tested in a scratch directory:** dry-run listed the stale workspaces and removed nothing. A real run removed only the stale ones, including the names with a space and a leading `-`, and left the fresh one, the empty one and the symlink. Bad `--days`, a missing root and an unknown option each exited non-zero with a message on stderr.
- **Requires GNU tools:** the script needs GNU `find` and `realpath`, which the original already assumed for `find -printf`.

I didn't commit anything.
