I couldn't apply this fix because this session can only read files. I can't edit or run anything, so nothing has been changed or tested yet. Below is the full fixed `scripts/backup.sh` to put in its place.

## What's wrong now (`scripts/backup.sh:7-13`)

- **Cleanup only happens on the last line.** `rm -rf $TMP` runs only if the script gets that far. If the script is killed or times out (a stalled `scp` is the usual case), or anything stops it early, the directory is left behind.
- **No strict mode.** A failed `tar` doesn't stop the script. It goes on to `scp` a missing or partial archive and can report success.
- **The temp path can be guessed.** `/tmp/backup.$$` is predictable. Another local user can create it or plant a symlink there first, and then `mkdir` fails and `tar` writes somewhere it shouldn't.
- **It runs from cron**, so it uses whatever `PATH`, `TMPDIR` and `umask` cron gives it, and the archive is created readable by others.
- None of the variables are quoted, and it uses backticks.

## Fixed script

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment instead of inheriting it.
PATH='/usr/local/bin:/usr/bin:/bin'
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

# Clean up, then die of the signal so cron and callers see 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp, so no signal can arrive between creation and cleanup.
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

  if ! scp -q -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **The `EXIT` trap is set before `mktemp`.** The directory is removed whether the script succeeds or fails, and `cleanup` always returns 0, so an empty or already-removed directory doesn't turn a good run into a failed one.
- **Signals are handled.** On `INT`/`TERM`/`HUP` the script cleans up and then exits with that signal. A run that gets killed reports as killed, not as a success.
- **`mktemp -d`** creates a unique directory under `/var/tmp` with mode 0700, which replaces the guessable `/tmp/backup.$$`.
- **Each failure stops the script** with a message on stderr and a non-zero exit, so a partial archive is never uploaded.
- **The environment is set at the top:** `PATH`, `TMPDIR` and `umask 077`. The date stamp is now UTC (`-u`). It used to be local time, so the filename can differ near midnight. Drop `-u` if you want local dates.

## Before you commit

Since nothing was run, please check:

1. `shellcheck scripts/backup.sh` and `bash -n scripts/backup.sh` both come back clean.
2. To test the failure path, point `DATA_DIR` at a path that doesn't exist. The script should exit non-zero with a message on stderr, and `ls /home/user/other-checkout*` should find nothing.
3. To test a kill, start a run, send `kill -TERM` to it while `scp` is running, and check that the exit status is 143 and the temp directory is gone.

If you give me edit and shell access, I can apply the change and run these checks myself.
