I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I haven't run the script. It needs root, `useradd` and a MySQL server, so I only syntax-checked it with `bash -n` and ran shellcheck. Shellcheck's only finding was an info note that it didn't follow the sourced `etc/db.conf`.

- **`--from-file FILE`** reads one account name per line and ignores blank lines and lines starting with `#`. It can be combined with names given as arguments.
- **`--shell SHELL`** sets the login shell on the accounts it creates. It must be an absolute, executable path that is listed in `/etc/shells`, otherwise the script exits with an error.
- **Summary line:** each account prints `provisioned NAME (shell: …, database user created)`. The password isn't in it.
- **Failures:** if one account fails, the script reports it, carries on with the rest, and exits 1.

I also changed some existing behaviour, because the new batch mode made these problems worse:
- **Name validation:** names must match `[a-z_][a-z0-9_-]{0,31}` and are all checked before anything is created. Before, names went unquoted into `useradd` and straight into the SQL.
- **Password generation:** passwords now come from `/dev/urandom` instead of `$RANDOM`, which is predictable.
- **Admin password:** the DB admin password goes to `mysql` through an option file on stdin instead of `-p…`, so it no longer shows up in `ps`.
- **Config path:** `etc/db.conf` is now found relative to the script instead of the current directory, which would have failed under cron.
- **Safety settings:** I added `set -euo pipefail` and `umask 077`.

**Password log:** I kept the line that appends each generated password to `/var/log/provision.log`. Without it the passwords would be lost, but it is plaintext, and `umask 077` only makes the file root-only if the script creates it. If you'd rather not store passwords there, say so and I'll change it.

**Cron job:** `etc/cron.d/provision` still calls the script with `$(cat /var/lib/provisioning/next)` as a single name. I left it alone.
