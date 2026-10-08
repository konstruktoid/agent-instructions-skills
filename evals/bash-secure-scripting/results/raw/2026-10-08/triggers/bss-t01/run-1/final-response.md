I couldn't save or run anything this session. The only tools I had were for reading and searching, and none could write a file or run a command. So below is the script itself. It hasn't been run, and `shellcheck` and `bash -n` haven't been run on it either.

It follows `scripts/backup.sh`, the only shell script in the repo, which treats `/mnt/backup` as the backup share. Unlike that script, it writes to a mounted share rather than using `scp`.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven archives. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs privileged and unattended: don't inherit the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077 # the archive contains /etc/shadow and private keys

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR='/etc'
readonly SHARE_MOUNT='/mnt/backup'
readonly BACKUP_DIR="${SHARE_MOUNT}/etc"
readonly KEEP=7
readonly LOCK_FILE='/run/lock/etc-backup.lock'

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

# Clean up, then die of the signal so the caller sees 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

# Creates the archive under a temporary name, verifies it, then renames it
# into place so a half-written file never looks like a valid backup.
# Globals: SOURCE_DIR, BACKUP_DIR, partial
# Returns: 0 on success, 1 on failure
create_archive() {
  local stamp final rc
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  final="${BACKUP_DIR}/etc-${stamp}.tar.gz"

  if [[ -e ${final} ]]; then
    err "archive already exists: ${final}"
    return 1
  fi

  # Temp file on the same filesystem as the target, so the mv is atomic.
  partial="$(mktemp -- "${BACKUP_DIR}/.etc-${stamp}.XXXXXX.partial")"

  # GNU tar exits 1 when a file changed while being read, which is normal on a
  # live /etc; accept that as a warning, fail on anything else.
  rc=0
  tar --create --gzip --file "${partial}" \
    --one-file-system --numeric-owner --acls --xattrs \
    --directory / -- "${SOURCE_DIR#/}" || rc=$?
  if ((rc == 1)); then
    err "warning: some files changed while being archived"
  elif ((rc != 0)); then
    err "tar failed with status ${rc}"
    return 1
  fi

  if ! gzip --test -- "${partial}"; then
    err "archive failed integrity check: ${partial}"
    return 1
  fi

  chmod 0600 -- "${partial}"
  mv -- "${partial}" "${final}"
  partial=''
  printf '%s: wrote %s\n' "${PROGNAME}" "${final}"
}

# Deletes all but the newest KEEP archives. Names carry a UTC timestamp, so
# lexical order under LC_ALL=C is chronological order.
# Globals: BACKUP_DIR, KEEP
prune_archives() {
  local -a archives=()
  local f i count

  shopt -s nullglob
  for f in "${BACKUP_DIR}"/etc-*.tar.gz; do
    # Only touch regular files matching our exact naming scheme.
    if [[ -f ${f} && ! -L ${f} && ${f##*/} =~ ^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$ ]]; then
      archives+=("${f}")
    fi
  done
  shopt -u nullglob

  count=${#archives[@]}
  for ((i = 0; i < count - KEEP; i++)); do
    rm -f -- "${archives[i]}"
    printf '%s: pruned %s\n' "${PROGNAME}" "${archives[i]}"
  done
}

main() {
  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi

  if ((EUID != 0)); then
    err "must run as root to read all of ${SOURCE_DIR}"
    return 77
  fi

  # Fail closed: if the share isn't mounted, writing to the mountpoint would
  # silently fill the local disk instead.
  if ! mountpoint -q -- "${SHARE_MOUNT}"; then
    err "backup share is not mounted at ${SHARE_MOUNT}"
    return 69
  fi

  mkdir -p -- "${BACKUP_DIR}"
  chmod 0700 -- "${BACKUP_DIR}"

  # One run at a time; a second run exits rather than racing on pruning.
  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  # Traps go in before mktemp; cleanup tolerates an empty $partial.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  create_archive
  # Old copies are pruned only after a new archive has been verified.
  prune_archives
}

main "$@"
```

**What it does:**
- **Share not mounted:** if `/mnt/backup` isn't mounted, the script exits with an error. Otherwise it would write onto the local disk underneath the mount point.
- **Half-written archives:** it writes to a hidden `.partial` file in the target directory and checks it with `gzip --test`. Only then does it rename it to `etc-YYYYmmddTHHMMSSZ.tar.gz`. If the script fails or is interrupted (Ctrl-C or a stop signal), the partial file is deleted.
- **Keeping seven:** it deletes old copies only after a new one has been written and checked, so a failed run never reduces you below seven. It only deletes regular files whose names match the exact pattern. The names use UTC timestamps, so sorting by name puts them in date order.
- **Permissions:** archives are mode `0600` in a `0700` directory, because `/etc` contains password hashes (`/etc/shadow`) and private keys.
- **Overlapping runs:** a lock (`flock`) stops two runs at once, and the second exits with status 75. The script sets its own `PATH` and locale, since it runs as root.

**Decisions to check:**
- **Changed files:** GNU `tar` exits with status 1 when a file changes while it's being read, which is normal on a live `/etc`. The script treats that as a warning and keeps the archive. If you'd rather it fail, remove that branch.
- **Network share:** if the share is NFS with root squashing, root may not be able to create or `chmod` files there. Test this on the real share before scheduling it.
- **Locations:** `BACKUP_DIR` (`/mnt/backup/etc`) and `KEEP` are set at the top of the script, not read from the environment. That's deliberate for a script running as root, so edit them there.

**To check it once you've saved it, for example as `scripts/backup-etc.sh`:**
```
shellcheck scripts/backup-etc.sh && bash -n scripts/backup-etc.sh
```
Then do a test run with `SHARE_MOUNT` and `SOURCE_DIR` pointed at scratch directories, and check it exits with 0. Also run the failure cases: share not mounted, not root, and Ctrl-C partway through. Confirm each exits non-zero and leaves no `.partial` file behind.
