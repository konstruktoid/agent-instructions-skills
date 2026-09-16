**Files changed:** `sbin/provision-user.sh`, `README.md`.

`provision-user.sh` now accepts `--from-file FILE` (one account per line, blank/`#` lines skipped, invalid names skipped with a warning instead of aborting the batch) and `--shell SHELL` (validated as an executable path, passed to `useradd -s`), refactored around a `provision_account` function so both the single-user and file-driven paths share it. Each provisioned account prints a summary line. While rewriting the per-account logic to run in a loop, I also switched the `mysql` call from `-p$DB_ADMIN_PASSWORD` to `MYSQL_PWD=$DB_ADMIN_PASSWORD` — the old form leaks the DB password to any local user via `ps`, and it was strictly worse to replicate that in a loop; the password is still logged in plaintext to `/var/log/provision.log`, unchanged from the original design since that's out of scope for this task.

Verified with `bash -n` + `shellcheck` (clean except a pre-existing informational SC1091 on the `db.conf` source) and a dry run against mocked `useradd`/`chpasswd`/`mysql`, covering the file loop, comment/whitespace handling, invalid-name skipping, backward-compatible single-user invocation, and the new error paths (missing args, conflicting args, bad shell).

Task accepted and reported — recommend `/clear` before starting anything unrelated.
