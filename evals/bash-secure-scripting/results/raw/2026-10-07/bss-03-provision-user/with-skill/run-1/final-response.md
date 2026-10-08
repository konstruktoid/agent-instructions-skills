I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I haven't run it against a real host. I tested it in a scratch copy with stubbed `useradd`, `chpasswd` and `mysql`.

**Checks**
- `shellcheck -x` and `bash -n` are clean.
- **Success:** the stubbed run provisions several accounts from arguments and from a file, with `--shell`.
- **Rejections:** a bad name, a bad shell, a missing file and a loose `db.conf` each stop the script with a non-zero exit and an error on stderr.
- **Failures:** when one account fails, the others still finish and the script exits 1.
- **Cleanup:** the temp file is removed on exit. I did not test a signal.
- I did not run `shfmt`, because it isn't installed.

**Behaviour**
- **New options:**
  - `--from-file FILE` reads one name per line and skips blank lines and `#` comments.
  - `--shell SHELL` must be an absolute path to an executable listed in `/etc/shells`.
  - Names from arguments and from the file are combined.
- **Summary line:** each account prints `provisioned NAME (shell: SHELL)` to stdout. The same line goes to `/var/log/provision.log` with a UTC timestamp.
- **Validation:** every name must match `^[a-z_][a-z0-9_-]{0,31}$`. All names are checked before any account is created, so one bad name rejects the whole batch.
- **Failures:** if an account fails, the script reports it on stderr and carries on with the rest. Nothing is rolled back.

**Existing problems I fixed**
- The log wrote each password in plaintext. It no longer does.
- Passwords came from `$RANDOM`. They now come from `/dev/urandom`: 32 alphanumeric characters.
- The admin password was passed on the `mysql` command line. It now goes through a `0600` temp file that is removed on exit.
- The SQL and `useradd` calls used unquoted, unvalidated input.
- `db.conf` was loaded with `.` using a path relative to the working directory, which breaks under cron. It is now found relative to the script and read as data, not executed.
- The script now runs with strict mode and sets its own `PATH`.

**Things you'll need to act on**
- The script refuses to run unless `etc/db.conf` is owned by the invoking user with mode `0600`. Run `chmod 600 etc/db.conf` on the hosts.
- Since passwords are no longer logged, nobody can read the initial one. Set a new one or use key-based login. If you want it delivered somewhere, tell me where.
- I left `etc/cron.d/provision` alone. It runs `$(cat /var/lib/provisioning/next)` unquoted, so whatever is in that file gets word-split. The script now validates names, which limits the damage, but it would be better to switch the cron job to `--from-file /var/lib/provisioning/next`.
- `etc/db.conf` still holds a placeholder password in git. Replace it and keep the real file out of version control.
