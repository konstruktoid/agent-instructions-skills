I don't have a file-editing or shell tool in this session, so I couldn't change `scripts/backup.sh` or run it. Below is the fixed version for you to drop in, followed by the checks to run.

## What's wrong now (`scripts/backup.sh`)

- **Line 13:** cleanup only happens if the script gets to its last line. If cron's timeout, a `SIGTERM` or a hangup kills it partway through `tar` or `scp`, `/tmp/backup.$$` stays behind.
- **No error checking:** a failed `tar` or `scp` doesn't stop the script, and it still exits 0. Failed backups currently look like successful ones in cron. Adding strict mode fixes that, but then every failure would leave the directory behind unless cleanup moves into a trap. That's why both changes go together.
- **Line 7:** the temp path is predictable (`/tmp/backup.<pid>`). Another local user could create it, or a symlink with that name, before the script does. `mkdir` would then fail, or the archive would go somewhere it shouldn't.
- **No quotes and an inherited `PATH`/`umask`:** under cron, the caller's environment decides which `tar` and `scp` run. The default umask can also leave the archive readable by other users.

## Fixed script

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting it.
PATH='/usr/local/bin:/usr/bin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
readonly DATA_DIR='/srv/ledger/data'
readonly TARGET='/mnt/backup'
readonly REMOTE='backup@archive.example.internal'

# Script scope: the EXIT trap runs after main returns.
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

# Clean up, then die of the signal so cron/supervisors see 128+n.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: no window in which the directory can be orphaned.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d)"

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

**Behaviour changes:**
- **Exit status:** failures now exit non-zero instead of 0, so cron mail and any monitoring will start reporting failed backups.
- **Temp location:** the work directory is now made in `/var/tmp` with `mktemp -d`, readable only by the owner.
- **Signals:** if the script is killed, it cleans up and then exits with the signal's status.
- **SSH prompts:** `BatchMode=yes` makes `scp` fail straight away instead of waiting for a password prompt that cron can't answer.
- **Archive date:** the filename date is now in UTC. Drop the `-u` if you want local dates to keep matching the existing archives.

## Checks to run

1. `shellcheck scripts/backup.sh` and `bash -n scripts/backup.sh`
2. `shfmt -d scripts/backup.sh`, if you use shfmt
3. A failure path: temporarily set `DATA_DIR` to a directory that doesn't exist, run the script, and confirm three things: it exits non-zero, it prints `tar ... failed` to stderr, and no `tmp.*` directory is left in `/var/tmp`.
4. An interrupted run: start it against real-sized data, `kill -TERM` it during the `scp`, and confirm the exit status is 143 and nothing is left in `/var/tmp`.

Directories already left by earlier failed runs are still sitting in `/tmp/backup.*`, and you'll need to delete those by hand once.
