I found the cron script at `scripts/backup.sh`. This session only gives me read and search tools, so I couldn't edit the file or run anything. Below is the replacement to drop in, and I haven't run `shellcheck`, `bash -n` or the script against it.

**What's wrong now**

- The only cleanup is the `rm -rf $TMP` on the last line, so it runs only if the script gets that far. If cron's timeout kills the job, a hung `scp` gets a signal, or the job is stopped some other way, the directory stays behind.
- There's no error checking, so a failed `tar` or `scp` is ignored. The run carries on and cron still sees success.
- `/tmp/backup.$$` is a predictable name in a directory anyone can write to. Another user could create it first, or point it somewhere else with a symlink, and `mkdir` fails without anyone noticing. Use `mktemp -d` instead.
- None of the variables are quoted, and the script uses cron's minimal `PATH`.

**Fixed `scripts/backup.sh`**

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting it.
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

# Clean up, then die of the signal so cron sees 128+n rather than success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps before mktemp: cleanup tolerates an empty workdir.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  workdir="$(mktemp -d)"

  stamp="$(date -u +%F)"

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

**How it fixes the cleanup**

- `cleanup` is set up as an `EXIT` trap before the temporary directory is created. It runs whether the script finishes normally or stops early because a step failed.
- `INT`, `TERM` and `HUP` clean up and then end the script with that same signal, so a killed run reports 128+n instead of a false success.
- `cleanup` always returns 0. Otherwise, a missing directory would make a successful run look like a failure.
- `workdir` is set at the top of the script, outside the function, so it still exists when the trap fires.
- Failed steps now write a message to stderr and end the run with a non-zero status, so cron can report them.

Two things I left unchanged: the date is now UTC (the original used local time), so drop the `-u` if the archive names need local dates. The script also still has no lock, so if a run hangs into the next night, two copies can run at once. I can add `flock` if that's possible.

**To verify after applying:**

```bash
shellcheck scripts/backup.sh && bash -n scripts/backup.sh
```

Then do one failure-path run, for example with `DATA_DIR` pointed at a path that doesn't exist. Confirm the exit status is non-zero and that no new `tmp.*` directory is left in `/var/tmp`.
