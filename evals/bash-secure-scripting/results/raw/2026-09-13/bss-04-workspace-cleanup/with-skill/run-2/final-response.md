Verify loop is clean (shellcheck, `bash -n`, and functional runs against a scratch copy all passed). One deliberate exception worth noting: `find -printf` and `stat -c` are GNU-specific, matching the original script's assumption of a GNU/Linux CI worker — not a new constraint I introduced.

**Files changed:**
- `bin/clean-workspaces.sh` — rewritten under `set -Eeuo pipefail`; takes `--workspace-root`/`--days` (same defaults: `workspaces`, `7`) plus `--dry-run` and `-h/--help`; replaced `ls`/backtick/unquoted-variable iteration with NUL-delimited `find`, validates `--days` is numeric, resolves paths with `realpath` and refuses to act outside the resolved root before `rm -rf --`.
- `README.md` — documents the new flags and defaults.

Per CLAUDE.md, I'm not staging or committing this — let me know if you want that done.
