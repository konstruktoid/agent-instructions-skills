I couldn't apply this fix. This session only gives me tools to read and search files, so I have no way to edit `scripts/backup.sh` or run shellcheck. Below is the full replacement for you to paste in. I haven't run it or checked it with any tool.

**Why the directory gets left behind** (`scripts/backup.sh:7-13`): the only cleanup is the `rm -rf $TMP` on the last line, so anything that stops the script before that line skips it. That includes a kill signal, cron's timeout, or a failure if strict mode is ever added. Three other problems come from the same lines:
- **Failures look like success:** without strict mode, if `tar` fails the script still runs `scp`. The exit status is whatever the last command returned, so cron can report success for a failed backup.
- **Unsafe temp name:** `/tmp/backup.$$` is a predictable name in a directory everyone can write to. Another user can create it first or plant a symlink there. `mkdir` would then fail, or `tar` would write through the link.
- **Unquoted variables** and the backtick `date` substitution.

**Replacement `scripts/backup.sh`:**

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

readonly PROGNAME="${0##*/}"
readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE='backup@archive.example.internal'

# Script scope, not local: the EXIT trap runs after main has returned.
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

# Clean up, then die of the signal so cron/the caller sees 128+n, not success.
on_signal() {
  local sig="$1"
  cleanup
  trap - EXIT "${sig}"
  kill -s "${sig}" -- "$$"
}

main() {
  local stamp

  # Traps go in before mktemp so there's no moment where the directory exists
  # but nothing will remove it. cleanup does nothing while workdir is empty.
  trap cleanup EXIT
  trap 'on_signal INT' INT
  trap 'on_signal TERM' TERM
  trap 'on_signal HUP' HUP
  trap 'err "failed at line ${LINENO}: ${BASH_COMMAND}"' ERR

  workdir="$(mktemp -d "${TMPDIR}/backup.XXXXXXXXXX")"
  stamp="$(date +%F)"

  tar -czf "${workdir}/data.tar.gz" "${DATA_DIR}"
  scp -- "${workdir}/data.tar.gz" "${REMOTE}:${TARGET}/data-${stamp}.tar.gz"
}

main "$@"
```

**How it works now:**
- **Cleanup on every exit:** an `EXIT` trap removes the directory whether the script finishes, fails partway, or is stopped by `INT`, `TERM` or `HUP`. After a signal it cleans up, then dies of that same signal, so cron sees a failure rather than a 0.
- **Safe temp directory:** `mktemp -d` creates it with a random name and owner-only permissions (`umask 077`). It goes in `/var/tmp`, not a `TMPDIR` the caller chose.
- **Failures are reported:** strict mode stops at the first failed step, writes the failing line to stderr (cron mails that output), and exits non-zero.
- **Environment:** the script sets its own `PATH` and locale instead of using whatever cron passes in.

**To check it** (please run these, since I couldn't):
1. `shellcheck scripts/backup.sh && bash -n scripts/backup.sh`
2. Set `DATA_DIR` to a path that doesn't exist and run it. It should exit non-zero, name `tar` on stderr, and leave nothing matching `/home/user/other-checkout*` behind.
3. Start a run, send it `kill -TERM` partway through, and check the exit status is 143 (128 + 15, the signal number for TERM) and the directory is gone.

**Something to consider separately:** `scp` from cron hangs if it ever falls back to asking for a password. Adding `-o BatchMode=yes` makes it fail straight away instead. I left it out because it changes how the transfer behaves.
