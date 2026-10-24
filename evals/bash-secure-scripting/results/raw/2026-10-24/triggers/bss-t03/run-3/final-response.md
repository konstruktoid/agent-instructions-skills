I couldn't apply this fix. The tools I have in this session can read files but can't edit them or run commands. So `scripts/backup.sh` is unchanged, and the version below hasn't been through `shellcheck`, `bash -n` or a test run.

## What's wrong in `scripts/backup.sh`

- **Cleanup only happens on the last line (`:13`).** It only runs if the script gets that far. If the script is killed partway through, for example by a cron timeout, a SIGTERM or a hung `scp`, the directory stays. `scp` can hang waiting for a password or host-key prompt that cron can't answer.
- **Errors don't stop the script.** With no `set -e`, a failed `tar` doesn't stop anything, so `scp` copies a broken or missing archive and the run still exits 0. Adding strict mode stops that, but it also means an error would now skip line 13. So moving cleanup into a trap is required, not optional.
- **The temp directory has a guessable name (`/tmp/backup.$$`).** If a leftover directory with that name exists, `mkdir` fails and the script carries on writing into it. Anyone on the machine could also create that path in advance, before the script runs.
- **Variables aren't quoted, and cron's `PATH` and `umask` are inherited.** This matters more than usual here because the archive holds the ledger data.

## Fixed script

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

# Runs from cron: set the environment rather than inheriting it.
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
export LC_ALL=C
umask 077

readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE=backup@archive.example.internal

# Script scope: the EXIT trap reads it after everything else has run.
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

# Traps before mktemp: cleanup tolerates the empty workdir until it is set.
trap cleanup EXIT
trap 'on_signal HUP' HUP
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM
workdir="$(mktemp -d /tmp/backup.XXXXXXXXXX)"

stamp="$(date +%F)"
tar -czf "${workdir}/data.tar.gz" -- "${DATA_DIR}"
scp -q -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"
```

How this fixes the leftover directory:

- **The `EXIT` trap** removes the directory on every exit: success, a failure under `set -e`, or an explicit `exit`.
- **The `HUP`, `INT` and `TERM` traps** clean up and then re-raise the signal. This way a killed run doesn't report success.
- **The traps are set before `mktemp`**, so no point in the run can create the directory without a trap to remove it.
- **`mktemp -d`** gives an unpredictable name and a directory only the owner can access (`0700`).

## Still to check

1. Run `shellcheck scripts/backup.sh` and `bash -n scripts/backup.sh`.
2. Test the failure path. Point `DATA_DIR` at a path that doesn't exist and check that the script exits non-zero and leaves nothing matching `/tmp/backup.*`.
3. Send a `kill -TERM` during the `scp` and check the same thing.

One more option: adding `-B` (batch mode) to `scp` makes it fail straight away when it needs a password, rather than hanging until cron kills it. I left it out because it depends on how authentication is set up on that host.

Separately, the instructions I followed for this have a bug in their example script. They set `local sig="nightly"` where it should take the argument (`"$1"`). The script above uses `"$1"`.
