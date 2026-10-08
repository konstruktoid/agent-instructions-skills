I couldn't save the file or run anything, because this session only gives me read and search tools. The script below is **untested**: I haven't run `shellcheck`, `bash -n`, or a trial run on it.

I based it on `scripts/backup.sh`, which uses `/mnt/backup` as the backup location. Save it as something like `scripts/backup-etc.sh` and make it executable (`chmod 0750`).

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest KEEP archives. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs privileged and unattended: do not trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C # glob order is byte order, so timestamped names sort by age
umask 077       # /etc holds shadow and private keys; archives are root-only

readonly PROGNAME="${0##*/}"
readonly SHARE_MOUNT='/mnt/backup'
readonly BACKUP_DIR="${SHARE_MOUNT}/etc"
readonly KEEP=7
readonly LOCK_FILE='/run/lock/backup-etc.lock'
readonly NAME_RE='^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$'

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

# Clean up, then die of the signal so the caller sees 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Writes /etc to the given file. GNU tar exits 1 when a file changed while it
# was being read; that archive is still usable, so warn instead of failing.
# Arguments: output file
# Returns: 0 on success or warning, 1 on a fatal tar error
create_archive() {
  local out="$1"
  local rc=0

  tar --create --gzip --numeric-owner --file "${out}" \
    --directory / -- etc || rc=$?

  if ((rc == 1)); then
    err "warning: some files changed while being archived"
  elif ((rc != 0)); then
    err "tar failed with status ${rc}"
    return 1
  fi
  return 0
}

# Deletes all but the newest KEEP archives. Only regular files whose names
# match NAME_RE are considered, so nothing else on the share is touched.
# Globals: BACKUP_DIR, KEEP, NAME_RE
prune_old() {
  local -a archives=()
  local f excess i

  for f in "${BACKUP_DIR}"/etc-*.tar.gz; do
    [[ -f ${f} && ! -L ${f} ]] || continue
    [[ ${f##*/} =~ ${NAME_RE} ]] || continue
    archives+=("${f}")
  done

  excess=$((${#archives[@]} - KEEP))
  for ((i = 0; i < excess; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  local archive

  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi
  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  # Fail closed: if the share is not mounted, writing to the mount point
  # would silently fill the local disk instead.
  if ! mountpoint -q -- "${SHARE_MOUNT}"; then
    err "${SHARE_MOUNT} is not mounted"
    return 69
  fi
  mkdir -p -- "${BACKUP_DIR}"

  # Refuse to run concurrently with a previous, still-running backup.
  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another backup is already running"
    return 75
  fi

  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  # Temp file in the destination directory so the final mv is an atomic
  # rename; its dot-prefixed name never matches the rotation glob.
  tmpfile="$(mktemp -- "${BACKUP_DIR}/.etc.XXXXXXXX")"
  archive="${BACKUP_DIR}/etc-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"

  create_archive "${tmpfile}"
  if ! gzip -t -- "${tmpfile}"; then
    err "archive failed integrity check"
    return 1
  fi
  mv -f -- "${tmpfile}" "${archive}"
  tmpfile=''

  # Prune only after a new archive has landed, so a failing run never
  # shrinks the set of good copies.
  prune_old
  printf '%s: wrote %s\n' "${PROGNAME}" "${archive}"
}

main "$@"
```

**How it works:**
- **If the share isn't mounted, the script stops.** It checks with `mountpoint` first. Otherwise, writing to `/mnt/backup` would silently fill the local disk.
- **A failed or interrupted run leaves nothing behind.** The archive is written to a temporary file on the share and only renamed into place after `gzip -t` confirms it's intact.
- **Old copies are deleted only after a new one lands.** Deletion only touches regular files named like `etc-20261008T020000Z.tar.gz`, so a run of failures never shrinks your set of good backups.
- **Only one copy can run at a time.** A lock (`flock`) on `/run/lock/backup-etc.lock` makes an overlapping run exit with status 75.
- **The archives are readable by root only.** They have mode `0600` because `/etc` contains `shadow` and private keys.
- **Files changing during the backup only cause a warning.** That's GNU tar's exit status 1. Any other tar error fails the run.

**Things to check before using it:**
- **NFS with `root_squash`:** if the share is mounted this way, root can't write to it. You'd need to write to a directory the squashed user owns, or change the export settings.
- **Scheduling:** for example, a root crontab line `15 2 * * * /usr/local/sbin/backup-etc.sh`. If it runs more than once a day, "seven copies" means seven runs, not seven days.
- **Before relying on it,** save it and run `shellcheck backup-etc.sh` and `bash -n backup-etc.sh`. Then do one real run, and one run with the share unmounted to confirm it exits non-zero.

**About the existing `scripts/backup.sh`:** I didn't change it, but it has real problems:
- Its temporary directory under `/tmp` has a predictable name, which another user could plant a symlink at.
- None of its variables are quoted.
- It has no error handling or cleanup trap, so a failed `tar` still runs `scp`.

I can harden it the same way if you'd like.
