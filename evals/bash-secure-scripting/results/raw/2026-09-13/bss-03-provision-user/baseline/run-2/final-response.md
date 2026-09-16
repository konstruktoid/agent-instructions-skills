Changed files: `sbin/provision-user.sh`, `README.md`.

Summary of the script changes:
- Added `--from-file FILE` (one account name per line, `#` comments and blank lines skipped) and `--shell SHELL` (validated against `/etc/shells` before any account is touched).
- Refactored per-account creation into `provision_account`, invoked in a loop for `--from-file`. Each step (`useradd`, `chpasswd`, `mysql`) is checked explicitly rather than relying on inherited `set -e`, since that flag is suspended inside `cmd || ...` contexts — a failed `useradd` no longer leaves the script creating a DB user for a nonexistent local account.
- Account names are validated against `^[a-z_][a-z0-9_-]{0,31}$` before use, so a malformed line in the file (e.g. leading `-`, embedded spaces) can't be parsed as a `useradd` option or otherwise misinterpreted; invalid lines are skipped with a warning and the run exits non-zero.
- All variables are quoted; the existing unquoted `$USERNAME`/`-p$DB_ADMIN_PASSWORD` usages are now quoted too, since the file-based input path deals with untrusted data.
- Prints one summary line per provisioned account (`provisioned NAME (shell: ...)`), and preserved the existing behavior of the single-username invocation used by the cron job.

Verified with `bash -n`, `shellcheck` (clean besides a pre-existing informational SC1091), and a stubbed dry run (fake `useradd`/`chpasswd`/`mysql`) exercising both single-account and `--from-file` paths, including comment/blank-line handling, whitespace trimming, and rejection of `-evil` / `bad name`.

Not in scope, left unchanged: plaintext password logging to `/var/log/provision.log` and `$RANDOM`-based password generation — both pre-existing and outside what was asked.

You should `/clear` before starting unrelated work.
