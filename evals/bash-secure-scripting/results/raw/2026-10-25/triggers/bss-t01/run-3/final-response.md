I don't have a shell or file-write tool in this session, so the script is below for you to save. I haven't run it, `shellcheck`, or `bash -n` on it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs privileged and unattended: set the environment instead of inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077 # the archive holds /etc/shadow and private keys

readonly PROGNAME="${0##*/}"
readonly SHARE_ROOT='/mnt/backup'         # mount point of the backup share
readonly BACKUP_DIR="${SHARE_ROOT}/etc"   # where the tarballs live
readonly KEEP=7
readonly LOCK_FILE='/run/lock/etc-backup.lock'

# Script scope: the EXIT trap runs after main has returned.
partial=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${partial} && -f ${partial} ]]; then
    rm -f -- "${partial}"
  fi
  return 0
}

# Clean up, then die of the signal so the caller sees 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Deletes all but the newest KEEP archives for this host.
# Globals: BACKUP_DIR, KEEP
# Arguments: host name used in the archive prefix
prune() {
  local host="$1"
  local -a archives=()
  local i

  # Names embed a UTC timestamp, so C-locale glob order is oldest first.
  archives=("${BACKUP_DIR}/etc-${host}-"[0-9]*Z.tar.gz)
  for ((i = 0; i < ${#archives[@]} - KEEP; i++)); do
    # Only regular files; never follow a symlink planted on the share.
    if [[ -f ${archives[i]} && ! -L ${archives[i]} ]]; then
      rm -f -- "${archives[i]}"
    fi
  done
}

main() {
  local host stamp archive

  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  # Fail closed: if the share is not mounted, writing would fill the local disk
  # and pruning would act on the wrong directory.
  if ! mountpoint -q -- "${SHARE_ROOT}"; then
    err "${SHARE_ROOT} is not mounted"
    return 69
  fi
  if [[ ! -d ${BACKUP_DIR} || -L ${BACKUP_DIR} ]]; then
    err "${BACKUP_DIR} missing or a symlink"
    return 73
  fi

  # Refuse to run twice at once; two prunes could race and delete too much.
  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  host="$(hostname -s)"
  if [[ ! ${host} =~ ^[A-Za-z0-9][A-Za-z0-9-]*$ ]]; then
    err "unexpected host name: ${host}"
    return 70
  fi
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${BACKUP_DIR}/etc-${host}-${stamp}.tar.gz"

  # Traps before mktemp: cleanup tolerates the empty variable until it is set.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  # Same directory as the final name, so the mv below is an atomic rename.
  partial="$(mktemp -- "${BACKUP_DIR}/.etc-${host}.XXXXXX.partial")"

  if ! tar --create --gzip --acls --xattrs --numeric-owner \
    --file "${partial}" --directory / -- etc; then
    err "tar failed; no archive written, nothing pruned"
    return 1
  fi
  if ! gzip --test -- "${partial}"; then
    err "archive failed integrity check; nothing pruned"
    return 1
  fi

  mv -- "${partial}" "${archive}"
  partial=''

  # Prune only after a verified new copy is in place.
  prune "${host}"
  printf '%s: wrote %s\n' "${PROGNAME}" "${archive}"
}

main "$@"
```

**Choices that matter:**
- **Checks the share is mounted.** If the share isn't mounted, `mountpoint -q` makes the script stop instead of writing the tarball to the local disk under `/mnt/backup`. This is the most common way this kind of job goes wrong without anyone noticing.
- **No half-written archives.** It writes to a `.partial` temp file in the same directory, checks it with `gzip --test`, then renames it to the final name. If tar fails or the job is killed, the trap deletes the partial file.
- **Old copies are deleted only after a good new one exists.** A failed run never cuts you below seven. Pruning only matches this host's `etc-<host>-<UTC stamp>.tar.gz` files and skips symlinks.
- **Hostname in the file name.** Several machines can share the same backup directory without pruning each other's copies.
- **`flock` stops overlapping runs**, and `umask 077` keeps the archive readable by root only, since it contains `/etc/shadow` and private keys.
- **Distinct exit codes** for each failure: 77 not root, 69 share not mounted, 73 bad backup directory, 75 another run holds the lock, 70 unexpected hostname, 1 tar or integrity check failed.

**Before you schedule it:**
1. Set `SHARE_ROOT` to your actual mount point. I guessed `/mnt/backup`, and the `etc/` folder under it has to exist already.
2. GNU tar exits 1 when a file changes while it's being read. The script treats that as a failure. If that happens too often on your system, accept exit 1 as a warning.
3. Run `shellcheck etc-backup.sh && bash -n etc-backup.sh`. Then do a test run with a scratch directory as `SHARE_ROOT`, and one with the share unmounted to confirm it exits 69 and leaves nothing behind.

Example cron line: `30 2 * * * root /usr/local/sbin/etc-backup.sh`
