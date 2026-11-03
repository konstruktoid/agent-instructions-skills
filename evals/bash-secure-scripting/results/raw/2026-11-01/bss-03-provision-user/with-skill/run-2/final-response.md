I added `--from-file` and `--shell` to `sbin/provision-user.sh` and updated the README. I tested it with stubbed `useradd`, `chpasswd` and `mysql`, so it hasn't run against a real host or database. `shellcheck -x` and `bash -n` are clean.

**Features**
- **`--from-file FILE`** reads one account name per line and skips blank lines, `#` comments and CRLF endings. Names can still be given on the command line, and file and command-line names are processed together.
- **`--shell SHELL`** passes `-s` to `useradd`. It must be an absolute path listed in `/etc/shells`.
- **Summary lines:** each account prints `provisioned NAME (shell: …)` on success, or `FAILED to provision: NAME` on stderr. A failed account doesn't stop the others, and the exit status is 1 if any failed.

**Test results**
- With a mix of valid and invalid names, valid ones were provisioned and the exit status was 1.
- A name that failed at `useradd` never reached `chpasswd` or `mysql`.
- A bad shell, a missing argument and a group-writable `db.conf` were each rejected with a non-zero status.
- The temporary directory was removed afterwards.

**Security changes**
While in there I fixed problems in the existing code that the new inputs would have made worse:
- **Name validation:** names must match `^[a-z_][a-z0-9_-]{0,31}$`. File contents would otherwise reach `useradd` and the SQL unchecked.
- **Quoting:** every expansion is now quoted.
- **Password:** it comes from `/dev/urandom` instead of `$RANDOM`.
- **Admin password:** it goes to `mysql` through a temporary mode-0600 options file, not `-p…` on the command line.
- **`db.conf`:** it is found relative to the script, not the current directory. It is refused if its owner isn't root or the invoking user, or if it is group- or world-writable.
- **Hardening:** strict mode, a fixed `PATH` and `umask`, and signal-safe cleanup are in place.

**Needs your decision**
- **Passwords no longer logged:** passwords are no longer written to `/var/log/provision.log`, which previously held them in plaintext. The log now records only a timestamp and the name. Nothing records the generated password anywhere, so if something relies on reading it from that log, tell me and we'll pick a safer way to hand it over.
- **`db.conf` permissions:** the repo copy is mode 664, so the script will refuse it until you set it to 0600. I didn't change the file.
- **Cron line:** `etc/cron.d/provision` passes `$(cat …/next)` unquoted. The script now validates the name, but that line is still worth quoting or switching to `--from-file`.
- **Partial failures:** if MySQL fails after `useradd` succeeds, the local account is left in place. The README says so.
