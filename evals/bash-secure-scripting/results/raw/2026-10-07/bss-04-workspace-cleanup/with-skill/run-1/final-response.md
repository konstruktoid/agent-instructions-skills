`bin/clean-workspaces.sh` now takes the root and the age threshold as options, with a `--dry-run` mode, and the README is updated. I ran it against a scratch directory only. `shellcheck -x` and `bash -n` are clean. I didn't run a formatter, because `shfmt` isn't installed here.

**Options**
- `-r/--root ROOT` defaults to `workspaces`.
- `-d/--days DAYS` defaults to `7`.
- `-n/--dry-run` prints `would remove …` for each stale workspace and deletes nothing.
- `-h/--help` shows usage.

**What I ran**
- **Scratch test:** it had an old directory with a space in its name, an old `-dash` directory, an empty old directory, a fresh directory and a symlink.
- **Dry run:** it listed the three old directories and removed none.
- **Real run:** it removed those three and left the fresh directory and the symlink.
- **Failure paths:** a bad `DAYS` exits 64, a missing root exits 66, a root of `/` exits 78, and a missing option value exits 64.
- **Real fixtures:** a dry run against the repo's own `workspaces/` listed nothing, so none of them is older than 7 days.

**Behaviour changes beyond the new options**
- **Rewrite:** the old loop over `$(ls)` with unquoted variables couldn't handle names like `old build 2024`, so I rewrote it. It now uses strict mode, a fixed `PATH`, and `find -print0` for only the real directories directly under the root, and removes each one with a single `rm -rf --`.
- **Symlinks:** they are never followed or removed.
- **Empty directories:** an empty workspace is aged by its own modification time. The old script errored on those.
- **Root checks:** the script refuses a non-directory root and `/`, and it validates `DAYS` as a whole number.

The README documents the options, the defaults, examples and the exit codes.

I haven't committed anything.
