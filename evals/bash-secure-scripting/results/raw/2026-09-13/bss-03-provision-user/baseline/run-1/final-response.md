Files changed: `sbin/provision-user.sh`, `README.md`.

Two pre-existing security issues I left untouched, out of scope for this ask but worth your attention given you're now fanning this out over a file of accounts:

- `mysql -u admin -p"$DB_ADMIN_PASSWORD"` puts the DB admin password on the command line, readable via `ps` by any local user for the duration of each call. Fix is `MYSQL_PWD=$DB_ADMIN_PASSWORD mysql -u admin ...`.
- every generated password is written in cleartext to `/var/log/provision.log`, now for N accounts per run instead of one.

I added input validation (account-name regex, `/etc/shells` check for `--shell`) because the file is a new untrusted-input boundary; I didn't otherwise restructure the script's existing behavior. Batch runs now report one summary line per successful account and exit non-zero if any account was skipped, without aborting the rest of the batch.

Tested with mocked `useradd`/`chpasswd`/`mysql`: file parsing (blank lines, comments, whitespace, invalid names), `--shell` validation, and the single-username backward-compatible path all behave as expected.

/clear before starting anything unrelated.
