I don't have a file-writing or shell tool in this session, so I couldn't save this to disk or run any checks on it. Here's the script for you to save as something like `/usr/local/sbin/backup-etc`:

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven archives. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs as root from a scheduler: set the environment rather than inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C # also makes glob results sort bytewise, i.e. chronologically
umask 077       # /etc holds shadow and private keys: archives are 0600

readonly PROGNAME="${0##*/}"
readonly BACKUP_MOUNT='/mnt/backup' # mount point of the backup share
readonly DEST_DIR="${BACKUP_MOUNT}/etc-archives"
readonly KEEP=7
readonly LOCK_FILE='/run/backup-etc.lock'
readonly NAME_RE='^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$'

# Script scope: the EXIT trap runs after the function that sets it has returned.
tmp_archive=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

log() {
  printf '%s: %s\n' "${PROGNAME}" "$*"
}

cleanup() {
  if [[ -n ${tmp_archive} && -e ${tmp_archive} ]]; then
    rm -f -- "${tmp_archive}"
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

# Fails closed: if the share isn't mounted, writing to DEST_DIR would fill the
# local disk under the mount point instead of reaching the backup share.
preflight() {
  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi
  if ! mountpoint -q "${BACKUP_MOUNT}"; then
    err "backup share is not mounted at ${BACKUP_MOUNT}"
    return 69
  fi
  if [[ -L ${DEST_DIR} || ! -d ${DEST_DIR} ]]; then
    err "${DEST_DIR} is missing, not a directory, or a symlink"
    return 73
  fi
  if [[ ! -w ${DEST_DIR} ]]; then
    err "${DEST_DIR} is not writable"
    return 73
  fi
}

# Writes to a temp file on the same share, verifies it, then renames it into
# place so a partial archive never carries a final name.
create_archive() {
  local final

  final="${DEST_DIR}/etc-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
  if [[ -e ${final} || -L ${final} ]]; then
    err "refusing to overwrite ${final}"
    return 73
  fi

  tmp_archive="$(mktemp -- "${DEST_DIR}/.etc-XXXXXXXX.partial")"
  tar --create --gzip --one-file-system --file "${tmp_archive}" \
    --directory / -- etc
  tar --list --gzip --file "${tmp_archive}" >/dev/null

  mv -T -- "${tmp_archive}" "${final}"
  tmp_archive=''
  log "created ${final}"
}

# Deletes only regular files whose names match this script's own pattern,
# oldest first, leaving the newest KEEP.
prune_archives() {
  local -a archives=()
  local path name excess i

  for path in "${DEST_DIR}"/etc-*.tar.gz; do
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

  # Traps go in before mktemp; cleanup is a no-op while tmp_archive is empty.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP

  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  create_archive
  prune_archives # only reached after a verified new archive exists
}

main "$@"
```

Install it as root-owned and not group- or world-writable (`install -o root -g root -m 0700 ...`). Then schedule it, for example with `/etc/cron.d/backup-etc`:

```
30 2 * * * root /usr/local/sbin/backup-etc
```

**How it behaves:**
- **Retention:** Old copies are only deleted after a new archive has been written and read back successfully. If a run fails, you keep your existing seven copies.
- **Share not mounted:** The script refuses to run. Otherwise it would quietly write into the empty local directory under `/mnt/backup`.
- **Deletions:** Only files matching `etc-YYYYmmddTHHMMSSZ.tar.gz` can be deleted, and never symlinks. Other files on the share are left alone.
- **Interrupted runs:** Nothing half-written is left on the share. The `.partial` temp file is removed on any error or signal.
- **Overlapping runs:** A lock (`flock`) stops two runs at once. Each failure type exits with its own non-zero code.

**Things to check or adjust:**
- **Paths:** `BACKUP_MOUNT` and `DEST_DIR` are guesses at your layout. Change them, and create `DEST_DIR` once by hand.
- **Network share permissions:** If the share is CIFS/SMB, file modes depend on the mount options (`file_mode=`, `uid=`). The archives contain `/etc/shadow` and private keys, so make sure the share only lets backup admins read them.
- **Strict about failures:** Any warning from `tar` (for example "file changed as we read it") fails the run. That's on purpose, because a possibly inconsistent archive is treated as a failure.
- **ACLs, xattrs, SELinux labels:** These aren't saved. Add `--acls --xattrs` (or `--selinux`) if your restores need them.

**Not yet verified:** I haven't run `shellcheck`, `bash -n`, or the script itself, so treat it as untested. Before scheduling it:
1. Run `shellcheck backup-etc && bash -n backup-etc`.
2. Point `BACKUP_MOUNT` at a scratch mount and run it nine times to confirm only seven archives remain.
3. Unmount the share and check that it exits with 69 and writes nothing.
