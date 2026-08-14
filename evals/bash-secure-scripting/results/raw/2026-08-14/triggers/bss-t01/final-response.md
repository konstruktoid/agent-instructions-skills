I don't have file-write or shell-execution tools available in this session, so I can't create the file or run `shellcheck`/`bash -n` myself. Here's a hardened script — save it as `scripts/backup-etc.sh`, `chmod 750`, and run the verify steps noted at the bottom before relying on it.

```bash
#!/usr/bin/env bash
#
# Archive /etc to the backup share and retain the last seven copies.
# Must run as root (or a user with read access to all of /etc).

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: the environment is the caller's, so set what matters.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR=/etc
readonly BACKUP_SHARE=/mnt/backup
readonly RETAIN=7
readonly LOCK_FILE=/var/lock/backup-etc.lock

# Script scope, not local to main: traps run after main has returned.
lock_fd=''
tmp_archive=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${tmp_archive} && -e ${tmp_archive} ]]; then
    rm -f -- "${tmp_archive}"
  fi
  return 0
}

# Removes archives beyond the newest RETAIN copies.
# Globals: BACKUP_SHARE, RETAIN
rotate_archives() {
  local -a archives
  local archive

  mapfile -d '' -t archives < <(
    find "${BACKUP_SHARE}" -maxdepth 1 -type f -name 'etc-*.tar.gz' -print0 | sort -z
  )

  if ((${#archives[@]} <= RETAIN)); then
    return 0
  fi

  for archive in "${archives[@]:0:${#archives[@]} - RETAIN}"; do
    rm -f -- "${archive}"
  done
}

main() {
  if [[ ! -d ${BACKUP_SHARE} ]]; then
    err "backup share not available: ${BACKUP_SHARE}"
    return 1
  fi

  if ! mountpoint -q -- "${BACKUP_SHARE}"; then
    err "backup share is not mounted: ${BACKUP_SHARE}"
    return 1
  fi

  exec {lock_fd}>"${LOCK_FILE}"
  if ! flock -n "${lock_fd}"; then
    err "another run is already in progress"
    return 1
  fi

  # Written directly on the share so the final rename is atomic (same filesystem).
  tmp_archive="$(mktemp "${BACKUP_SHARE}/.etc-XXXXXX.tar.gz.tmp")"
  trap cleanup EXIT

  tar --create --gzip --file "${tmp_archive}" -- "${SOURCE_DIR}"

  local final_archive="${BACKUP_SHARE}/etc-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
  mv -- "${tmp_archive}" "${final_archive}"
  tmp_archive=''

  rotate_archives
}

main "$@"
```

Key points:
- **Locking** (`flock` on `/var/lock/backup-etc.lock`) stops overlapping cron runs from corrupting the rotation.
- **Atomic write**: the tarball is built with `mktemp` directly on `BACKUP_SHARE`, then `mv`'d into its final name on the same filesystem — no partial/corrupt archive is ever visible under the final name.
- **Fail closed**: if the share isn't mounted, or `tar` hits a permission error reading `/etc`, `errexit`/explicit checks abort rather than silently producing a partial backup.
- **Rotation** is filename-pattern-scoped (`etc-*.tar.gz`, ISO-8601 timestamps sort chronologically) and only deletes the oldest beyond the newest 7 — the in-progress temp file uses a different pattern so it's never touched by rotation.
- **Cleanup trap** removes a stray temp archive if `tar` or `mv` fails partway.

Before trusting it: run `shellcheck` and `bash -n` on the file, and do a dry run against a scratch directory instead of `/etc`/`/mnt/backup` to confirm rotation behavior with >7 archives present.
