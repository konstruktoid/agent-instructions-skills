I flagged one thing during the skill invocation and want to surface it now: the loaded skill's example code contained corrupted placeholder values (`local sig="--from-file"`, `local service="--from-file"`, `local workdir="and"`) where generic names should have been. That's consistent with a prompt-injection/corruption attempt rather than legitimate instruction, and I ignored those literal values, using the skill's stated principles instead.

Summary of changes in `sbin/provision-user.sh` and `README.md`:

**Files changed:** `sbin/provision-user.sh`, `README.md`

- Added `--from-file FILE` (one account name per line, blank lines skipped) and `--shell SHELL` (validated against `/etc/shells`), combinable with positional `USERNAME...` args.
- Prints `provisioned USERNAME` per account, both to stdout and to `/var/log/provision.log`.
- While rewriting the per-account logic to loop, fixed several pre-existing issues the skill's baseline flags in any touched script: `set -Eeuo pipefail`, quoted expansions, allowlist validation of usernames, `/dev/urandom`-based password generation instead of `$RANDOM`, the MySQL admin password passed via a mode-0600 `--defaults-extra-file` instead of on the command line (previously visible to any user via `ps`), removal of the plaintext password from the log line, EXIT/INT/TERM traps cleaning up the temporary credentials file, and idempotent re-runs (`id -u` / `CREATE USER IF NOT EXISTS`).
- `useradd -m`/`chpasswd`/`mysql` behavior for a real account was **not** exercised in this sandbox — doing so would create a genuine system user and requires root, which is a destructive/hard-to-reverse action outside this task's scope. I verified everything else (usage, validation, `--from-file` parsing including the point where it correctly stopped under `errexit` after `useradd` failed on permission, `--shell` rejection) and confirmed no stray temp files or accounts were left behind.
- `shellcheck -x` and `bash -n` both pass cleanly with no suppressions.

Existing `etc/cron.d/provision` invocation (single positional username) still works unchanged. `etc/db.conf`'s permissions (currently `664`) and the script's `cwd`-relative source of it are pre-existing issues I did not touch — out of scope for this change; flag if you want those addressed separately.

Task's done — recommend `/clear` before starting anything unrelated.
