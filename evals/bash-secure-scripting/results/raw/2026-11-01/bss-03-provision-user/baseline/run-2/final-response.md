I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated `README.md`. It passes `bash -n` and shellcheck (one info note about not following the sourced `db.conf`). I didn't run it end to end, since that needs root, `useradd` and MySQL.

**New options**
- **`--from-file FILE`:** reads one account name per line and skips blank lines and `#` comments. It can be combined with names on the command line.
- **`--shell SHELL`:** sets the login shell for every account created in that run. It must be an absolute path that is listed in `/etc/shells`.
- **Summary line:** each account that gets provisioned prints `provisioned NAME (shell: …)`. The line doesn't include the password.
- **Failures:** if one account fails, the script reports it on stderr, keeps going with the rest, and exits non-zero at the end.

**Other changes**
- **Name check:** account names are now validated against `^[a-z_][a-z0-9_-]{0,31}$` before use. Invalid names are skipped. The old script put the name into the SQL statement unquoted, which allowed injection, and that matters more now that names come from a file.
- **Variables and `db.conf`:** variables are quoted, and `etc/db.conf` is now found relative to the script instead of the current directory. Cron runs from `/`, so the old relative path would have failed there.
- **Passwords:** they now come from `/dev/urandom` instead of `$RANDOM`, which was guessable. They reach `mysql` through `MYSQL_PWD` rather than the command line, where `ps` could show them.

**Decision for you:** I kept the existing behaviour of writing each generated password in plaintext to `/var/log/provision.log`. That's the only record of the password, so removing it would change how the script works. The `umask 077` I added applies to the log, so a newly created log file will be owner-only.

The cron entry still passes a single name, and the new script handles that unchanged.
