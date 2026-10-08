I couldn't fix `scripts/backup.sh`. Write is disabled in this session and I have no other way to edit files, so nothing has changed on disk. I also haven't run `shellcheck`, `bash -n` or the script.

**What's wrong**
- The script has no `set -e` and no `trap`. The `rm -rf $TMP` on the last line only runs if every earlier step gets that far.
- A `SIGINT` or `SIGTERM`, or any later change that adds strict mode, skips the cleanup and leaves `/tmp/backup.$$` behind.
- `/tmp/backup.$$` is a predictable name. `mkdir $TMP` fails if another user has pre-created that path.
- `$TMP`, `$DATA_DIR` and the `scp` target are all unquoted.
- The script inherits `PATH` and `TMPDIR` from cron, so the caller decides which `tar` and `scp` run.

**Proposed replacement for `scripts/backup.sh`**

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment instead of inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
export TMPDIR=/var/tmp
umask 077

readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE=backup@archive.example.internal

# Script scope: the EXIT trap runs after main has returned.
tmp=''

cleanup() {
  if [[ -n ${tmp} && -d ${tmp} ]]; then
    rm -rf -- "${tmp}"
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
  # Traps first, so a signal between mktemp and the trap cannot leak the directory.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  tmp="$(mktemp -d)"

  tar --create --gzip --file "${tmp}/data.tar.gz" -- "${DATA_DIR}"
  scp -- "${tmp}/data.tar.gz" "${REMOTE}:${TARGET}/data-$(date +%F).tar.gz"
}

main "$@"
```

**What this changes**
- **Cleanup:** the `EXIT` trap runs `cleanup` on every exit path, including a failed `tar` or `scp`. It is installed before `mktemp -d`, so a signal can't leave the directory behind. The `INT` and `TERM` handlers clean up and then re-raise the signal, so cron still sees a failure.
- **Strict mode:** `set -Eeuo pipefail` makes a half-failed run stop instead of carrying on. `tar` and `scp` failures now give a non-zero exit.
- **Temp directory:** `mktemp -d` creates an unpredictable directory. `umask 077` keeps the archive private.
- **Environment:** `PATH` and `TMPDIR` are now set by the script.
- **Quoting:** every expansion is quoted, and `--` guards the arguments to `tar` and `scp`.
- **`scp` target:** its remote path now comes from the quoted `REMOTE` and `TARGET` constants.

I assumed the hardcoded `/var/tmp` and the `PATH` value suit your cron host. Adjust them if they don't.

If you re-enable Write or apply the file yourself, tell me and I'll run `shellcheck`, `bash -n` and a failure-path test (a failing `tar`, checking that no `/var/tmp/tmp.*` is left).
