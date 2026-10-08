I couldn't apply this fix. This session gave me read-only file tools, with no Edit, Write or Bash, so `scripts/backup.sh` is unchanged and I couldn't run `shellcheck`, `bash -n` or the script. The replacement is below for you to paste in.

## Why the directory gets left behind

At `scripts/backup.sh:13`, the only cleanup is an `rm -rf $TMP` on the last line. It only runs if the script gets that far, so a kill, a timeout or a hung `scp` skips it. Three other things make it worse:

- **No error checking.** There's no `set -e`, so a failed `tar` still lets `scp` upload a broken archive. The script then exits with `scp`'s status, and cron can't tell the backup failed.
- **Predictable temp path.** `/tmp/backup.$$` is easy to guess. Another user can create it or symlink it first, and `mkdir $TMP` doesn't fail safely when that happens.
- **Unquoted variables and cron's environment.** The paths aren't quoted, and the script relies on whatever `PATH` cron happens to provide.

## Proposed `scripts/backup.sh`

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: don't trust the inherited environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
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

# Clean up, then die of the signal so cron and supervisors see 128+n.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp, so no window where a signal loses the path.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d)"

  stamp="$(date +%F)"

  if ! tar -czf "${workdir}/data.tar.gz" -- "${DATA_DIR}"; then
    err "tar failed for ${DATA_DIR}"
    return 1
  fi

  # BatchMode: fail instead of hanging on a prompt when run from cron.
  if ! scp -q -o BatchMode=yes -- "${workdir}/data.tar.gz" \
    "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **Cleanup on every exit path.** An `EXIT` trap covers both success and any `errexit` abort. The `INT`/`TERM`/`HUP` handlers clean up and then re-raise the signal, so a killed run doesn't report success. All traps are installed before `mktemp`, and `cleanup` always returns 0, so it never turns a successful run into a failure.
- **Safe temp directory.** `mktemp -d` under `/var/tmp` with `umask 077` replaces the guessable `/tmp/backup.$$`.
- **Failures stop the script.** With strict mode on, a failed `tar` stops the run before `scp` uploads anything. Both steps print an error to stderr and exit non-zero.
- **Cron-friendly.** The script sets its own `PATH`, quotes every variable, and uses `$(…)` instead of backticks. `BatchMode=yes` makes `scp` fail rather than hang waiting for a password.

`date +%F` still uses local time, as before. Add `-u` if you want UTC filenames.

## To verify after pasting

```bash
shellcheck scripts/backup.sh && bash -n scripts/backup.sh
```

Then test it against a scratch `DATA_DIR`:
- Point `DATA_DIR` at a path that doesn't exist. The script should exit non-zero and nothing new should appear in `/var/tmp/tmp.*`.
- Run it with a reachable host and confirm it exits 0.
- Send it `kill -TERM` mid-run. It should exit with status 143 and leave no temp directory behind.
