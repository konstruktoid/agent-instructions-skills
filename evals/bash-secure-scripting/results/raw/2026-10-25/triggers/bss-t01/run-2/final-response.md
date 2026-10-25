I've written the script below, but I haven't checked or run it. This session only has read and search tools, so I couldn't save the file or run `shellcheck`, `bash -n` or a test run. The paths are placeholders: I don't know your backup share's mount point, so set `SHARE_MOUNT` before using it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven archives. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs as root from a scheduler: set the environment rather than inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
# The archive holds /etc/shadow and private keys: owner-only.
umask 077

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR='/etc'
readonly SHARE_MOUNT='/mnt/backup'
readonly BACKUP_DIR="${SHARE_MOUNT}/etc"
readonly KEEP=7
readonly LOCK_FILE='/run/lock/backup-etc.lock'
readonly NAME_RE='^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$'

# Script scope, not local: the EXIT trap runs after the function has returned.
partial=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

log() {
  printf '%s: %s\n' "${PROGNAME}" "$*"
}

cleanup() {
  if [[ -n ${partial} && -f ${partial} ]]; then
    rm -f -- "${partial}"
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

# Refuses to run unless the share is really mounted, so an unmounted share
# never fills the local disk under the empty mount point.
# Returns: 77 not root, 69 share not mounted, 73 unusable backup directory
preflight() {
  if ((EUID != 0)); then
    err "must run as root to read all of ${SOURCE_DIR}"
    return 77
  fi
  if ! mountpoint -q -- "${SHARE_MOUNT}"; then
    err "backup share is not mounted at ${SHARE_MOUNT}"
    return 69
  fi
  if [[ -L ${BACKUP_DIR} ]]; then
    err "refusing symlinked backup directory: ${BACKUP_DIR}"
    return 73
  fi
  if [[ ! -d ${BACKUP_DIR} ]]; then
    mkdir -m 700 -- "${BACKUP_DIR}"
  fi
  if [[ ! -w ${BACKUP_DIR} ]]; then
    err "backup directory is not writable: ${BACKUP_DIR}"
    return 73
  fi
}

# Writes the archive to a hidden temporary name on the share, reads it back,
# then renames it into place so a partial archive never looks like a backup.
# Globals: BACKUP_DIR, SOURCE_DIR, partial
create_archive() {
  local stamp final

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  final="${BACKUP_DIR}/etc-${stamp}.tar.gz"
  if [[ -e ${final} ]]; then
    err "archive already exists: ${final}"
    return 73
  fi

  partial="$(mktemp -- "${BACKUP_DIR}/.etc-${stamp}.XXXXXX")"
  tar --create --gzip --numeric-owner --file "${partial}" \
    --directory / -- "${SOURCE_DIR#/}"

  # A truncated write on a network share shows up here, before pruning.
  tar --list --gzip --file "${partial}" >/dev/null

  mv --no-clobber -- "${partial}" "${final}"
  if [[ -e ${partial} ]]; then
    err "could not move archive into place: ${final}"
    return 73
  fi
  partial=''
  log "created ${final}"
}

# Deletes all but the newest KEEP archives. Only names matching NAME_RE are
# considered, so nothing else on the share can be removed.
# Globals: BACKUP_DIR, KEEP, NAME_RE
prune_archives() {
  local -a archives=()
  local path name excess i

  # Under LC_ALL=C the glob sorts bytewise, which is oldest first for these names.
  for path in "${BACKUP_DIR}"/etc-*.tar.gz; do
    name="${path##*/}"
    if [[ ${name} =~ ${NAME_RE} && -f ${path} && ! -L ${path} ]]; then
      archives+=("${path}")
    fi
  done

  excess=$((${#archives[@]} - KEEP))
  for ((i = 0; i < excess; i++)); do
    rm -f -- "${archives[i]}"
    log "removed ${archives[i]}"
  done
}

main() {
  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi

  preflight

  exec 9>"${LOCK_FILE}"
  if ! flock --nonblock 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  # Traps before mktemp; cleanup tolerates the empty path until it is set.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  create_archive
  # Old copies are pruned only after a new archive is verified and in place.
  prune_archives
}

main "$@"
```

**How it behaves:**
- **Unmounted share:** if the share isn't mounted, the script exits with code 69 and writes nothing. Otherwise it would fill the local disk under the empty mount point.
- **Old copies:** old archives are deleted only after the new one has been written, read back with `tar --list` and renamed into place. A failed run never shrinks the set of good backups.
- **Partial archives:** the archive is written under a hidden temporary name on the share. If the script fails or is interrupted, that file is deleted, so a half-written file never looks like a backup.
- **Safe pruning:** pruning only touches files named exactly like `etc-20261025T020000Z.tar.gz`, and never symlinks. Other files on the share are left alone.
- **Permissions:** with `umask 077` the archive is readable only by root, which matters because it contains `/etc/shadow` and private keys.
- **Overlapping runs:** `flock` stops two runs from overlapping. If a run is already going, the script exits with code 75.

**Things to check for your setup:**
- **Changed files:** GNU tar exits 1 if a file changes while it's being read ("file changed as we read it"). The script treats that as a failure. If `/etc` changes a lot on your host, run the backup at a quiet time.
- **Root squash:** if the share is NFS with root squash, root may not be able to write to `BACKUP_DIR`. The preflight check catches this and exits with code 73.
- **ACLs and SELinux labels:** add `--acls --xattrs --selinux` to the `tar` command if you need to keep them and your tar supports these options.

**Before relying on it,** run:

```bash
shellcheck backup-etc.sh && bash -n backup-etc.sh
```

Then do a test run with `SHARE_MOUNT` pointing at a scratch mount. Check the exit status and that eight runs leave seven archives. Also run it once with the share unmounted to check that it exits 69 and leaves nothing behind.

To run it nightly from cron, as root:

```
15 2 * * * /usr/local/sbin/backup-etc.sh
```
