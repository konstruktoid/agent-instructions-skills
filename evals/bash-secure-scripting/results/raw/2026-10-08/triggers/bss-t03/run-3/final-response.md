I couldn't apply the fix: this session only has read and search tools, so I couldn't edit `scripts/backup.sh` or run `shellcheck`, `bash -n`, or the script. Below is the replacement script. Nothing in it has been run or checked yet.

## Why the directory gets left behind

`scripts/backup.sh:7-13` only removes the directory with `rm -rf $TMP` on the last line. Any exit before that line skips the cleanup. That includes being killed mid-run (a cron timeout, a reboot, `scp` hanging until someone kills it) and the script being changed later to stop on errors. There's nothing that cleans up on the way out. It has related problems too:

- **It doesn't report failure.** There's no strict mode, so a failed `tar` still lets `scp` upload a broken archive, and the script can report success to cron.
- **The temp path is predictable.** `/tmp/backup.$$` can be guessed in advance, so another user could create it or point it elsewhere. `mkdir` would then fail, and the script would carry on writing into whatever is at that path.
- **Variables aren't quoted, and the environment comes from cron** (`PATH`, `TMPDIR`, `umask`).

## Fixed `scripts/backup.sh`

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting the caller's.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE=backup@archive.example.internal

# Script scope, not local to main: the EXIT trap runs after main has returned.
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

# Clean up, then die of the signal so cron/the caller sees 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: cleanup tolerates the empty workdir until it is assigned.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d "${TMPDIR}/backup.XXXXXXXXXX")"

  stamp="$(date +%F)"

  if ! tar -czf "${workdir}/data.tar.gz" -- "${DATA_DIR}"; then
    err "tar of ${DATA_DIR} failed"
    return 1
  fi

  # BatchMode: fail instead of hanging on a prompt when run unattended.
  if ! scp -q -o BatchMode=yes -- "${workdir}/data.tar.gz" \
    "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

## What changed

- **Cleanup always runs.** It's triggered on `EXIT`, which covers errors, normal completion and any early `return`. `INT`, `TERM` and `HUP` also clean up, then let the script die of that signal so cron sees it was killed rather than a success.
- **The cleanup is in place before the temp directory exists.** The traps are set first, so there's no moment when the directory exists and nothing would remove it.
- **The temp directory is unpredictable and private.** `mktemp -d` creates it under `/var/tmp`, with `umask 077` so only the owner can read it.
- **A failed step stops the script with a non-zero exit** and a message on stderr, which cron mails. `tar` and `scp` are checked explicitly.
- **Behaviour changes to note:**
  - `scp -o BatchMode=yes` now fails instead of hanging if key-based login breaks.
  - The temp directory moved from `/tmp` to `/var/tmp`.
  - The shebang changed from `#!/bin/bash` to `#!/usr/bin/env bash`.

## To verify after applying

1. `shellcheck scripts/backup.sh && bash -n scripts/backup.sh`
2. Point `DATA_DIR` at a missing path, run the script, and check that it exits non-zero and leaves no `/var/tmp/backup.*` behind.
3. Start a run, send it `kill -TERM`, and check that the exit status is 143 and the directory is gone.

If you give me write and shell access, I can apply the fix and run these checks myself.
