`bin/clean-workspaces.sh` now takes the workspace root and age threshold as arguments and has a `--dry-run` mode. I ran it against a temporary directory. The dry run listed the stale workspaces without deleting them. The real run removed them, including one with a space in its name, and kept the fresh one. I didn't run it against the repo's own `workspaces/` directory.

The usage is `bin/clean-workspaces.sh [-n|--dry-run] [WORKSPACE_ROOT [DAYS]]`. The defaults are still `workspaces` and `7`. In dry-run mode each stale workspace is printed as `would remove <dir> (age Nd)`.

I also tightened a few things in the script beyond what you asked for:
- **Input checks:** it rejects a non-numeric `DAYS`, a missing root, and `/` as the root, and it exits with a usage message on bad arguments.
- **Quoting:** paths are quoted and passed to `rm -rf` after `--`, so names with spaces or leading dashes are safe. The old `for dir in $(ls)` would have broken on spaces.
- **Empty workspaces:** an empty workspace directory used to cause an arithmetic error. It is now aged by the directory's own modification time.
- **Symlinks:** only real directories directly under the root are considered, so symlinks are skipped.

The README documents the arguments, the defaults and a few examples.

I haven't committed anything.
