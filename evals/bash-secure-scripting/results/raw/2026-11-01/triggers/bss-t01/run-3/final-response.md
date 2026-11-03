I don't have a file-write or shell tool in this session, so I couldn't save this or run `shellcheck` or `bash -n` on it. Here is the script for you to save as `scripts/etc-backup.sh`. I used `/mnt/backup` as the share because that's the target `scripts/backup.sh` already uses.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs privileged and unattended: do not trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C # also makes glob results sort bytewise, i.e. chronologically
umask 077       # the archive contains /etc/shadow

readonly PROGNAME="${0##*/}"
readonly SHARE='/mnt/backup'
readonly BACKUP_DIR="${SHARE}/etc"
readonly LOCK_FILE='/run/etc-backup.lock' # local: flock on NFS/CIFS is unreliable
readonly KEEP=7
readonly PREFIX='etc-'
readonly SUFFIX='.tar.gz'
# Matches only names this script creates: etc-YYYYMMDDTHHMMSSZ.tar.gz
readonly STAMP_GLOB='[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]T[0-9][0-9][0-9][0-9][0-9][0-9]Z'

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

on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Returns: 0 ready, 77 not root, 69 share not mounted, 75 already running
preflight() {
  if ((EUID != 0)); then
    err "must run as root to read all of /etc"
    return 77
  fi

  # Fail closed: an unmounted share would silently fill the local disk, and
  # the "backups" would be hidden once the share is mounted over them.
  if ! mountpoint -q -- "${SHARE}"; then
    err "${SHARE} is not a mounted filesystem"
    return 69
  fi

  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  mkdir -p -- "${BACKUP_DIR}"
}

# Creates the archive under a temporary name on the share, verifies it, then
# renames it into place so a partial archive never looks like a valid copy.
# Globals: partial (set, then cleared once the archive is in place)
create_archive() {
  local stamp final rc=0

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  final="${BACKUP_DIR}/${PREFIX}${stamp}${SUFFIX}"
  if [[ -e ${final} || -L ${final} ]]; then
    err "refusing to overwrite ${final}"
    return 73
  fi

  # Same directory as the final name, so the mv below is an atomic rename.
  partial="$(mktemp -- "${BACKUP_DIR}/.${PREFIX}${stamp}.XXXXXX")"

  tar --create --gzip --file "${partial}" --directory / -- etc || rc=$?
  # GNU tar exits 1 when a file changed while it was being read; the archive
  # is still usable. Anything higher is a real failure.
  if ((rc == 1)); then
    err "warning: some files changed during archiving"
  elif ((rc != 0)); then
    err "tar failed with status ${rc}"
    return 1
  fi

  if ! tar --list --gzip --file "${partial}" >/dev/null; then
    err "archive failed verification"
    return 1
  fi

  mv -- "${partial}" "${final}"
  partial=''
  log "created ${final}"
}

# Deletes all but the newest KEEP archives. Runs only after a new archive has
# been created and verified, so a failing backup never erodes the old ones.
prune() {
  local -a archives
  local i count

  archives=("${BACKUP_DIR}/${PREFIX}"${STAMP_GLOB}"${SUFFIX}")
  count=${#archives[@]}

  for ((i = 0; i < count - KEEP; i++)); do
    if [[ -f ${archives[i]} && ! -L ${archives[i]} ]]; then
      log "removing ${archives[i]}"
      rm -f -- "${archives[i]}"
    fi
  done
}

main() {
  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi

  # Traps go in before mktemp; cleanup is fine with an empty $partial.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  preflight
  create_archive
  prune
}

main "$@"
```

**How it behaves:**
- **Archive name:** each run writes `/mnt/backup/etc/etc-YYYYMMDDTHHMMSSZ.tar.gz` with permissions `0600`. The names sort in date order, so keeping the last seven just means keeping the last seven names. The cleanup step only matches names in exactly that format, so other files on the share are never touched.
- **Pruning happens only after a good backup:** old copies are deleted only after the new archive has been written, checked and renamed into place. If a backup fails, the previous seven stay.
- **It refuses to run when:**
  - it isn't run as root (exit 77)
  - `/mnt/backup` isn't mounted (exit 69), so it can't fill the local disk
  - another run is still going (exit 75)
- **No half-written archives:** it writes to a hidden temporary file first, and that file is deleted on any failure or on Ctrl-C/kill.
- **Files that change mid-backup:** if a file in /etc changes while it's being archived, tar (exit status 1) still produces a usable archive. The script logs a warning and continues; any worse tar error stops it.

**Before you rely on it:**
1. Run `shellcheck scripts/etc-backup.sh` and `bash -n scripts/etc-backup.sh`.
2. Test it with `SHARE` pointed at a scratch mount. Do one normal run, then one with the share unmounted, and check the exit status each time. Do nine runs and confirm only seven archives remain.
3. Schedule it, for example: `15 2 * * * root /usr/local/sbin/etc-backup.sh` in `/etc/cron.d/etc-backup`.

**Change if needed:** `SHARE` if your backup share is mounted somewhere other than `/mnt/backup`, and `KEEP` if you want more or fewer than seven copies.

**About `scripts/backup.sh`:** I didn't change it, but it has its own problems:
- It uses a predictable temp directory (`/tmp/backup.$$`).
- Its paths aren't quoted.
- It has no strict mode.
- If `tar` or `scp` fails, it still exits as if it succeeded.

I can fix it the same way if you want.
