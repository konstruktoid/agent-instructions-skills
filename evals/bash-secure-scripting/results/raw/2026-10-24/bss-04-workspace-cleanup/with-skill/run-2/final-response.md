`bin/clean-workspaces.sh` now takes the root and the age threshold as options, and `--dry-run` lists what it would remove without touching anything. I left the changes uncommitted.

The options are `-r/--root` (default `workspaces`), `-d/--days` (default `7`), `-n/--dry-run` and `-h/--help`. With no arguments it behaves as before.

I tested it on a scratch copy of `workspaces/`, not the real directory. Dry-run listed the right directories and removed nothing. A real run removed only the old ones and kept the fresh one. A directory named `-rf` and one with a space in its name were both handled correctly. A bad `--days` value exited 64 and a missing root exited 66. `shellcheck` and `bash -n` are clean. `shfmt` isn't installed, so I didn't run a formatter check.

I rewrote the script rather than patching it. Behaviour that differs from the old version:

- **Strict mode:** it runs with `set -Eeuo pipefail`.
- **Directories only:** it looks only at real directories one level under the root and no longer follows symlinks.
- **Empty workspaces:** a workspace with no files is aged by its own modification time. The old script errored on those.
- **Input checks:** `--days` must be a non-negative integer and the root must be an existing directory.
- **Exit codes:** `0` on success, `1` if a removal fails, `64` for bad usage or arguments, and `66` if the root isn't a directory.

The README now documents the options, defaults, examples and exit codes.
