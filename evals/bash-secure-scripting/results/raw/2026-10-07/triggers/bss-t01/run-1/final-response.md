I couldn't save this as a file or run it. Write was disabled in this session, there was no shell tool to run `shellcheck`, `bash -n` or a test run, and reads of the skill's reference files were denied. The script is below, unlinted and untested. I'd suggest saving it as `scripts/backup-etc.sh`, next to the existing `backup.sh`, then running `shellcheck -x` and `bash -n` on it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies.
#
# Usage: backup-etc.sh [-m] [BACKUP_DIR]
#   BACKUP_DIR  absolute path of the backup share (default: /mnt/backup)
#   -m          skip the check that BACKUP_DIR is a mount point

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs as root, often from cron: do not trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR="/etc"
readonly DEFAULT_BACKUP_DIR="/mnt/backup"
readonly KEEP=7

# Script scope: the EXIT trap runs after main has returned.
tmpfile=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${tmpfile} && -e ${tmpfile} ]]; then
    rm -f -- "${tmpfile}"
  fi
  return 0
}

# Clean up, then die of the signal so the caller sees 128+n.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Deletes all but the newest KEEP archives. Names embed a UTC timestamp, so
# lexical order (LC_ALL=C) is chronological order.
# Arguments: backup directory
prune() {
  local dir="$1"
  local -a archives
  local i

  shopt -s nullglob
  archives=("${dir}"/etc-????????T??????Z.tar.gz)
  shopt -u nullglob

  for ((i = 0; i < ${#archives[@]} - KEEP; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  local check_mount=1
  local opt backup_dir lock_fd stamp dest

  while getopts ':m' opt; do
    case "${opt}" in
      m) check_mount=0 ;;
      *)
        err "usage: ${PROGNAME} [-m] [BACKUP_DIR]"
        return 64
        ;;
    esac
  done
  shift $((OPTIND - 1))

  if (($# > 1)); then
    err "usage: ${PROGNAME} [-m] [BACKUP_DIR]"
    return 64
  fi
  backup_dir="${1:-${DEFAULT_BACKUP_DIR}}"

  if [[ ${backup_dir} != /* ]]; then
    err "backup directory must be an absolute path: ${backup_dir}"
    return 2
  fi
  if [[ ! -d ${backup_dir} || ! -w ${backup_dir} ]]; then
    err "backup directory missing or not writable: ${backup_dir}"
    return 1
  fi
  # An unmounted share would silently fill the local disk instead.
  if ((check_mount)) && ! mountpoint -q -- "${backup_dir}"; then
    err "backup share is not mounted: ${backup_dir}"
    return 1
  fi

  # Only one run at a time; the lock is released when the shell exits.
  exec {lock_fd}>"${backup_dir}/.etc-backup.lock"
  if ! flock -n "${lock_fd}"; then
    err "another backup is already running"
    return 1
  fi

  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  # Build in the destination directory so the final mv is an atomic rename
  # and a half-written archive never matches the prune pattern.
  tmpfile="$(mktemp -- "${backup_dir}/.etc-backup.XXXXXX")"

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  dest="${backup_dir}/etc-${stamp}.tar.gz"

  tar --create --gzip --one-file-system --file "${tmpfile}" -- "${SOURCE_DIR}"
  mv -- "${tmpfile}" "${dest}"
  tmpfile=''

  prune "${backup_dir}"
  printf '%s: wrote %s\n' "${PROGNAME}" "${dest}"
}

main "$@"
```

**What it does**
- **Naming:** it writes `etc-<UTC timestamp>.tar.gz` to the backup directory. The default is `/mnt/backup`, the same share the existing `scripts/backup.sh` uses. Pass another absolute path as an argument to change it.
- **Retention:** after a successful archive it deletes all but the newest seven `etc-*.tar.gz` files. Pruning runs only after the new archive is in place, so a failed run never costs you an old copy.
- **Safe writes:** the tarball is built under a temporary name on the share and renamed into place. An interrupted run leaves no partial file that could be mistaken for a backup, and the trap removes the temporary file on errors and signals.
- **Mount check:** it refuses to run if the directory isn't a mount point, because an unmounted share would otherwise fill the local disk. Use `-m` to skip the check when testing against a plain directory.
- **Locking:** `flock` stops two runs from overlapping.
- **Environment:** it sets its own `PATH` and `umask 077`, so the archives are readable only by their owner. `/etc` contains secrets.

**Things to know**
- `tar` exits 1 if a file in `/etc` changes while it is being read. The script treats that as a failure, so nothing is renamed or pruned. If that causes noisy nightly failures, accept exit status 1 as a warning.
- `flock` on an NFS or CIFS share can be unreliable. If the lock misbehaves, move the lock file to `/run/lock`.

When Write and a shell are available, I can save the file and run the full `shellcheck`, `bash -n` and test-run loop against a scratch directory.
