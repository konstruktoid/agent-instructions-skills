Both files are updated and tested. Summary of changes:

**`sbin/provision-user.sh`**
- Added `--from-file FILE` to provision multiple accounts (one per line, `#` comments/blank lines skipped) and `--shell SHELL` to set the login shell (validated against `/etc/shells`).
- Prints a summary line (`provisioned NAME (shell: ...)`) per account.
- Hardened while I was touching the file: `set -euo pipefail`, account names validated against `^[a-z_][a-z0-9_-]*$` before being used in `useradd`/SQL (closes an injection path once names come from a file instead of a trusted arg), all variables quoted, DB password passed via `MYSQL_PWD` env var instead of `-p<pass>` on the command line (avoids leaking it via `ps`), and stronger random passwords via `/dev/urandom` instead of `$RANDOM`. Failures for one account (bad name, `useradd` failure) are logged and skipped rather than aborting the whole batch; the script exits non-zero if any account failed.

**`README.md`** — documented the new usage, flags, and exit behavior.

I tested both single-account and `--from-file` batch modes (including invalid names, a failing `useradd`, an invalid `--shell`, and conflicting/missing args) against stubbed `useradd`/`chpasswd`/`mysql`/`getent` — all behaved as expected.
