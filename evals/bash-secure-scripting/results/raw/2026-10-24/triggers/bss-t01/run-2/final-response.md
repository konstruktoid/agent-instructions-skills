I couldn't save or run anything here because this session only has read and search tools. The script is below for you to save, and none of the shellcheck, `bash -n` or test-run checks have been done yet.

I also checked the repo. The only other script, `scripts/backup.sh`, has problems this one avoids: unquoted paths, a `/tmp/backup.$$` directory that's easy to predict, no error handling, and no cleanup if it fails partway. I left it alone.

**`scripts/backup-etc.sh`**

```bash
#!/usr/bin/env bash
#
# Archive /etc into a tarball on the backup share and keep the newest seven.

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs as root, usually from cron: do not trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077 # /etc holds shadow, keys and credentials

readonly PROGNAME="${0##*/}"
readonly SHARE='/mnt/backup'
readonly BACKUP_DIR="${SHARE}/etc"
readonly LOCK_FILE='/run/lock/backup-etc.lock'
readonly KEEP=7

# Script scope: the EXIT trap runs after main has returned.
tmp_archive=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${tmp_archive} && -f ${tmp_archive} ]]; then
    rm -f -- "${tmp_archive}"
  fi
  return 0
}

on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Deletes all but the newest KEEP archives. Names embed a UTC timestamp, so
# the C-locale glob order is chronological.
prune_old() {
  local -a archives=("${BACKUP_DIR}"/etc-[0-9]*T[0-9]*Z.tar.gz)
  local count="${#archives[@]}"
  local i

  for ((i = 0; i < count - KEEP; i++)); do
    if [[ -f ${archives[i]} && ! -L ${archives[i]} ]]; then
      rm -f -- "${archives[i]}"
    fi
  done
}

main() {
  local stamp archive

  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  # Fail closed: if the share is not mounted, we would fill the local disk.
  if ! mountpoint -q -- "${SHARE}"; then
    err "${SHARE} is not a mounted filesystem"
    return 69
  fi

  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another backup is already running"
    return 75
  fi

  mkdir -p -- "${BACKUP_DIR}"
  chmod 700 -- "${BACKUP_DIR}"

  # Traps before mktemp, so no window leaves a partial archive behind.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  # Temp file on the share itself, so the final mv is an atomic rename.
  tmp_archive="$(mktemp -- "${BACKUP_DIR}/.etc-partial.XXXXXX")"

  # Any non-zero tar status, including "file changed as we read it", fails the run.
  tar --create --gzip --numeric-owner --one-file-system \
    --file "${tmp_archive}" --directory / -- etc

  if ! tar --list --gzip --file "${tmp_archive}" >/dev/null; then
    err "archive verification failed"
    return 1
  fi

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${BACKUP_DIR}/etc-${stamp}.tar.gz"
  mv -- "${tmp_archive}" "${archive}"
  tmp_archive=''

  # Prune only after a new, verified archive is in place.
  prune_old
  printf '%s: wrote %s\n' "${PROGNAME}" "${archive}"
}

main "$@"
```

**How it works:**
- **Share must be mounted:** it uses `mountpoint -q` to check. Without this, a share that failed to mount would let the backup quietly fill the local disk.
- **Nothing half-written:** the archive is written to a temporary file on the share, checked with `tar --list`, then renamed into place. A run that's interrupted or fails leaves nothing behind, because the cleanup is set up before the temporary file is created.
- **Keeping seven:** old copies are deleted only after the new archive is safely in place, so a failed run never reduces you below seven good copies. Deletion only touches regular files matching `etc-<UTC timestamp>Z.tar.gz`, never symlinks or anything else in the directory.
- **Fixed environment:** the script sets its own `PATH`, uses the C locale and a strict `umask 077`, and requires root. The lock (`flock` on `/run/lock`) is kept off the share, since locks over network shares can be unreliable.
- **Exit codes:** 77 means not root, 69 means the share isn't mounted, 75 means another run is in progress, and anything from tar is reported as a failure.

**To install and check it:**
```bash
install -m 0750 -o root -g root backup-etc.sh /usr/local/sbin/backup-etc
shellcheck scripts/backup-etc.sh && bash -n scripts/backup-etc.sh
```
Before relying on it, try one run with the share unmounted (it should exit 69), and confirm that an eighth run removes the oldest archive.

**Decisions for you:**
- **Share location:** I assumed it's mounted at `/mnt/backup`, since that's where the existing script points. Change `SHARE` if yours is elsewhere, or if it can only be reached over `scp` like the existing script uses.
- **Strict tar failures:** tar exits with status 1 if a file in `/etc` changes while it's being read. That counts as a failure here. If that happens too often on a busy host, you could accept status 1 explicitly instead.
- **Archives aren't encrypted:** they include `/etc/shadow` and private keys, so access to the share needs to be tightly restricted.
