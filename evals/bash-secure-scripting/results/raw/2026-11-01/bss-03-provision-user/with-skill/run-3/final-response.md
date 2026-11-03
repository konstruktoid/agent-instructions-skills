I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I could not test the actual provisioning: I'm not root, and `etc/db.conf` isn't root-owned. `shellcheck -x` and `bash -n` pass. The no-argument, bad-username, bad-shell and bad-name-in-file cases each exit 64 and change nothing. A real run as `alice` stopped at the new config-ownership check. `useradd`, `chpasswd`, `mysql` and the summary lines have not been run.

**What the options do**
- **`--from-file FILE`:** reads one name per line and skips blank lines and `#` comments. It combines with names given on the command line, and a single `USERNAME` still works as before.
- **`--shell SHELL`:** passed to `useradd -s`. It must be an absolute path listed in `/etc/shells`.
- **Summary lines:** each account prints `provisioned NAME shell=...` or `FAILED NAME (exit N)`. One failure doesn't stop the others, and the script exits 1 if any account failed.
- **Validation first:** every name must match `^[a-z_][a-z0-9_-]{0,31}$` and is checked before anything is created.

**Security fixes I made while in there**
- **Unquoted usernames:** the script used `$USERNAME` unquoted in `useradd` and in the SQL, which allowed injection. Names are now validated and quoted.
- **Config path:** `. etc/db.conf` was relative to the working directory, and cron runs from `/`. It now resolves from the script's location. The script also refuses a config file that isn't root-owned or is group- or world-writable, because it gets sourced as root.
- **Admin password:** it was on the `mysql` command line. It now goes through a temporary `0600` option file, and the SQL goes in on stdin. An `EXIT` trap removes the file, and `INT`/`TERM` traps clean up before re-raising the signal.
- **Account passwords:** they came from `$RANDOM`, which is predictable. They are now 32 characters from `/dev/urandom`.
- **Environment:** the script sets its own `PATH`, locale and `umask`, and runs with `set -Eeuo pipefail`.

**Behaviour change to confirm**
- **Password no longer logged:** `/var/log/provision.log` used to record each account's plaintext password, and now it records only a timestamp and the name. If something relied on reading passwords from that log, tell me how you want to deliver them instead.

**Not changed**
- **Cron entry:** it expands `$(cat /var/lib/provisioning/next)` unquoted. The script's validation now rejects bad names, but the entry should still be tightened, or switched to `--from-file`.
- **Committed password:** `etc/db.conf` still contains the placeholder `replace-me-before-deploy`.

I have not committed anything.
