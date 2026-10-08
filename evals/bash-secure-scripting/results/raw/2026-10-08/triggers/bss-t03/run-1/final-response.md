I couldn't apply the fix. This session gives me only read and search tools, with no way to edit files or run commands. Below is the corrected `scripts/backup.sh` for you to paste in. I haven't run `shellcheck`, `bash -n` or the script itself.

## What's wrong with the current script

- **The cleanup only runs if the script reaches the last line.** `rm -rf $TMP` is the final command. If the job is stopped partway (a cron timeout, a reboot, or a `kill` during a slow `scp`), that line never runs and the directory stays.
- **A failed step is ignored.** There's no `set -e`, so if `tar` fails the script still runs `scp` on a missing or half-written archive. The exit status comes from `rm`, so cron sees success even when the backup didn't happen.
- **The temp directory name is predictable.** `/tmp/backup.$$` can be guessed, so another local user can create it in advance as a directory or symlink. Then `mkdir` fails or the data goes somewhere it shouldn't. Paths are also unquoted, and cron's `PATH` decides which `tar`/`scp` run.

## Fixed `scripts/backup.sh`

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

# Clean up, then die of the signal so cron/supervisors see 128+n.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp, so there is no window where the path can be lost.
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

  if ! scp -q -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **The temp directory is always removed.** It's deleted by the `EXIT` trap whether the script succeeds, fails partway, or is stopped. The traps are set before `mktemp` creates the directory, and `cleanup` always returns 0 so it can't hide the real exit status.
- **A failed step stops the job.** If `tar` or `scp` fails, the script prints an error to stderr and exits non-zero, so cron's mail or your monitoring will see it.
- **The temp directory is safer.** `mktemp -d` under `/var/tmp` gives a name nobody can guess, and `umask 077` makes the directory and archive readable only by the backup user.
- **The script sets its own environment.** It fixes `PATH` and the locale, quotes every path, and uses `$(…)` instead of backticks.
- **The date is now UTC.** `date -u` stops the backup's file name shifting with the time zone. Drop `-u` if you want local dates.

## Before merging

1. Run `shellcheck scripts/backup.sh` and `bash -n scripts/backup.sh`.
2. Test the failure path. Point `DATA_DIR` at a path that doesn't exist, or make `scp` fail by using an unreachable host. The script should exit non-zero and leave nothing in `/var/tmp/tmp.*`.
3. Test an interruption. Start the script, run `kill -TERM <pid>` during the `scp`, and check that the exit status is 143 and the directory is gone.
