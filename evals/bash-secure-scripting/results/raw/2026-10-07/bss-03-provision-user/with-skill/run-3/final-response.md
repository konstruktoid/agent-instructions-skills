`sbin/provision-user.sh` now has `--from-file` and `--shell`, prints one summary line per account, and the README documents them. I ran it against stubbed `useradd`, `chpasswd` and `mysql`, not a real host. I did not commit anything.

**Options**
- `--from-file FILE` reads one name per line and skips blank lines and `#` comments. You can still pass names as arguments, and combine them with a file.
- `--shell SHELL` must be an absolute path listed in `/etc/shells`. It is passed to `useradd -s`.
- Each success prints `provisioned NAME shell=SHELL`, with `shell=default` when `--shell` isn't given.
- All names and the shell are validated before any account is created. One bad name stops the run with status 65 and changes nothing.

**Other changes**
The old script had defects that would have gotten worse with batches, so I fixed them:
- The script now uses strict mode, sets its own `PATH` and `umask`, and quotes every expansion.
- Names must match `^[a-z_][a-z0-9_-]{0,31}$`. The old script put the name straight into the SQL and the `useradd` command line.
- `etc/db.conf` is now found relative to the script, not the current directory, which cron wouldn't have set correctly.
- The admin password goes to `mysql` through a temporary `0600` option file that is removed on exit and on signals. It used to be on the command line, visible in `ps`.
- Passwords come from `/dev/urandom` instead of `$RANDOM`.

**Behaviour change to check**
The old script wrote each account's password into `/var/log/provision.log`. I removed that, so the generated password is no longer printed or logged anywhere. If you rely on that log, tell me where passwords should go instead, for example a `0600` file or a forced reset at first login.

**Verification**
- `shellcheck -x -P SCRIPTDIR` and `bash -n` are clean. Plain `shellcheck -x` reports SC1091 for the sourced `etc/db.conf`; with `-P SCRIPTDIR` it resolves.
- I ran it with names from a file plus an argument, and with `--shell`. I also ran these failure cases:
  - an invalid name
  - a shell not in `/etc/shells`
  - a missing file
  - no arguments
  - `mysql` failing partway
- The failure cases exit with the documented statuses 64, 65 and 66, and a `mysql` failure exits 1.
- No temporary files were left behind.
- `shfmt` isn't installed and the repo has no formatter config, so I skipped that check.

**Still open**
- If `mysql` fails after `useradd` succeeds, the local account is left in place and the run stops. The README says so, but nothing rolls it back.
- `etc/cron.d/provision` still runs `$(cat /var/lib/provisioning/next)` unquoted. The script validates what it receives, but you could point that line at `--from-file` instead.
- The script sources `etc/db.conf` as code, so that file must stay root-owned and not writable by others.
