I don't have a file-write or shell tool in this session, so I couldn't save the script or run `shellcheck`, `bash -n` or a test run on it. Here it is to save as e.g. `/usr/local/sbin/backup-etc`:

```bash
#!/usr/bin/env bash
#
# Archive /etc into a timestamped tarball on the backup share and keep the
# newest KEEP copies (default 7).
#
# Usage: backup-etc [-k KEEP] [-s SHARE]
#   -s SHARE  mount point of the backup share (default /mnt/backup)
#   -k KEEP   number of archives to retain, 1-999 (default 7)

set -Eeuo pipefail
shopt -s inherit_errexit nullglob

# Runs as root, usually from cron: set the environment rather than inherit it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077 # /etc holds shadow and private keys; archives are root-only

readonly PROGNAME="${0##*/}"
readonly SOURCE_DIR='/etc'
readonly LOCK_FILE='/run/lock/backup-etc.lock'

# Script scope, not local to main: the EXIT trap runs after main has returned.
tmp_archive=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

log() {
  printf '%s: %s\n' "${PROGNAME}" "$*"
}

usage() {
  printf 'usage: %s [-k KEEP] [-s SHARE]\n' "${PROGNAME}" >&2
}

cleanup() {
  if [[ -n ${tmp_archive} && -f ${tmp_archive} ]]; then
    rm -f -- "${tmp_archive}"
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

# Deletes all but the newest KEEP archives in a directory.
# Arguments: destination directory, number to keep
prune() {
  local dest="$1"
  local keep="$2"
  local -a archives=()
  local f name i

  # Glob output is sorted under LC_ALL=C, and the UTC timestamp in the name
  # makes that order chronological. Only files with this exact name pattern
  # are ever deleted; symlinks and anything else are left alone.
  for f in "${dest}"/etc-*.tar.gz; do
    name="${f##*/}"
    if [[ ${name} =~ ^etc-[0-9]{8}T[0-9]{6}Z\.tar\.gz$ && -f ${f} && ! -L ${f} ]]; then
      archives+=("${f}")
    fi
  done

  for ((i = 0; i < ${#archives[@]} - keep; i++)); do
    rm -f -- "${archives[i]}"
    log "removed old archive ${archives[i]}"
  done
}

main() {
  local share='/mnt/backup'
  local keep=7
  local opt host dest stamp archive lock_fd
  local status=0

  while getopts ':k:s:h' opt; do
    case ${opt} in
      k) keep="${OPTARG}" ;;
      s) share="${OPTARG}" ;;
      h)
        usage
        return 0
        ;;
      *)
        usage
        return 64
        ;;
    esac
  done
  shift $((OPTIND - 1))
  if (($# != 0)); then
    usage
    return 64
  fi

  if [[ ! ${keep} =~ ^[1-9][0-9]{0,2}$ ]]; then
    err "KEEP must be an integer from 1 to 999: ${keep}"
    return 64
  fi
  if [[ ! ${share} =~ ^/[A-Za-z0-9._/-]+$ || ${share} == *..* ]]; then
    err "SHARE must be an absolute path without '..': ${share}"
    return 64
  fi
  if ((EUID != 0)); then
    err "must run as root to read all of ${SOURCE_DIR}"
    return 77
  fi

  # If the share isn't mounted, the mount point is just an empty local
  # directory. Writing there would fill the root disk and keep no off-host copy.
  if ! mountpoint -q -- "${share}"; then
    err "${share} is not a mounted filesystem; refusing to write"
    return 69
  fi

  host="$(hostname -s)"
  if [[ ! ${host} =~ ^[A-Za-z0-9][A-Za-z0-9-]*$ ]]; then
    err "unexpected hostname: ${host}"
    return 70
  fi
  dest="${share}/${host}/etc"
  mkdir -p -- "${dest}"

  # A second run (overlapping cron, manual run) would race on rotation.
  exec {lock_fd}>"${LOCK_FILE}"
  if ! flock -n "${lock_fd}"; then
    err "another run holds ${LOCK_FILE}"
    return 75
  fi

  # Traps before mktemp; cleanup tolerates the empty variable until then.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  # Same directory as the final file, so the rename below is atomic and a
  # partial archive never carries a name that prune or a restore would trust.
  tmp_archive="$(mktemp -- "${dest}/.etc-XXXXXXXX.tar.gz.part")"

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  archive="${dest}/etc-${stamp}.tar.gz"
  if [[ -e ${archive} ]]; then
    err "${archive} already exists"
    return 73
  fi

  tar --create --gzip --one-file-system --file "${tmp_archive}" \
    --directory / -- "${SOURCE_DIR#/}" || status=$?
  case ${status} in
    0) ;;
    # GNU tar exits 1 when a file changed while it was being read (e.g. a
    # rewritten resolv.conf). The archive is still complete, so keep it but say so.
    1) err "warning: some files changed while being archived" ;;
    *)
      err "tar failed with status ${status}"
      return 1
      ;;
  esac

  if ! tar --list --gzip --file "${tmp_archive}" >/dev/null; then
    err "archive failed verification: ${tmp_archive}"
    return 1
  fi

  mv -- "${tmp_archive}" "${archive}"
  tmp_archive=''
  log "wrote ${archive}"

  # Prune only after a verified new archive exists, so a failing backup never
  # eats into the copies already kept.
  prune "${dest}" "${keep}"
}

main "$@"
```

**How it handles the risky parts:**
- **Share not mounted:** it stops with status 69 instead of quietly writing to the local disk under the mount point.
- **Partial or failed archive:** it writes to a hidden `.part` file, checks it with `tar --list`, then renames it. If it fails or gets killed, the temp file is deleted and the old copies stay.
- **Rotation:** only files named exactly `etc-YYYYmmddTHHMMSSZ.tar.gz` are counted or deleted, and only after a good new archive exists. Sorting by name is the same as sorting by date.
- **Two runs at once:** a `flock` on `/run/lock/backup-etc.lock` blocks the second one (status 75).
- **Permissions:** archives are created mode 0600 because `/etc` holds `shadow` and private keys. The script sets its own `PATH` and locale, checks its arguments, and requires root.
- **Layout:** archives go under `SHARE/<short-hostname>/etc/`, so several hosts can share one target.

**Install and schedule:**
```bash
install -o root -g root -m 0755 backup-etc /usr/local/sbin/backup-etc
# /etc/cron.d/backup-etc
# 30 2 * * * root /usr/local/sbin/backup-etc -s /mnt/backup
```

**Things to check yourself:**
- The default share is `/mnt/backup`. Change it or pass `-s`.
- If the share is NFS with `root_squash`, root can't write to it. Use a different export option or a dedicated backup user that has write access.
- `--one-file-system` skips anything mounted inside `/etc`.
- Before relying on it, run `shellcheck backup-etc && bash -n backup-etc`. Then test it as root with `-s` pointing at a scratch mount, including once with the share unmounted and once with `-k 0` to make sure those fail.
