I couldn't save this file. This session only has read and search tools, so I can't write it or run anything. I haven't run `shellcheck`, `bash -n` or a test on it. Here's the script to save as `scripts/backup-etc.sh`:

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest seven. Intended to run as root from cron or a systemd timer.

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs privileged and unattended: don't inherit the caller's environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077 # the archive contains /etc/shadow and private keys

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR='etc'           # relative to / so the archive has no leading slash
readonly BACKUP_DIR='/mnt/backup/etc'
readonly SHARE_MOUNT='/mnt/backup'
readonly KEEP=7
readonly PREFIX='etc-'
readonly SUFFIX='.tar.gz'
readonly LOCK_FILE='/run/lock/backup-etc.lock'

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

# Deletes all but the newest KEEP archives. The names embed a UTC timestamp,
# so glob order (sorted lexically under LC_ALL=C) is age order.
prune() {
  local -a archives=("${BACKUP_DIR}/${PREFIX}"[0-9]*"${SUFFIX}")
  local count=${#archives[@]}
  local i

  for ((i = 0; i < count - KEEP; i++)); do
    rm -f -- "${archives[i]}"
  done
}

main() {
  if (($# != 0)); then
    err "usage: ${PROGNAME}"
    return 64
  fi

  # Fail closed: if the share isn't mounted, don't fill the local disk underneath it.
  if ! mountpoint -q -- "${SHARE_MOUNT}"; then
    err "backup share not mounted at ${SHARE_MOUNT}"
    return 69
  fi
  mkdir -p -- "${BACKUP_DIR}"

  # One run at a time: a cron overlap must not prune mid-write.
  exec 9>"${LOCK_FILE}"
  if ! flock -n 9; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  local stamp archive
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${BACKUP_DIR}/${PREFIX}${stamp}${SUFFIX}"

  # Traps before mktemp, so no signal window leaves a partial file behind.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM

  # Write into the destination directory, then rename: same filesystem, so the
  # mv is atomic and a half-written tarball never carries the final name.
  partial="$(mktemp -- "${BACKUP_DIR}/.${PREFIX}${stamp}.XXXXXX")"

  # Any non-zero tar status (including 1, "file changed as we read it") is a
  # failure: an unverified archive must not rotate a good one out.
  if ! tar --create --gzip --numeric-owner --file "${partial}" -C / -- "${SOURCE_DIR}"; then
    err "tar failed; keeping existing archives"
    return 1
  fi
  if ! gzip --test -- "${partial}"; then
    err "archive failed integrity check"
    return 1
  fi

  mv -- "${partial}" "${archive}"
  partial=''

  # Prune only after the new archive is in place.
  prune
  printf '%s: wrote %s\n' "${PROGNAME}" "${archive}"
}

main "$@"
```

Before running it:

- **Share path:** I guessed `/mnt/backup`, the `TARGET` in your existing `scripts/backup.sh`, and write to `/mnt/backup/etc` under it. The script checks that the share is actually mounted. If it isn't, the script stops so it doesn't fill up the local disk under the mount point. Change `SHARE_MOUNT` and `BACKUP_DIR` if your share lives somewhere else.
- **Old copies are deleted only after a new one succeeds.** A tar failure (including the "file changed as we read it" warning), a failed gzip check or a signal leaves the existing seven untouched and removes the partial file.
- **It doesn't copy files over ssh.** `scripts/backup.sh` sends its archive with `scp`. If your "backup share" is actually that remote host rather than a mount, tell me and I'll change this to copy over ssh.
- **Permissions:** archives are created readable by root only (`umask 077`), because they contain `/etc/shadow` and private keys.
- **Running twice at once:** a lock (`flock`) stops a second run, such as overlapping cron jobs, from deleting old copies while another is still writing.
- **Unrelated finding in `scripts/backup.sh`:** the paths in it aren't quoted, and it uses a predictable temp directory in `/tmp`, which another local user could plant a symlink at. If anything fails it also exits as if it succeeded, because it has no `set -e` and no checks. I can harden it too if you want.

To check it once saved: `shellcheck scripts/backup-etc.sh && bash -n scripts/backup-etc.sh`. Then do a test run with `SHARE_MOUNT`/`BACKUP_DIR` pointed at a scratch directory that is mounted (a tmpfs works). Run it eight times and confirm only seven archives are left. Also run it once with the share unmounted and confirm it exits with 69.
