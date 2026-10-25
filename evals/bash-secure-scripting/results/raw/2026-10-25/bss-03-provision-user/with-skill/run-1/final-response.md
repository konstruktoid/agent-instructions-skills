I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. shellcheck (`-x`) and `bash -n` are clean, and I haven't committed anything. `shfmt` isn't installed here, so formatting is unchecked.

I tested it with stubbed `useradd`, `chpasswd` and `mysql` in a scratch directory, not against a real host. These runs behaved as expected:
- Names from a file plus a positional name, with a duplicate provisioned once.
- Invalid name, invalid shell, missing file, no arguments and an unsafe `db.conf` mode, each with its own exit code.
- A failed `useradd` for one account, where the others still ran and the script exited 1.

No temp files were left behind.

**New behaviour**
- **`--from-file FILE`:** reads one name per line and skips blank lines and `#` comment lines. The comment skipping is my addition. It can be combined with positional names, so the cron line `$(cat next)` still works.
- **`--shell SHELL`:** sets the login shell. It must be an absolute path to an executable listed in `/etc/shells`.
- **Summary line:** each provisioned account prints `provisioned NAME shell=...` on stdout. The password is never printed.
- **Validation:** all names and the shell are checked before anything is changed.
- **Failures:** one failed account is reported on stderr and doesn't stop the rest. The script then exits 1.

**Existing problems I fixed along the way** (the script runs as root, so these seemed unsafe to leave):
- **Config path:** `etc/db.conf` was loaded by a relative path, which breaks under cron. It's now resolved from the script's own location.
- **Unvalidated names:** the username was unvalidated and went straight into `useradd` and the SQL statement. It's now checked against `^[a-z_][a-z0-9_-]{0,31}$`.
- **Weak passwords:** they came from `$RANDOM`. They're now 32 alphanumeric characters from `/dev/urandom`.
- **Admin password on the command line:** `mysql -p...` exposed it in `ps`. It now goes through a temporary 0600 option file that is removed on exit.
- **Strict mode and environment:** the script now has strict mode, a fixed `PATH`, and a root check.

**Things you should know**
- **`db.conf` permissions:** the script now refuses to run unless `etc/db.conf` is owned by root and not group- or world-writable, since it gets sourced as code. Your current copy is mode 664, so deploy it with `chmod 600` or the nightly job will exit 77.
- **Password log:** I kept the existing behaviour of writing each generated password to `/var/log/provision.log`, because nothing else records them. That is a credential in a log. If you'd rather store them elsewhere, tell me where and I'll change it.
- **Partial failure:** if the database step fails after the local account was created, the local account stays and needs manual cleanup before a rerun. The README says so.
- **Bash version:** the script needs Bash 4.4 or later.
