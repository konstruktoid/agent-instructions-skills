I don't have a file-writing or shell tool in this session, so I couldn't save the script or run it. It's below to drop in as `scripts/backup-etc.sh`. That also means none of the skill's checks were run (`shellcheck`, `bash -n`, a test run, a failure-path run). Please run them before scheduling it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven archives. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs privileged and unattended: set the environment rather than inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077 # /etc holds shadow, keys and credentials: archives are root-only

readonly PROGNAME="${0##*/}"
readonly SHARE='/mnt/backup'
readonly BACKUP_DIR="${SHARE}/etc"
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

# Deletes all but the newest KEEP archives. The names embed a UTC timestamp,
# so the C-locale glob order is chronological.
# Globals: BACKUP_DIR, KEEP
prune_archives() {
  local -a archives
  local count

  shopt -s nullglob
  archives=("${BACKUP_DIR}"/etc-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]T[0-9][0-9][0-9][0-9][0-9][0-9]Z.tar.gz)
  shopt -u nullglob

  count=${#archives[@]}
  if ((count > KEEP)); then
    rm -f -- "${archives[@]:0:count-KEEP}"
  fi
}

main() {
  local stamp archive lock_fd

  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi
  if ((EUID != 0)); then
    err 'must run as root to read all of /etc'
    return 77
  fi

  # Fail closed: without the share mounted, the archive would silently land
  # on the local disk under the mount point.
  if ! mountpoint -q -- "${SHARE}"; then
    err "backup share not mounted: ${SHARE}"
    return 69
  fi
  mkdir -p -- "${BACKUP_DIR}"

  # Prevent two overlapping runs from racing on the same files.
  exec {lock_fd}>"${LOCK_FILE}"
  if ! flock -n "${lock_fd}"; then
    err 'another backup is already running'
    return 75
  fi

  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${BACKUP_DIR}/etc-${stamp}.tar.gz"

  # Write on the same filesystem, then rename: a reader never sees a partial
  # archive, and an interrupted run leaves nothing that matches the prune glob.
  partial="$(mktemp -- "${BACKUP_DIR}/.etc-${stamp}.XXXXXXXXXX")"

  if ! tar --create --gzip --numeric-owner --acls --xattrs \
    --file "${partial}" --directory / -- etc; then
    err 'tar failed; keeping existing archives untouched'
    return 1
  fi

  mv -f -- "${partial}" "${archive}"
  partial=''

  # Prune only after a new archive exists, so a failing run never shrinks the set.
  prune_archives
}

main "$@"
```

**How it behaves:**
- **Archive name and location:** archives go to `/mnt/backup/etc/etc-YYYYMMDDTHHMMSSZ.tar.gz`. I took `/mnt/backup` from the existing `scripts/backup.sh`. Change `SHARE` if your share is mounted somewhere else. Paths inside the tarball are relative (`etc/...`), so restoring with `tar -xzf … -C /` doesn't depend on where you run it.
- **Unmounted share:** if `/mnt/backup` isn't a mount point, the script exits with an error instead of quietly filling the local disk.
- **Pruning:** old archives are only deleted after a new one has been written in full. Only files matching the exact `etc-<timestamp>Z.tar.gz` pattern can be deleted, so nothing else in the directory is touched. Leftover temp files are hidden dotfiles that the pattern doesn't match.
- **Permissions:** archives are mode 0600 (owner-only), because `/etc` contains `shadow` and private keys. If the share is NFS with root squashing, root may not be able to write there. That would show up as an error, not an empty backup.
- **Overlapping runs:** a lock file stops two runs at once. If one is already running, the new one exits with status 75.
- **Exit codes:** 64 = bad usage, 77 = not root, 69 = share not mounted, 75 = already running, 1 = `tar` failed. If interrupted, it deletes its partial file and exits with the signal's status.

**Decision for you:** with GNU `tar`, exit status 1 means "a file changed while being read." The script counts that as a failure, which is the safe choice. If package updates during the backup window cause false alarms, that's where to relax it.

**Checks to run:**
```bash
shellcheck scripts/backup-etc.sh && bash -n scripts/backup-etc.sh
```
To test it safely, point `SHARE` at a scratch mount and run it more than seven times; only seven archives should remain. Then unmount the scratch share and run it again; it should exit 69.

**Separate problem in `scripts/backup.sh`:** it uses a predictable `/tmp/backup.$$` path and unquoted variables, it has no strict mode, and it skips cleanup if `tar` or `scp` fails. I left it alone, but I can harden it the same way if you want.
