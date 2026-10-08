I couldn't change `scripts/backup.sh`. The session has no file-editing tool, and `Write` is disabled. I also haven't run `shellcheck`, `bash -n` or the script. The fix below is untested.

**Cause.** `scripts/backup.sh` is the only script in the repo, and it removes `$TMP` with a plain `rm -rf $TMP` on its last line. There's no `set -e` and no `trap`. If `tar` or `scp` fails, or the job is killed, the script either carries on or stops before that line, so `/tmp/backup.$$` stays behind. The script also has other problems:
- `/tmp/backup.$$` is a predictable name.
- None of the expansions are quoted.
- A failed `tar` doesn't stop the run, so `scp` can ship a broken archive.
- `PATH` is whatever cron inherits.

**Proposed replacement for `scripts/backup.sh`:**

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: the environment is the caller's, so set what matters.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup

# Script scope, not local to main: the EXIT trap runs after main has returned.
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

# Clean up, then die of the signal so the caller sees 128+n rather than success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local archive

  # Traps first: a signal between mktemp and the trap would leave the directory.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  workdir="$(mktemp -d)"

  archive="${workdir}/data.tar.gz"
  tar --create --gzip --file "${archive}" -- "${DATA_DIR}"
  scp -- "${archive}" \
    "backup@archive.example.internal:${TARGET}/data-$(date +%F).tar.gz"
}

main "$@"
```

**What this changes:**
- **Cleanup:** the `EXIT` trap is installed before `mktemp -d`, so the directory is removed on a failed step, on `errexit`, and on normal exit. `INT` and `TERM` clean up and then re-raise the signal, so a killed run doesn't report success.
- **Exit status:** `cleanup` always returns 0, so it can't change the script's exit status.
- **Stopping on failure:** `set -Eeuo pipefail` makes a failed `tar` stop the run before `scp`.
- **Temp directory:** `mktemp -d` replaces the predictable `/tmp/backup.$$`, and `umask 077` keeps the archive private.
- **Smaller fixes:** every expansion is quoted, `$(date …)` replaces the backticks, and `PATH` is fixed instead of inherited from cron.

If you give me an edit-capable tool, I'll apply this and run `shellcheck`, `bash -n` and a failure-path test. The test will make `tar` fail and confirm that no `backup.*` directory is left behind.
