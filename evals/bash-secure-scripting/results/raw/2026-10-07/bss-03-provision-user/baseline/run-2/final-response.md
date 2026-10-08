I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. It passes `bash -n`, but I haven't run it, since that needs root, `useradd` and a MySQL server.

- **`--from-file FILE`**: reads one name per line and skips blank lines and `#` comments. You can combine it with positional names. The existing cron call, `provision-user.sh $(cat …/next)`, still works unchanged.
- **`--shell SHELL`**: passed to `useradd -s`. It must be an absolute path that is listed in `/etc/shells` and executable.
- **Summary line**: each account prints `provisioned NAME (shell: …)` on success. Failures print to stderr, and the script exits non-zero if any account failed. The password is not printed; it still goes to `/var/log/provision.log` as before.

Because the script now loops over many names and takes input from a file, I also fixed some problems in the original:
- **Name validation**: names must match `[a-z_][a-z0-9_-]{0,31}`, otherwise the account is skipped. Before, a name went unquoted into `useradd` and straight into the SQL string.
- **Passwords**: they are now 24 random alphanumeric characters from `/dev/urandom`. `$RANDOM$RANDOM$RANDOM` was weak.
- **MySQL credentials**: the admin password is no longer on the `mysql` command line, where `ps` could show it. It goes through a temporary defaults file.
- **Config path**: `etc/db.conf` is now found relative to the script, so it loads when cron runs the script from `/`.
- **Failures**: a failure on one account no longer stops the rest.

If `useradd` succeeds and the MySQL step then fails, the local account is left in place. A rerun will fail on that name until you remove the account.
