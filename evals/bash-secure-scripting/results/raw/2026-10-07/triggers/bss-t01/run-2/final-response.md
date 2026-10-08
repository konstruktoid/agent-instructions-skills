I couldn't save the script or test it. The Write tool is disabled in this session, and I wasn't allowed to read the skill's reference files. So `shellcheck`, `bash -n` and a test run haven't been done. The script is below, and it follows the skill's baseline from memory of the skill text rather than the full references.

Save it as `scripts/archive-etc.sh`. Run `shellcheck -x`, `bash -n` and `shfmt -d` on it before you trust it. Then do a trial run against a scratch directory, as root, and check the exit status.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven archives.
#
# Usage: archive-etc.sh [BACKUP_DIR]    (default: /mnt/backup)

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs as root, often from cron: do not trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
# The archive holds /etc/shadow and keys: owner-only from creation.
umask 077

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR="/etc"
readonly KEEP=7
readonly ARCHIVE_PREFIX="etc-"
readonly ARCHIVE_SUFFIX=".tar.gz"

# Script scope, not local to main: the EXIT trap runs after main has returned.
stage=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${stage} && -e ${stage} ]]; then
    rm -f -- "${stage}"
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

# Deletes all but the newest KEEP archives. Names embed a UTC timestamp, so
# lexical order is chronological. Only exact-pattern names are considered.
prune() {
  local dir="$1"
  local -a archives=()
  local f i

  for f in "${dir}/${ARCHIVE_PREFIX}"[0-9]*"${ARCHIVE_SUFFIX}"; do
    [[ -f ${f} && ! -L ${f} ]] || continue
    [[ ${f##*/} =~ ^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$ ]] || continue
    archives+=("${f}")
  done

  ((${#archives[@]} > KEEP)) || return 0

  for ((i = 0; i < ${#archives[@]} - KEEP; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  local backup_dir="${1:-/mnt/backup}"
  local stamp final lock_fd

  if (($# > 1)); then
    err "usage: ${PROGNAME} [BACKUP_DIR]"
    return 64
  fi
  if ((EUID != 0)); then
    err "must run as root to read all of ${SOURCE_DIR}"
    return 77
  fi
  if [[ ${backup_dir} != /* ]]; then
    err "backup directory must be an absolute path: ${backup_dir}"
    return 64
  fi
  # Fail closed: an unmounted share would leave us writing to the local disk.
  if [[ ! -d ${backup_dir} || -L ${backup_dir} ]]; then
    err "backup directory missing or a symlink: ${backup_dir}"
    return 66
  fi
  if ! mountpoint -q -- "${backup_dir}"; then
    err "backup share is not mounted: ${backup_dir}"
    return 69
  fi

  # One run at a time; the lock is released when the shell exits.
  exec {lock_fd}>"${backup_dir}/.${PROGNAME}.lock"
  if ! flock --nonblock "${lock_fd}"; then
    err "another run holds the lock"
    return 75
  fi

  # Traps before mktemp so a signal cannot orphan the staging file. Staging in
  # the destination directory keeps the final mv an atomic same-filesystem rename.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  stage="$(mktemp -- "${backup_dir}/.${ARCHIVE_PREFIX}stage.XXXXXX")"

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  final="${backup_dir}/${ARCHIVE_PREFIX}${stamp}${ARCHIVE_SUFFIX}"
  if [[ -e ${final} ]]; then
    err "archive already exists: ${final}"
    return 73
  fi

  tar --create --gzip --file "${stage}" --one-file-system \
    --directory / -- "${SOURCE_DIR#/}"

  # Do not rotate out good copies on the strength of a bad new one.
  tar --list --gzip --file "${stage}" >/dev/null

  mv -T -- "${stage}" "${final}"
  stage=''

  prune "${backup_dir}"
  printf '%s: wrote %s\n' "${PROGNAME}" "${final}"
}

main "$@"
```

**How it behaves**
- **Archive names:** each archive is `etc-YYYYmmddTHHMMSSZ.tar.gz`. A UTC timestamp to the second means two runs on the same day don't overwrite each other, and sorting by name gives chronological order.
- **Retention:** the script prunes only after the new archive has been written and read back successfully. It deletes only regular files whose names match the exact pattern. Anything else on the share is left alone.
- **Share check:** it refuses to run unless the backup directory is an actual mount point. Otherwise a share that failed to mount would fill the local disk silently.
- **Partial files:** it stages the archive in the destination directory and renames it into place. A crash or signal never leaves a partial `etc-*.tar.gz`. The trap removes the staging file.
- **Concurrency:** an `flock` on a lock file in the backup directory stops two runs from overlapping.
- **Permissions:** the archive is owner-only (`umask 077`), because `/etc` contains `shadow` and private keys.

**Assumptions to check**
- **Mount point:** the share is mounted at `/mnt/backup`. That's the path in your existing `scripts/backup.sh`, and you can pass a different one as the first argument.
- **Root:** it must run as root, and it exits with 77 otherwise.
- **Strict failures:** `tar` exiting non-zero for any reason, including a file changing mid-read, fails the run. Rerun it if that happens.
- **Mounts under `/etc`:** `--one-file-system` skips anything separately mounted under `/etc`. Remove the flag if you have such a mount.

I left `scripts/backup.sh` unchanged. It has unquoted variables, no strict mode and a predictable `/tmp` path. I can harden it too if you want.
