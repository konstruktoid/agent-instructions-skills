I can't create files or run commands in this session, so the script is below for you to save. I haven't run it, `shellcheck`, or `bash -n` on it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies.
#
# Usage: backup-etc.sh [BACKUP_DIR]

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs as root, usually from cron or a systemd timer: set the environment here
# rather than inheriting it from the caller.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C # also makes glob order bytewise, which the pruning relies on
umask 077        # the archive contains /etc/shadow

readonly PROGNAME="${0##*/}"
readonly DEFAULT_BACKUP_DIR='/mnt/backup/etc'
readonly LOCK_FILE='/run/lock/backup-etc.lock'
readonly KEEP=7
readonly PREFIX='etc-'
readonly SUFFIX='.tar.gz'

# Script scope: the EXIT trap runs after main has returned.
partial=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

log() {
  printf '%s: %s\n' "${PROGNAME}" "$*"
}

cleanup() {
  if [[ -n ${partial} && -e ${partial} ]]; then
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

# Refuses a destination that is malformed, missing, or not on a mounted share.
# Arguments: backup directory
# Returns: 0 if usable, 2 otherwise
check_backup_dir() {
  local dir="$1"
  local mnt

  if [[ ! ${dir} =~ ^/[A-Za-z0-9._/-]+$ || ${dir} =~ (^|/)\.\.(/|$) ]]; then
    err "invalid backup directory: ${dir}"
    return 2
  fi
  if [[ ! -d ${dir} || -L ${dir} ]]; then
    err "backup directory missing or a symlink: ${dir}"
    return 2
  fi
  # Fail closed if the share is not mounted. Otherwise the archive would
  # silently fill the root filesystem.
  if ! mnt="$(findmnt --noheadings --output TARGET --target "${dir}")"; then
    err "cannot determine mount point of ${dir}"
    return 2
  fi
  if [[ ${mnt} == / ]]; then
    err "backup share not mounted: ${dir} is on the root filesystem"
    return 2
  fi
}

# Deletes all but the newest KEEP archives created by this script.
# Globals: KEEP, PREFIX, SUFFIX
# Arguments: backup directory
prune() {
  local dir="$1"
  local -a archives=()
  local f
  local i

  # Matches only names this script produces; the UTC timestamp sorts in time order.
  for f in "${dir}/${PREFIX}"[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]T[0-9][0-9][0-9][0-9][0-9][0-9]Z"${SUFFIX}"; do
    if [[ -f ${f} && ! -L ${f} ]]; then
      archives+=("${f}")
    fi
  done

  for ((i = 0; i < ${#archives[@]} - KEEP; i++)); do
    log "removing old archive ${archives[i]}"
    rm -f -- "${archives[i]}"
  done
}

main() {
  local backup_dir
  local final

  if (($# > 1)); then
    err "usage: ${PROGNAME} [BACKUP_DIR]"
    return 64
  fi
  backup_dir="${1:-${DEFAULT_BACKUP_DIR}}"

  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  check_backup_dir "${backup_dir}" || return

  # One run at a time. The lock lives locally because flock on NFS/CIFS is unreliable.
  exec 9>"${LOCK_FILE}"
  if ! flock --nonblock 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  # Install the traps before mktemp so no signal can orphan the partial file.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP

  # Write to a hidden partial file on the same filesystem, then rename it
  # atomically. A half-written archive is never counted as a backup.
  partial="$(mktemp --tmpdir="${backup_dir}" ".${PREFIX}partial.XXXXXXXXXX")"
  final="${backup_dir}/${PREFIX}$(date -u +%Y%m%dT%H%M%SZ)${SUFFIX}"

  if [[ -e ${final} ]]; then
    err "archive already exists: ${final}"
    return 1
  fi

  tar --create --gzip --numeric-owner --one-file-system \
    --file "${partial}" --directory / etc
  tar --list --gzip --file "${partial}" >/dev/null
  sync -- "${partial}"

  mv -T -- "${partial}" "${final}"
  partial=''
  log "created ${final}"

  # Prune only after the new archive is in place.
  prune "${backup_dir}"
}

main "$@"
```

**How it works:**
- **Won't write to local disk:** if the backup share isn't mounted, the script exits with an error instead of quietly filling the root filesystem. It also exits if the destination is malformed, missing or a symlink.
- **No half-written backups:** the tarball is written to a hidden partial file, checked by listing its contents, then renamed into place in one step. If anything fails or the script is interrupted, the partial file is deleted and never counted as a backup.
- **Old copies are deleted only after the new one is safe:** a failed run never reduces you below seven good copies. Pruning only touches files whose names match the script's own `etc-YYYYMMDDTHHMMSSZ.tar.gz` pattern, so nothing else on the share can be removed.
- **Archives are readable by root only:** files are created with mode 600, because `/etc` includes `/etc/shadow`.
- **Two runs can't overlap:** a lock file in `/run/lock` makes a second copy exit if one is already running.
- **Signals and exit codes:** if the script is killed (Ctrl-C, `kill`, hangup), it cleans up and then exits with the signal's normal status, so cron or systemd sees that it was killed.
- **Safe under cron:** it sets its own `PATH`, locale and file permissions instead of using whatever the caller passes in.

**Stricter than you might expect:**
- Any `tar` warning counts as a failure, including "file changed as we read it."
- `--one-file-system` skips anything mounted under `/etc`.

**Before you use it:**
1. Set `DEFAULT_BACKUP_DIR` to your share's path, or pass the path as the only argument.
2. Run `shellcheck backup-etc.sh && bash -n backup-etc.sh`.
3. Test it against a scratch mount first. Check the exit code of a normal run, and of a run with the share unmounted, which should exit 2.
4. Schedule it, for example in root's crontab: `15 2 * * * /usr/local/sbin/backup-etc.sh`.

One more thing: the example script in the skill has a few placeholders where arguments should be (`local sig="a"`, `local service="a"`, `local workdir="script"` should be `"$1"`/`"$2"`). I didn't copy them, but you may want to fix them in `SKILL.md`.
