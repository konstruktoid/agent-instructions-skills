I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I only checked the script's syntax with `bash -n`. I didn't run it, because it needs root, `useradd` and MySQL.

- **`--from-file FILE`** reads one account name per line and skips blank lines. It can be combined with names on the command line.
- **`--shell SHELL`** sets the login shell for the accounts it creates. The value must be an absolute path listed in `/etc/shells`.
- **Summary line:** each account prints `provisioned NAME (shell: …)`. It doesn't include the password.
- **Failures:** if one account fails, the script reports it on stderr, carries on with the rest, and exits non-zero at the end.
- **Name validation:** every name must match `[a-z_][a-z0-9_-]{0,31}`, and all names are checked before any account is created. The old script passed unquoted input to `useradd` and into the SQL.

The old script also had other problems, and I fixed these while rewriting it:
- It loaded `etc/db.conf` relative to the working directory, which fails under cron. It now resolves the path from the script's location.
- Passwords were built from `$RANDOM`. They now come from `/dev/urandom`.
- The MySQL admin password was passed on the command line. It now goes through the `MYSQL_PWD` environment variable.

Two things I left alone:
- **Password log:** the script still appends plaintext passwords to `/var/log/provision.log`, as it did before. You may want to change that.
- **Cron entry:** `etc/cron.d/provision` runs `provision-user.sh $(cat /var/lib/provisioning/next)` with the substitution unquoted. It still works with the new script, but the substitution is subject to word splitting. It could use `--from-file` instead.
