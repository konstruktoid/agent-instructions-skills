I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I only syntax-checked it with `bash -n`. I did not run it, because it needs root, `useradd` and MySQL.

- **`--from-file FILE`**: reads one name per line and skips blank lines and `#` comments. Names from the file are added to any given on the command line, so `USERNAME` still works as before.
- **`--shell SHELL`**: passes the shell to `useradd -s`. It must be an absolute path listed in `/etc/shells`.
- **Summary line**: each provisioned account prints `provisioned NAME (shell: …)`.
- **Validation**: names must match `[a-z_][a-z0-9_-]{0,31}`, and every name is checked before any account is created. A bad name therefore can't leave a half-finished batch.

I also fixed a few problems in the original script while I was in it:
- **Quoting**: variables were unquoted. Because the SQL string embeds the username, an unvalidated name could have been injected.
- **Config path**: `. etc/db.conf` only worked from the repo root. It now resolves relative to the script, which matters under cron.
- **Passwords**: they came from `$RANDOM`, which is weak. They now come from `/dev/urandom`.
- **Admin password**: it was on the `mysql` command line, visible in the process list. It now goes through a temporary option file.
- **Strictness**: the script now runs with `set -euo pipefail` and `umask 077`.

- **Plaintext passwords in the log**: it still appends generated passwords to `/var/log/provision.log`, as before, because that's the only place they're recorded. I'd move them somewhere safer, but that changes how people get their passwords, so I left it.
- **Cron entry**: it runs `provision-user.sh $(cat /var/lib/provisioning/next)` unquoted, so word splitting there is a risk. `--from-file` would be a safer way to feed it. I didn't change the cron file.
