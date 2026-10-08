I couldn't apply this fix. This session gives me read and search tools but no way to edit files or run commands. The fixed `scripts/backup.sh` is below, ready to paste in. I haven't run it, `shellcheck`, or `bash -n` on it.

## What's wrong now

The script has no strict mode and no trap. The cleanup is just a plain `rm -rf $TMP` on the last line:

- **Leftover directories:** the `rm` only runs if the script reaches the last line. If the job is killed (by a cron timeout, a reboot, or Ctrl-C), `/tmp/backup.<pid>` stays behind.
- **Failures look like success:** when `tar` or `scp` fails, the script carries on and exits with `rm`'s status, which is 0. Cron sees a successful run even though no backup was made.
- **Predictable temp path:** `/tmp/backup.$$` can be guessed. If `mkdir` fails because that path already exists (or another user planted it as a symlink), the script still writes the archive there and then runs `rm -rf` on it.

## Fixed script

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
readonly DATA_DIR='/srv/ledger/data'
readonly TARGET='/mnt/backup'
readonly REMOTE='backup@archive.example.internal'

# Script scope: the EXIT trap runs after main has returned.
workdir=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${workdir} && -d ${workdir} ]]; then
    rm -rf -- "${workdir}"
  fi
  return 0
}

# Clean up, then die of the signal so cron and callers see 128+n.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: cleanup tolerates the empty workdir.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d -t backup.XXXXXXXXXX)"

  stamp="$(date -u +%F)"

  if ! tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"; then
    err "tar of ${DATA_DIR} failed"
    return 1
  fi

  if ! scp -q -o BatchMode=yes -- "${workdir}/data.tar.gz" \
    "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **Cleanup on every exit:** the cleanup now runs on any exit, set up before the temp directory is created, so it happens whether a step fails, the script finishes normally, or it's interrupted. If it's killed by a signal, it cleans up and then exits the way a killed process normally does, instead of reporting success.
- **Temp directory:** `mktemp -d` replaces `/tmp/backup.$$`. The directory gets a random name under `/var/tmp`, and `umask 077` keeps it private to the user running the job.
- **Failures stop the script:** `set -Eeuo pipefail` makes the script stop at the first failing step. `tar` and `scp` are also checked one by one, so each failure prints an error to stderr and the script exits non-zero. Cron will now see the failures that the old script hid.
- **Cron-safe defaults:** a fixed `PATH`, all variables quoted, `$(…)` instead of backticks, and the date in UTC so the archive name doesn't depend on the server's timezone.
- **`scp -o BatchMode=yes`:** if key-based login stops working, `scp` fails immediately instead of hanging at a password prompt.

## Behaviour changes to check

- The temp directory moves from `/tmp` to `/var/tmp`. If `/var/tmp` is too small for the archive, change `TMPDIR`.
- Archive names use the UTC date. If backups run near midnight and you want local dates, drop the `-u`.

## Verifying after you apply it

```bash
shellcheck scripts/backup.sh && bash -n scripts/backup.sh
# Failure path: point DATA_DIR at a missing dir in a scratch copy, run it, then
echo $?                       # expect non-zero
ls /var/tmp/backup.*          # expect: no such file
```

If you run those checks or give me edit access, I'll go through any findings.
