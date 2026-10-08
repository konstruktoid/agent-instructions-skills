I don't have file-write or shell tools in this session, so the script is below rather than saved to disk. That also means I couldn't run `shellcheck`, `bash -n` or a test run, so treat it as unverified until you do.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a compressed tarball on the backup share and keep the
# newest seven archives. Intended to run as root from cron or a systemd timer.
#
# Usage: backup-etc.sh

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs as root from a scheduler: don't trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C # also makes glob order byte-wise, which pruning relies on
umask 077       # archives contain /etc/shadow and private keys

readonly PROGNAME="${0##*/}"
readonly BACKUP_MOUNT='/mnt/backup'
readonly BACKUP_DIR="${BACKUP_MOUNT}/etc"
readonly LOCK_FILE='/run/lock/backup-etc.lock' # local: flock on NFS/CIFS is unreliable
readonly KEEP=7
readonly PREFIX='etc-'
readonly SUFFIX='.tar.gz'
readonly NAME_RE='^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$'

# Script scope: the EXIT trap runs after main has returned.
tmp_archive=''
lock_fd=''

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

# Removes all but the newest KEEP archives in BACKUP_DIR.
# Globals: BACKUP_DIR, PREFIX, SUFFIX, NAME_RE, KEEP
# Only files whose names match NAME_RE exactly are considered; anything else
# in the directory is left alone.
prune_archives() {
  local -a archives=()
  local f name excess i

  shopt -s nullglob
  for f in "${BACKUP_DIR}/${PREFIX}"*"${SUFFIX}"; do
    name="${f##*/}"
    if [[ ${name} =~ ${NAME_RE} && -f ${f} && ! -L ${f} ]]; then
      archives+=("${f}")
    fi
  done
  shopt -u nullglob

  # UTC timestamps in the name sort chronologically under LC_ALL=C.
  excess=$((${#archives[@]} - KEEP))
  for ((i = 0; i < excess; i++)); do
    log "removing old archive ${archives[i]##*/}"
    rm -f -- "${archives[i]}"
  done
}

main() {
  local archive status

  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi

  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  # Fail closed: if the share isn't mounted, writing would fill the local disk.
  if ! mountpoint -q "${BACKUP_MOUNT}"; then
    err "backup share is not mounted at ${BACKUP_MOUNT}"
    return 69
  fi

  mkdir -p -- "${BACKUP_DIR}"

  exec {lock_fd}>"${LOCK_FILE}"
  if ! flock --nonblock "${lock_fd}"; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  # Traps before mktemp; cleanup tolerates the empty path until it is assigned.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  # Same directory as the final archive, so the mv below is an atomic rename.
  # The leading dot keeps a partial file out of the prune glob.
  tmp_archive="$(mktemp -- "${BACKUP_DIR}/.${PREFIX}partial.XXXXXXXXXX")"

  # GNU tar exits 1 when a file changed while being read; that is a warning
  # for a live /etc, while 2 or more is a real failure.
  status=0
  tar --create --gzip --file "${tmp_archive}" --directory / -- etc || status=$?
  if ((status == 1)); then
    err "warning: some files changed while being archived"
  elif ((status != 0)); then
    err "tar failed with status ${status}"
    return 1
  fi

  if ! gzip --test -- "${tmp_archive}"; then
    err "archive failed integrity check"
    return 1
  fi

  archive="${BACKUP_DIR}/${PREFIX}$(date -u +%Y%m%dT%H%M%SZ)${SUFFIX}"
  if [[ -e ${archive} ]]; then
    err "refusing to overwrite existing ${archive}"
    return 1
  fi
  mv -- "${tmp_archive}" "${archive}"
  tmp_archive=''
  log "created ${archive}"

  # Prune only after a new archive exists, so a failed run never deletes good copies.
  prune_archives
}

main "$@"
```

**What it does:**
- **Won't write to local disk by mistake:** it stops with status 69 if `/mnt/backup` isn't a mounted filesystem. Otherwise an unmounted share would quietly fill up the root disk.
- **No half-written archives:** it builds the tarball under a hidden temp name in the backup directory, checks it with `gzip --test`, then renames it into place. If the run fails or is interrupted, the trap deletes the partial file.
- **Old copies are only deleted after a good backup:** if a run fails, all existing archives stay. It only deletes files named exactly `etc-YYYYMMDDTHHMMSSZ.tar.gz`, so nothing else in the directory is touched.
- **One run at a time:** a lock file in `/run/lock` stops two runs from overlapping. The lock is on local disk because locking on NFS or CIFS shares is unreliable.
- **Locked-down settings:** it sets its own `PATH`, uses `umask 077`, and requires root. The archives contain `/etc/shadow` and private keys, so only root can read them.

**Things to adjust:**
- Change `BACKUP_MOUNT` and `BACKUP_DIR` to match your share. If several hosts write to the same share, add the hostname to `BACKUP_DIR`.
- To run it daily from cron, add this to `/etc/cron.d/backup-etc`: `30 2 * * * root /usr/local/sbin/backup-etc.sh`

**To check it before use:**
1. Run `shellcheck backup-etc.sh && bash -n backup-etc.sh`.
2. Point `BACKUP_MOUNT` at a scratch mount and run it more than seven times. Confirm only seven archives remain and the exit status is 0.
3. Unmount the scratch share and confirm the script exits with 69 and writes nothing.
