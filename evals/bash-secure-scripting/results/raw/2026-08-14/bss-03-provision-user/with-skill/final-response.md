Done. Summary of changes to `sbin/provision-user.sh` and `README.md`:

**New options**
- `--from-file FILE` — provisions one account per line (blank lines skipped), reusing the same per-account logic as the single-username path.
- `--shell SHELL` — sets the login shell for accounts created in that run; validated as an absolute, executable path listed in `/etc/shells`.
- Every account prints a summary line: `NAME: provisioned (shell: SHELL)` or `NAME: already exists, skipped`.

**Hardening applied while touching the file** (the original had no strict mode, unquoted variables, a SQL-injection-shaped username interpolation, `$RANDOM`-based passwords, the DB admin password on the `mysql -p` command line, and plaintext passwords appended to a shared log):
- `set -Eeuo pipefail` + `shopt -s inherit_errexit`, explicit `PATH`, `umask 077`.
- Username/shell validated against allowlists before use.
- Passwords generated from `/dev/urandom`, never `$RANDOM`.
- DB admin auth passed via a `mktemp`'d 0600 `--defaults-extra-file`, cleaned up by an `EXIT` trap — never on the command line.
- Generated passwords go to per-account `0600` files under `/var/lib/provisioning/credentials/`, not the log; the log only records that provisioning happened.
- `etc/db.conf` is checked for safe ownership/mode before being sourced (and its real permissions tightened to `600`, since it was `664`).
- Idempotent: an existing account is skipped, so a rerun after a partial failure repairs rather than duplicates.
- `flock`-based lock so two cron-triggered runs can't provision concurrently.
- Fixed a latent bug: the config was sourced via a relative path (`etc/db.conf`), which would fail under cron's unspecified working directory; it's now resolved relative to the script's own location.

**Verified**: `shellcheck` and `bash -n` clean. Since `useradd`/`chpasswd`/`mysql` mutate real system/database state, I didn't run them for real — I shimmed those three commands plus `id` in a scratch sandbox mirroring the repo layout and exercised: help, single-account creation, `--from-file` batch (including blank lines and whitespace), the already-exists skip path, and all failure paths (bad username, bad shell, missing/unreadable file, combining `--from-file` with a username, no args, unknown option). Confirmed no leftover temp files and correct `0600` modes on generated credential files.
