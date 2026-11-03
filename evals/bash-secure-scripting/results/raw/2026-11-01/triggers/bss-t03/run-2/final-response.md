I found the problem in `scripts/backup.sh`. I couldn't apply the fix, though: this session only gives me read and search tools (no edit, write or shell), so the corrected script below isn't saved or tested.

## What's wrong

```bash
TMP=/tmp/backup.$$
mkdir $TMP
tar czf $TMP/data.tar.gz $DATA_DIR
scp ... 
rm -rf $TMP          # only reached if every earlier step "works"
```

1. **The cleanup only runs if the script reaches the last line.** If the script is interrupted, or you add `set -e`, the `rm` never runs. Without `set -e` the opposite problem happens: if `tar` or `scp` fails, the script keeps going, deletes the directory and exits 0. So cron never hears that the backup failed.
2. **The temp path is predictable** (`/tmp/backup.$$`). Anyone on the host can create that path or a symlink there ahead of time, and the script will write the backup of `/srv/ledger/data` into it. For a backup of ledger data that's a real exposure, not just mess. `mkdir` also fails if a previous run left a directory with the same PID behind.
3. **Nothing is quoted, and it relies on cron's `PATH` and `umask`.** That means the archive may be readable by every user on the host.

## Suggested fix: `scripts/backup.sh`

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: don't rely on the caller's environment.
PATH='/usr/local/bin:/usr/bin:/bin'
export PATH
export LC_ALL=C
umask 077

readonly PROGNAME="${0##*/}"
readonly DATA_DIR='/srv/ledger/data'
readonly REMOTE='backup@archive.example.internal'
readonly TARGET='/mnt/backup'

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

  # Install traps before mktemp so there is no window where the path is lost.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXXXXXX")"

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

## What changes

- **Cleanup runs every time the script exits.** It's in an `EXIT` trap, set up before the temp directory is created, so a normal finish, a failed step or an exit from `set -e` all remove it. INT, TERM and HUP also clean up, then re-raise the signal so the run doesn't report success.
- **The temp directory comes from `mktemp -d`.** The name is random and the directory is mode 0700, which removes the pre-created path and symlink risk.
- **Failures now show up.** If `tar` or `scp` fails, the script writes a message to stderr and exits non-zero, so cron's mail or your monitoring will see it. Before, it exited 0.
- **Smaller fixes:**
  - all expansions are quoted;
  - `$(...)` replaces backticks;
  - `PATH`, locale and `umask 077` are fixed, so the archive isn't readable by other users;
  - the date is UTC, so the file name doesn't depend on the server's timezone.

## Checks to run after applying it

```bash
shellcheck scripts/backup.sh && bash -n scripts/backup.sh
# Failure path: point DATA_DIR at a missing dir (or block the scp host), then:
./scripts/backup.sh; echo "exit=$?"; ls -d /tmp/backup.* 2>/dev/null   # expect non-zero exit, no leftovers
```

If you give me edit and shell access, I'll apply the change and run these checks myself.
