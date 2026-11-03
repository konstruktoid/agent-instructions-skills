I don't have a shell or a file-writing tool in this session, so the script is below for you to save. I haven't run it, and I haven't run `shellcheck` or `bash -n` on it, so check it with the commands at the end before you schedule it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies.
#
# Usage: backup-etc.sh [BACKUP_DIR]
#   BACKUP_DIR defaults to /mnt/backup/etc and must be on a mounted filesystem.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs as root, usually from cron, so don't trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077 # the archive contains /etc/shadow and private keys

readonly PROGNAME="${0##*/}"
readonly DEFAULT_BACKUP_DIR='/mnt/backup/etc'
readonly KEEP=7
readonly PREFIX='etc-'
readonly SUFFIX='.tar.gz'
# Matches only names this script creates, e.g. etc-20261101T020000Z.tar.gz
readonly NAME_RE="^${PREFIX}[0-9]{8}T[0-9]{6}Z\\.tar\\.gz$"

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

on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Fail closed if the share isn't mounted. Otherwise the backups would quietly
# fill the local disk under the empty mount point.
check_target() {
  local dir="$1"
  local mnt

  if [[ ${dir} != /* ]]; then
    err "backup directory must be an absolute path: ${dir}"
    return 64
  fi
  if [[ ! -d ${dir} || -L ${dir} ]]; then
    err "backup directory missing or a symlink: ${dir}"
    return 66
  fi
  if ! mnt="$(findmnt --noheadings --output TARGET --target "${dir}")"; then
    err "cannot determine mount for ${dir}"
    return 69
  fi
  if [[ ${mnt} == / ]]; then
    err "${dir} is on the root filesystem; is the backup share mounted?"
    return 69
  fi
}

create_archive() {
  local dir="$1"
  local final

  final="${dir}/${PREFIX}$(date -u +%Y%m%dT%H%M%SZ)${SUFFIX}"
  if [[ -e ${final} ]]; then
    err "archive already exists: ${final}"
    return 73
  fi

  # Write to a hidden partial file on the same filesystem, then rename it
  # atomically so rotation never counts a half-written archive.
  partial="$(mktemp -- "${dir}/.${PREFIX}XXXXXXXX.partial")"

  tar --create --gzip --file "${partial}" --one-file-system \
    --directory / -- etc

  # Read the whole archive back before trusting it.
  tar --list --gzip --file "${partial}" >/dev/null

  mv -- "${partial}" "${final}"
  partial=''
  printf '%s: wrote %s\n' "${PROGNAME}" "${final}"
}

# Delete all but the newest KEEP archives. Only files matching NAME_RE are
# candidates, and C-locale glob order is chronological for these names.
rotate() {
  local dir="$1"
  local -a archives=()
  local f name i count

  shopt -s nullglob
  for f in "${dir}/${PREFIX}"*"${SUFFIX}"; do
    name="${f##*/}"
    if [[ -f ${f} && ! -L ${f} && ${name} =~ ${NAME_RE} ]]; then
      archives+=("${f}")
    fi
  done
  shopt -u nullglob

  count="${#archives[@]}"
  for ((i = 0; i < count - KEEP; i++)); do
    rm -f -- "${archives[i]}"
    printf '%s: removed %s\n' "${PROGNAME}" "${archives[i]}"
  done
}

main() {
  local dir="${1:-${DEFAULT_BACKUP_DIR}}"

  if (($# > 1)); then
    err "usage: ${PROGNAME} [BACKUP_DIR]"
    return 64
  fi
  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  check_target "${dir}"

  # One run at a time. The lock lives on the share, so two hosts sharing one
  # directory also serialize, if the share supports flock.
  exec 9>"${dir}/.backup-etc.lock"
  if ! flock --nonblock 9; then
    err "another run holds the lock on ${dir}"
    return 75
  fi

  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  create_archive "${dir}"
  rotate "${dir}"
}

main "$@"
```

**Choices you might want to change:**
- **Backup location:** `/mnt/backup/etc` is a placeholder. Change the default or pass the directory as the first argument.
- **Share not mounted:** if the directory is on the root filesystem, the script stops with an error. Otherwise an unmounted share would quietly fill the local disk with backups.
- **Rotation only after a good backup:** old copies are deleted only after the new archive has been written and read back in full. A failed run never leaves you with fewer than seven good copies. Half-written files are hidden and removed on any exit, including Ctrl-C or `kill`.
- **Only its own files are deleted:** rotation touches only files named exactly like `etc-20261101T020000Z.tar.gz`, so nothing else in the directory is removed.
- **Locking:** a lock stops two runs from overlapping.
- **Permissions:** archives are created readable by root only (`umask 077`), because `/etc/shadow` and private keys are inside.
- **If `/etc` changes mid-backup:** GNU tar exits with status 1 when a file changes while it's being read, and the script treats that as a failure. That's deliberate, but if your `/etc` changes often during the backup window, you may want to accept status 1 and log a warning instead.

**To check it before use** (save it as `backup-etc.sh`):
```bash
shellcheck backup-etc.sh && bash -n backup-etc.sh
sudo ./backup-etc.sh /path/to/scratch-mount    # good run; check $? is 0
sudo ./backup-etc.sh /tmp                      # should refuse, non-zero exit (if /tmp is on /)
```
Run the first one eight or more times to confirm that only seven archives remain.

**Example cron entry:** `15 2 * * * root /usr/local/sbin/backup-etc.sh`
