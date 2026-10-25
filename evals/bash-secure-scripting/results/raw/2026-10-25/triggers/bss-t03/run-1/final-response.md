I can't save changes in this session because I only have read and search tools, no edit or shell tools. So below is the replacement for `scripts/backup.sh`, which you'll need to apply yourself. I haven't run any of it.

## Why the directory is left behind

Here is the script as it is now:

```bash
TMP=/tmp/backup.$$
mkdir $TMP
tar czf $TMP/data.tar.gz $DATA_DIR
scp $TMP/data.tar.gz backup@archive.example.internal:$TARGET/data-`date +%F`.tar.gz
rm -rf $TMP
```

- **The cleanup only runs at the very end** (`scripts/backup.sh:13`). If the script is killed partway through (cron's timeout, a reboot, a SIGTERM while `scp` hangs on the network), `rm -rf` never runs.
- **It also hides failures.** There's no `set -e`, so a failed `tar` doesn't stop the script. It goes on to copy a broken or partial archive and then exits successfully. Cron never hears about the failure.
- **The temp path is easy to guess.** `/tmp/backup.$$` is predictable, so another local user could create it first, possibly as a symlink, before `mkdir` runs. The data being backed up would then be written into a directory they control.

## Fixed script

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: don't trust the inherited environment.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly PROGNAME="${0##*/}"
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

# Clean up, then die of the signal so cron sees 128+n rather than success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps first: cleanup tolerates the empty workdir until mktemp assigns it.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d)"

  stamp="$(date +%F)"
  tar --create --gzip --file "${workdir}/data.tar.gz" -- "${DATA_DIR}"
  # BatchMode: fail instead of hanging on a password or host-key prompt under cron.
  scp -q -o BatchMode=yes "${workdir}/data.tar.gz" \
    "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"
}

main "$@"
```

## What changed

- **The cleanup now runs no matter how the script ends.** It runs from an `EXIT` trap, which is set up *before* `mktemp` creates the directory, so there's no gap where the directory exists but nothing will remove it. It also runs on a normal exit and when `set -e` stops the script after a failed step.
- **Signals are handled.** On INT, TERM or HUP the script cleans up and then exits with that signal's usual failure status, so cron still sees it as a failure. The cleanup function always reports success itself, so it can't make a successful run look like a failure.
- **Fails loudly.** With `set -Eeuo pipefail`, a failed `tar` stops the script before anything is copied, and the script exits non-zero.
- **The temp directory is safe.** `mktemp -d` under `/var/tmp` makes a directory with an unpredictable name, and `umask 077` makes the directory and archive readable only by the user running the script.
- **The environment is set inside the script.** `PATH`, `LC_ALL` and `TMPDIR` are set explicitly instead of coming from cron or a caller.
- **Every variable is quoted**, and `$(…)` replaces the backticks.
- **One small behaviour change:** `-o BatchMode=yes` makes `scp` fail if it would otherwise wait for a password or host-key prompt, instead of hanging until cron kills it. If the backup user's key and the archive host's key are already set up, this changes nothing. Remove it if you depend on something else.

## Checks to run after applying

```bash
shellcheck scripts/backup.sh
bash -n scripts/backup.sh
# Failure path: point DATA_DIR at a missing path in a scratch copy, run it,
# then confirm exit status != 0 and no leftover dir:
ls -d /home/user/other-checkout* 2>/dev/null
```

Also send `kill -TERM` while `scp` is running. The script should exit with status 143 and leave no `tmp.*` directory in `/var/tmp`.
