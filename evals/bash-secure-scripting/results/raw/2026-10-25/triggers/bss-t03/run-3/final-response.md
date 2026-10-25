I couldn't change the file: this session gives me only read and search tools, so I can't edit files or run commands. Below is the fixed `scripts/backup.sh` for you to apply. I haven't run `shellcheck`, `bash -n` or the script on it.

**Why the directory is left behind:** the only cleanup is the `rm -rf $TMP` on the last line. If the script stops early (cron kills it, `scp` times out, or it runs with `-e` and a step fails), that line never runs. Because there's no strict mode, a failed `tar` also carries on and runs `scp` on a missing or partial archive.

**A related security problem:** `/tmp/backup.$$` is a predictable name in a directory anyone can write to. Another local user can create that path, or a symlink to it, before the job runs. `mkdir` then fails, and the script still writes the data archive into their directory. Using `mktemp -d` fixes this.

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: don't trust the inherited environment.
PATH='/usr/local/bin:/usr/bin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE=backup@archive.example.internal

# Script scope: the EXIT trap runs after main has returned.
workdir=''

err() {
  printf '%s: %s\n' "${PROGNAME}" "$*" >&2
}

cleanup() {
  if [[ -n ${workdir} && -d ${workdir} ]]; then
    rm -rf -- "${workdir}"
  fi
  return 0
}

# Clean up, then die of the signal so cron/supervisors see 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: cleanup tolerates the empty workdir.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d)"

  stamp="$(date +%F)"
  if ! tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"; then
    err "tar of ${DATA_DIR} failed"
    return 1
  fi
  if ! scp -q -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"; then
    err "upload to ${REMOTE} failed"
    return 1
  fi
}

main "$@"
```

**What changed:**
- **Cleanup on every exit:** an `EXIT` trap removes the directory whether the script succeeds, fails partway, or is interrupted. It's set up before the directory is created, so nothing can slip through between the two.
- **Signals:** if cron kills the script (INT, TERM or HUP), it cleans up and then exits as killed. Without that, a killed run would report success.
- **Stops on failure:** strict mode plus explicit checks on `tar` and `scp`. Each failure prints a message to stderr and exits non-zero, so a broken backup no longer looks like it worked.
- **Safe temporary directory:** `mktemp -d` under `/var/tmp`, with `umask 077` so only the job's own user can read the archive.
- **Fixed environment:** `PATH`, locale and `TMPDIR` are set in the script rather than inherited from cron.
- **Quoting:** all paths are quoted, and the backticks are replaced with `$(…)`.

**To check it after applying:**
- Run `shellcheck scripts/backup.sh && bash -n scripts/backup.sh`.
- Test a failure: point `DATA_DIR` at a missing path, run it, and confirm it exits non-zero and that `ls /home/user/other-checkout*` shows nothing left behind.
