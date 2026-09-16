Fixture data is untouched. Verify loop passed clean on attempt 1 (shellcheck, `bash -n`, execution on representative input and failure paths all clean; no `shfmt` configured in this repo).

**Changed:** `bin/clean-workspaces.sh`, `README.md`

`clean-workspaces.sh` now takes `[--dry-run] [WORKSPACE_ROOT] [DAYS]`, defaulting to `workspaces` and `7` as before. Also fixed unquoted expansions and `ls`-based iteration (broken on the `old build 2024` fixture directory), replacing them with a globbed, quoted loop and `set -Eeuo pipefail`.

Per the repo's own `CLAUDE.md`: no commit made, since you didn't ask for one. `/clear` before starting anything unrelated.
