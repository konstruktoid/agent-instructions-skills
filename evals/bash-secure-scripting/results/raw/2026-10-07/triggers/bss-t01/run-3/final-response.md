I couldn't write the file or run any checks. This session has no Write or Bash tool, and my reads of the skill's reference files were denied. The script below follows the skill's baseline, but I haven't run `shellcheck`, `bash -n` or the script itself. Please run them before you rely on it.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven archives.
#
# Usage: etc-backup.sh [BACKUP_DIR]
#   BACKUP_DIR defaults to /mnt/backup and must be a mounted share.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs as root, often from cron: set the environment instead of inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C               # also makes glob order below byte-wise
umask 077                     # /etc holds shadow files; the archive is root-only

readonly PROGNAME="${0##*/}"
readonly DEFAULT_BACKUP_DIR='/mnt/backup'
readonly KEEP=7
readonly PREFIX='etc-backup-'

# Script scope, not local: the EXIT trap runs after main has returned.
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

# Clean up, then die of the signal so callers see 128+n rather than success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Deletes all but the newest KEEP archives in a directory. Names embed a UTC
# timestamp, so lexical order is chronological.
# Arguments: backup directory
prune() {
  local dir="$1"
  local -a archives
  local i

  shopt -s nullglob
  archives=("${dir}/${PREFIX}"[0-9]*.tar.gz)
  shopt -u nullglob

  for ((i = 0; i < ${#archives[@]} - KEEP; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  local dest="${1:-${DEFAULT_BACKUP_DIR}}"
  local host stamp final lock_fd

  if (($# > 1)); then
    err "usage: ${PROGNAME} [BACKUP_DIR]"
    return 64
  fi
  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi
  if [[ ! -d ${dest} ]]; then
    err "backup directory not found: ${dest}"
    return 66
  fi
  # Fail closed: an unmounted share would silently fill the local disk.
  if ! mountpoint -q -- "${dest}"; then
    err "not a mounted filesystem: ${dest}"
    return 69
  fi

  # Only one run at a time; a second run would race the prune step.
  exec {lock_fd}>"${dest}/.${PROGNAME}.lock"
  if ! flock -n "${lock_fd}"; then
    err "another run is in progress"
    return 75
  fi

  # Traps first, so a signal between mktemp and here cannot leak the file.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  host="$(hostname -s)"
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  final="${dest}/${PREFIX}${stamp}-${host}.tar.gz"

  # Same directory as the destination so the final mv is an atomic rename.
  tmpfile="$(mktemp -- "${dest}/.${PREFIX}XXXXXX.tmp")"

  # Any tar failure (including "file changed as we read it") aborts the run.
  tar --create --gzip --numeric-owner --file "${tmpfile}" -C / -- etc
  # Prove the archive is readable before it can displace an older copy.
  tar --list --gzip --file "${tmpfile}" >/dev/null

  mv -- "${tmpfile}" "${final}"
  tmpfile=''

  # Prune only after the new archive is safely in place.
  prune "${dest}"
  printf '%s: wrote %s\n' "${PROGNAME}" "${final}"
}

main "$@"
```

**Behavior**
- **Archive name:** each run writes `etc-backup-<UTC timestamp>-<host>.tar.gz`. It's written to a temp file on the share, checked with `tar --list`, then renamed into place. A failed or interrupted run never leaves a partial archive that looks valid.
- **Retention:** after a successful backup it deletes everything except the newest seven archives. The timestamp in the name sorts in time order. Pruning happens last, so a failed run never costs you an older copy.
- **Checks that stop the run:**
  - The script must run as root.
  - The target must be a real mountpoint. Without that check, an unmounted share would fill the local disk.
  - Any `tar` error stops the run, including "file changed as we read it".
  - `flock` blocks a second run at the same time.
- **Hardening:** it sets its own `PATH` and `umask 077`. Cleanup runs on every exit path, and `INT`/`TERM` are re-raised so the caller sees the right exit status.

**Assumptions to confirm**
- I assumed the share is mounted at `/mnt/backup`. Pass a different path as the first argument, or edit `DEFAULT_BACKUP_DIR`.
- I assumed seven copies means seven archives, not seven days. If you run it more than once a day, you'd keep less than seven days.
- NFS root-squash or SMB mounts may refuse `umask 077` permissions or ownership. If so, run the share-side checks first.

**Next steps**
1. Save it as `etc-backup.sh`.
2. Run `shellcheck etc-backup.sh` and `bash -n etc-backup.sh`.
3. Do a test run against a scratch mount.

I can adjust the script after you've done that, or if you tell me the real share path and schedule.
