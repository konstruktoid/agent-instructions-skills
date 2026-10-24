I couldn't save or run the script in this session: I have no write or shell tools, so I couldn't save the file or run `shellcheck`, `bash -n` or a test. Here it is to save as `scripts/backup-etc.sh`. I took the backup share to be `/mnt/backup`, the path the existing `scripts/backup.sh` uses; change `BACKUP_ROOT` if yours is somewhere else.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs privileged and unattended: don't trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR='/etc'
readonly BACKUP_ROOT='/mnt/backup'
readonly DEST_DIR="${BACKUP_ROOT}/etc"
readonly KEEP=7
readonly LOCK_FILE='/run/lock/backup-etc.lock'

# Script scope: the EXIT trap runs after main has returned.
partial=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${partial} && -e ${partial} ]]; then
    rm -f -- "${partial}"
  fi
  return 0
}

on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Removes all but the newest KEEP archives. Names are UTC timestamps, so the
# C-locale glob order is chronological order.
# Globals: DEST_DIR, KEEP
prune_old() {
  local -a archives=("${DEST_DIR}"/etc-[0-9]*T[0-9]*Z.tar.gz)
  local count=${#archives[@]}
  local i

  if ((count <= KEEP)); then
    return 0
  fi
  for ((i = 0; i < count - KEEP; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  local stamp archive

  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi
  if ((EUID != 0)); then
    err "must run as root to read all of ${SOURCE_DIR}"
    return 77
  fi

  # Fail closed if the share isn't mounted, or the archive would land on
  # the local disk underneath the mount point.
  if ! mountpoint -q -- "${BACKUP_ROOT}"; then
    err "${BACKUP_ROOT} is not mounted"
    return 69
  fi

  # Only one run at a time; a second concurrent run would race the pruning.
  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  mkdir -p -- "${DEST_DIR}"
  chmod 700 -- "${DEST_DIR}"

  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${DEST_DIR}/etc-${stamp}.tar.gz"

  # Write to a hidden temp file on the same filesystem, then rename into
  # place, so a crash never leaves a truncated file that looks complete.
  partial="$(mktemp -- "${DEST_DIR}/.etc-${stamp}.XXXXXX")"

  if ! tar --create --gzip --file "${partial}" \
    --one-file-system --acls --xattrs --numeric-owner \
    -C / -- "${SOURCE_DIR#/}"; then
    err "tar failed for ${SOURCE_DIR}"
    return 1
  fi
  if ! tar --list --gzip --file "${partial}" >/dev/null; then
    err "archive verification failed: ${partial}"
    return 1
  fi

  chmod 600 -- "${partial}"
  mv -f -- "${partial}" "${archive}"
  partial=''

  # Prune only after a good new copy exists.
  prune_old
  printf '%s: wrote %s\n' "${PROGNAME}" "${archive}"
}

main "$@"
```

**How it works:**
- **Old copies are deleted only after a good new one exists.** Each archive is written to a hidden temp file, checked with `tar --list`, and only then renamed into place. A failed or interrupted run deletes nothing and leaves no partial file.
- **It refuses to run if the share isn't mounted** (`mountpoint -q`). Without this check, the archives would quietly fill the local disk under `/mnt/backup`.
- **Only one copy can run at a time.** It uses `flock`, so overlapping cron runs can't both prune at once.
- **Retention goes by name, not file times.** Names are UTC timestamps like `etc-20261024T020000Z.tar.gz`, so sorting them gives the age order. Pruning only matches files named that way, so nothing else on the share gets deleted.
- **It doesn't depend on who starts it.** It sets its own `PATH` and locale, and with `umask 077`, `/etc` (which includes `shadow`) is never stored readable by others.
- **It exits with a distinct code for each failure** and prints the reason to stderr.

**Things to adjust:**
- GNU `tar` exits 1 if a file changes while it's being read. The script treats that as a failure, so a rare run may fail and need rerunning.
- If the share is NFS with `root_squash`, root can't create files on it. You'd need a mount option change or a dedicated backup user.

**Example cron entry** (`/etc/cron.d/backup-etc`):
```
15 2 * * * root /usr/local/sbin/backup-etc.sh
```

**Checks to run before relying on it:**
1. `shellcheck scripts/backup-etc.sh` and `bash -n scripts/backup-etc.sh`.
2. Point `BACKUP_ROOT` at a scratch mount and run it nine times. Confirm exactly seven archives remain and that `$?` is 0.
3. Unmount the scratch share and run it again. It should exit 69 and write nothing.

Separately, the existing `scripts/backup.sh` has real problems: unquoted variables, a guessable temp path in `/tmp`, no error checking, and cleanup that's skipped if anything fails. Do you want me to harden that one too?
