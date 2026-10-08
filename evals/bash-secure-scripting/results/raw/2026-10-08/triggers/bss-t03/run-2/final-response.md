I couldn't apply this fix. This session gives me no tool that can edit files or run commands, so `scripts/backup.sh` hasn't changed and I haven't run `shellcheck`, `bash -n` or the script. Below is the replacement to paste in.

## Why the directory is left behind

In `scripts/backup.sh`, cleanup is a plain `rm -rf $TMP` on the last line. Two things go wrong when a step fails:

- If `tar` or `scp` fails, the script just keeps going because errors don't stop it (no strict mode). It runs `rm`, then exits 0, so cron never hears about the failure.
- If the script is killed, times out or is interrupted, it never reaches line 13, so `/tmp/backup.<pid>` stays.

There are related problems too: the temp name is predictable (`/tmp/backup.$$`), which leaves it open to symlink or pre-creation tricks in `/tmp`. Variables are unquoted, and `PATH` and `umask` are inherited from cron.

## Replacement `scripts/backup.sh`

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: don't trust the inherited environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
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

# Clean up, then die of the signal so cron/supervisors see 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: cleanup tolerates an empty workdir.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXXXXXX")"

  stamp="$(date +%F)"

  if ! tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"; then
    err "tar of ${DATA_DIR} failed"
    return 1
  fi

  if ! scp -q -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **Cleanup on every exit path:** `trap cleanup EXIT` is set before the temp directory is created, so the directory is removed on success, when a step fails, and on an early exit. `INT`/`TERM`/`HUP` clean up and then re-raise the signal, so a killed run doesn't report success.
- **Failures are reported:** `set -Eeuo pipefail` plus explicit checks on `tar` and `scp` stop the script at the first failure, print a message to stderr and exit non-zero, so cron's mail or log shows it.
- **Safe temp directory:** `mktemp -d` creates a random, private name with mode 0700 (because of `umask 077`) instead of a guessable `/tmp/backup.$$`.
- **Fixed environment:** `PATH`, `LC_ALL` and `umask` are set explicitly, every expansion is quoted, and `$(...)` replaces the backticks.
- **`cleanup` always returns 0**, so a successful run isn't reported as failed just because there was nothing left to remove.

## Checks to run after pasting it in

```bash
shellcheck scripts/backup.sh
bash -n scripts/backup.sh
# Failure path: point DATA_DIR at a missing path (or make scp fail), then confirm:
#   exit status != 0, an error on stderr, and no new backup.* directory under /tmp
```

The scp connection still depends on whatever SSH key the cron user has. I didn't change that.
