I couldn't apply this fix. This session only gave me read and search tools, so I can't edit the file or run `shellcheck`, `bash -n` or the script. Below is the replacement for `scripts/backup.sh` to paste in yourself.

## Why the directory gets left behind

`scripts/backup.sh:7-13` only deletes the temp directory with the `rm -rf $TMP` on its last line, and nothing else ever removes it:

- If cron or a supervisor kills the script (for example, `scp` hangs and hits a timeout), it never reaches that last line.
- With `set -e` added but no cleanup trap, the first failing step would exit straight away and also skip the `rm`.
- Without `set -e` (the current state), a failed `tar` doesn't stop the script. It goes on to `scp` a missing or partial archive, and the script's exit status comes from `rm`, so the failure is hidden.
- The path `/tmp/backup.$$` is predictable, and `$TMP` is used unquoted. Another local user could create that path or a symlink at it before the script runs. That matters more if the script runs as root.

## Fixed script

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
readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE=backup@archive.example.internal

# Script scope, not local: the EXIT trap runs after main has returned.
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
  workdir="$(mktemp -d)"

  stamp="$(date +%F)"

  if ! tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"; then
    err "tar of ${DATA_DIR} failed"
    return 1
  fi

  if ! scp -o BatchMode=yes -- "${workdir}/data.tar.gz" \
    "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **Cleanup on every exit:** cleanup now runs from a `trap … EXIT` that is set before the directory is created. It runs on success, when a step fails, and when the script is killed by INT, TERM or HUP. After a signal, the script cleans up and then dies of that same signal, so cron sees a failure instead of a success.
- **Safe temp directory:** `mktemp -d` under `/var/tmp` with `umask 077` replaces the guessable `/tmp/backup.$$`.
- **Failures stop the run:** strict mode plus explicit checks on `tar` and `scp` mean a failed step stops the script, prints a message to stderr and exits non-zero. It no longer uploads a broken archive.
- **Fixed `PATH`:** cron runs the script with whatever environment it inherits, so the script now sets its own `PATH`.
- **Other fixes:** every expansion is quoted, `$(...)` replaces backticks, and `--` goes before path arguments.
- **One behaviour change: `-o BatchMode=yes` on `scp`.** If the SSH key or host key isn't accepted, `scp` now fails straight away instead of waiting at a prompt. That waiting is a likely cause of the killed runs that leave the directory behind. Remove the option if you rely on something interactive.

## Still to check

1. Run `shellcheck scripts/backup.sh` and `bash -n scripts/backup.sh`.
2. Run it with `DATA_DIR` pointed at a scratch directory and `REMOTE` at a test host, and confirm it exits 0.
3. Make it fail: use a missing `DATA_DIR`, then an unreachable host. Each time, confirm a non-zero exit status, a message on stderr, and nothing left in `/home/user/other-checkout*`.
4. Start a run and send it `kill -TERM`. The exit status should be 143 and the temp directory should be gone.
