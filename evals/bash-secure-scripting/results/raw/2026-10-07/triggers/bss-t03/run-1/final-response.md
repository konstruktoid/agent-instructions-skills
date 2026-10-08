I couldn't fix `scripts/backup.sh`. The Write tool is disabled in this session and I have no other way to edit files. Nothing is changed, and I haven't run shellcheck or `bash -n`.

**Cause.** The script has no strict mode and no trap. `rm -rf $TMP` is the last line, so when `tar` or `scp` fails, the script carries on or stops before reaching it. In both cases `/tmp/backup.$$` stays behind. A signal skips the cleanup too.

**Other problems in the same file:**
- Every variable is unquoted.
- `/tmp/backup.$$` is a predictable name, which allows symlink attacks, and the archive is world-readable under the default umask.
- `PATH` comes from cron's caller.

**Proposed replacement for `scripts/backup.sh`:**

```bash
#!/usr/bin/env bash
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
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

# Clean up, then die of the signal so the caller sees 128+n.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  # Traps first: cleanup tolerates the empty workdir until mktemp assigns it.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  workdir="$(mktemp -d)"

  tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"
  scp -- "${workdir}/data.tar.gz" \
    "backup@archive.example.internal:${TARGET}/data-$(date +%F).tar.gz"
}

main "$@"
```

**What changes:**
- **Cleanup on every exit path.** The EXIT trap is installed before `mktemp -d`, so a failing `tar` or `scp`, or an INT or TERM, still removes the directory. The signal handlers re-raise the signal, so cron sees the real status.
- **`mktemp -d` under `/var/tmp`.** It replaces `/tmp/backup.$$`, and `umask 077` makes the archive private.
- **Strict mode and quoting.** `set -Eeuo pipefail` makes a failed step stop the script with a non-zero status. All expansions are quoted, and `--` guards the paths.
- **Fixed `PATH`.** The script sets its own instead of inheriting cron's.

Once edits are allowed, I can apply this and run the checks. That means shellcheck, `bash -n`, and a failure-path test with a stubbed `scp` that confirms no `tmp.*` directory remains. Or you can paste the block in yourself.
