Verify loop is clean (shellcheck, `bash -n`, functional tests all passed). Files changed:

- `sbin/provision-user.sh` — added `--from-file` and `--shell`, per-account summary output, username validation, and per-item error isolation (one bad/duplicate account doesn't abort the batch). While touched, I also brought it up to the shop's Bash baseline: `set -Eeuo pipefail`, a controlled `PATH`, `mktemp`+trap-based cleanup for the MySQL credentials file (previously passed as `-p$DB_ADMIN_PASSWORD`, visible in `ps`), signal-safe traps, and stronger password generation (`/dev/urandom` instead of `$RANDOM`). I also stopped writing the generated password to `/var/log/provision.log` in plaintext — the log now records only that an account was provisioned. That's a scope expansion beyond what you asked for, done under the security-review instructions this skill sets for every touched script; flag if you'd rather I split it out or revert it.
- `README.md` — documents the two new flags and the summary-line behavior.

I did not touch `etc/cron.d/provision`, though its `$(cat /var/lib/provisioning/next)` is unquoted and vulnerable to word-splitting/injection if that file's content is ever attacker-influenced — out of scope for this task, worth a separate look.

Not committed, per your instructions. Task is small and self-contained; no `/clear` needed unless you're moving to unrelated work next.
