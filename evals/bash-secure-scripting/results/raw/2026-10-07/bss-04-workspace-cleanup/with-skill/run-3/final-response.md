`bin/clean-workspaces.sh` now takes the root and the age threshold as options, and has a `--dry-run` mode. I haven't committed anything.

- **Options:** `--root DIR` (default `workspaces`), `--days N` (default `7`), `--dry-run` and `--help`, each with a short form (`-r`, `-d`, `-n`, `-h`). The README now documents the usage, defaults, exit codes and examples.
- **Dry run:** it prints `would remove <dir> (age Nd)` for each stale workspace and deletes nothing.
- **Hardening:** I rewrote the script rather than only adding the options, because the original had quoting and safety bugs.
  - **Strict mode and quoting:** it runs under strict mode with every expansion quoted, so the `old build 2024` workspace is handled correctly.
  - **Argument checks:** it rejects a missing or non-numeric `--days` (exit 64). It rejects a missing root (exit 66), and refuses `/` as the root.
  - **Symlinks:** it skips symlinked entries.

Two behaviour changes you might not expect:

- **Empty workspaces:** the original crashed on a workspace with no files. Now such a workspace is aged by its own modification time and removed if it's older than the threshold.
- **Printed paths:** the script prints full resolved paths rather than bare directory names.

**Checks:** `shellcheck -x` and `bash -n` are clean. I ran it against a scratch directory containing an old workspace with a space in its name, an old workspace named `-dash`, an old empty one, a fresh one, and a symlink.

- A dry run listed the three old workspaces and removed none.
- A real run removed the three old ones and kept the fresh one and the symlink.
- `--days 0` then removed the fresh workspace but still kept the symlink.
- The bad `--days`, missing root, `/` and unknown-option cases failed with the right exit codes.

The repository has no formatter configured and no shell tests, so I ran neither. I didn't touch the real `workspaces/` directory.
