I couldn't apply this fix. This session only gave me read and search tools, so I can't edit files or run anything. The script is `scripts/backup.sh`. Below is the corrected version to paste in. I haven't run it or checked it with `shellcheck`.

**Why the directory is left behind:** the only cleanup is the `rm -rf $TMP` on the last line, so it runs only if the script gets that far. There's also a second problem. The script has no `set -e`, so when `tar` fails it carries on and copies a partial or missing archive with `scp`. The cron job can then exit 0 even though the backup is bad.

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting the caller's.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE=backup@archive.example.internal

# Script scope, not local to main: the EXIT trap runs after main has returned.
workdir=''

cleanup() {
  if [[ -n ${workdir} && -d ${workdir} ]]; then
    rm -rf -- "${workdir}"
  fi
  return 0
}

# Clean up, then die of the signal so cron and callers see 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: cleanup tolerates the empty workdir until it is assigned.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d)"

  stamp="$(date +%F)"
  tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"
  scp -q -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"
}

main "$@"
```

**What changed:**
- **Cleanup on every exit:** a `trap cleanup EXIT` is set up before the temporary directory is created. It runs on success, when a step fails, and on an early exit. If the script is stopped by `INT`/`TERM`/`HUP`, it cleans up and then exits with that signal, so it doesn't report success.
- **The run stops at the first failure:** with `set -Eeuo pipefail`, a failed `tar` stops the run before `scp`, and the script exits non-zero.
- **Safer temporary directory:** `mktemp -d` under `/var/tmp` with `umask 077` replaces the predictable `/tmp/backup.$$`. Anyone can guess that old name and create a file or link there first, and the archive used to be readable by every user.
- **Fixed environment and quoting:** cron's environment varies, so the script now sets its own `PATH` and locale. All file paths are quoted, and `date` uses `$(...)` instead of backticks.

**Behavior change to expect:** a failed step now ends the run with a non-zero exit, where before it often exited 0. So cron may start reporting failures that were happening silently before.

**To check it** (I couldn't run any of these):
1. Run `shellcheck scripts/backup.sh` and `bash -n scripts/backup.sh`.
2. Run it once with `DATA_DIR` pointing at a path that doesn't exist. It should exit non-zero, never call `scp`, and leave no new `tmp.*` directory under `/var/tmp`.
3. Send it `kill -TERM` during the `tar` step. It should exit 143 and also leave nothing behind.
