I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I only syntax-checked it with `bash -n`. I didn't run it, because it needs root, `useradd` and a MySQL server.

- **`--from-file FILE`**: reads one account name per line and skips blank lines and `#` comments. The names are added to any given on the command line.
- **`--shell SHELL`**: passed to `useradd -s`. It must be an absolute path listed in `/etc/shells`, or the script exits before creating anything.
- **Summary line**: each account prints `provisioned NAME (shell: …)`. A failed or invalid account prints a message to stderr and the script carries on with the rest. The exit code is non-zero if any account failed.

I also changed some existing behaviour, because multi-account runs from a file would have made these problems worse:
- **Passwords**: they now come from `/dev/urandom` instead of `$RANDOM$RANDOM$RANDOM`, which was guessable.
- **Password handling**: the database password no longer appears on the `mysql` command line, where other users could see it. The admin password goes through `MYSQL_PWD` and the SQL goes through stdin.
- **Log file**: `/var/log/provision.log` no longer records plaintext passwords. It now logs only a timestamp and the account name. If anything relied on reading passwords from that log, this breaks it.
- **Input checks**: names must match `[a-z_][a-z0-9_-]{0,31}`, and duplicate names are skipped.

Because passwords are no longer printed or logged, nothing records them anywhere. If you need them handed off somewhere, tell me where they should go.

The README documents the new options and these changes.
