I couldn't save or run anything in this session because I only have read-only tools here: no file-write and no shell. So below is the script for you to save as `scripts/backup-etc.sh`. I **haven't run** `shellcheck`, `bash -n` or a test on it, so do that before you schedule it (commands at the end).

I took the share's location from your existing `scripts/backup.sh`, which uses `/mnt/backup`. The archives go into `/mnt/backup/etc/`.

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven copies. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit

# Privileged and scheduled: do not trust the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR='/etc'
readonly SHARE='/mnt/backup'
readonly BACKUP_DIR="${SHARE}/etc"
readonly KEEP=7
readonly NAME_RE='^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$'

# Script scope: the EXIT trap runs after main has returned.
partial=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
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

# Removes all but the newest KEEP archives. Names embed a UTC timestamp,
# so lexical order is chronological.
# Globals: BACKUP_DIR KEEP NAME_RE
prune_old() {
  local -a archives=()
  local path name i

  shopt -s nullglob
  for path in "${BACKUP_DIR}"/etc-*.tar.gz; do
    name="${path##*/}"
    # Only touch files this script created; skip anything else that matches the glob.
    if [[ ${name} =~ ${NAME_RE} && -f ${path} && ! -L ${path} ]]; then
      archives+=("${path}")
    fi
  done
  shopt -u nullglob

  for ((i = 0; i < ${#archives[@]} - KEEP; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  local stamp archive

  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi
  if ((EUID != 0)); then
    err 'must run as root to read all of /etc'
    return 77
  fi

  # Fail closed: if the share is not mounted, writing would silently fill
  # the local disk under the mount point instead.
  if ! mountpoint -q -- "${SHARE}"; then
    err "backup share not mounted: ${SHARE}"
    return 69
  fi

  # One run at a time; a second instance exits rather than racing the prune.
  exec 9>"${SHARE}/.backup-etc.lock"
  if ! flock -n 9; then
    err 'another run is in progress'
    return 75
  fi

  mkdir -p -- "${BACKUP_DIR}"

  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${BACKUP_DIR}/etc-${stamp}.tar.gz"

  # Write to a temp file on the same filesystem, then rename atomically, so
  # a partial archive never counts as one of the seven copies.
  partial="$(mktemp -- "${BACKUP_DIR}/.etc-${stamp}.XXXXXX")"

  if ! tar --create --gzip --file "${partial}" \
    --directory / --one-file-system -- "${SOURCE_DIR#/}"; then
    err "tar failed; keeping existing archives untouched"
    return 1
  fi

  mv -- "${partial}" "${archive}"
  partial=''

  prune_old
  printf '%s: wrote %s\n' "${PROGNAME}" "${archive}"
}

main "$@"
```

**How it works:**
- **Share not mounted:** if `/mnt/backup` isn't mounted, the script stops with an error. Otherwise it would quietly write to the local disk under the empty mount point.
- **No half-written backups:** each tarball is written to a temporary file first and renamed only once it's complete. If the script is interrupted, the temporary file is deleted. Old copies are pruned only after a new archive is complete, so a failed run never reduces you below seven good backups.
- **Pruning only touches its own files:** it deletes files named exactly like `etc-20261024T020000Z.tar.gz`, skipping symlinks and anything else in the directory. The UTC timestamp in the name means alphabetical order is date order.
- **One run at a time:** a lock (`flock`) makes a second copy exit instead of racing the first.
- **Fixed environment:** the script sets its own `PATH`, locale and `umask 077`. That last setting makes the archives readable only by root, which matters because `/etc` contains `shadow` and private keys.
- **Exit codes:** each failure has its own exit status (64, 77, 69, 75, 1), so cron or systemd can tell what went wrong.

**One thing to decide:** GNU `tar` exits with status 1 if a file changes while it's being read. The script treats that as a failure and keeps the previous archives. That's the safer default; tell me if you'd rather accept it with a warning.

**Before you schedule it**, run these:
```bash
shellcheck scripts/backup-etc.sh && bash -n scripts/backup-etc.sh
sudo scripts/backup-etc.sh; echo "exit=$?"    # with the share mounted
```
To test a failure, run it once with the share unmounted. It should exit 69 and write nothing. To test pruning, run it eight times and check that seven archives remain.

**Separately, your existing `scripts/backup.sh` has problems:** it has no strict mode, uses unquoted paths, and creates a temp directory at the predictable path `/tmp/backup.$$`, which another local user could hijack. It also has no cleanup if `tar` or `scp` fails. I can harden it the same way if you'd like.
