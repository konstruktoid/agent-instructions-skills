I traced this to `scripts/backup.sh`. The bug: cleanup is just `rm -rf $TMP` on the last line, so if `tar` or `scp` fails, `set -e` isn't even enabled, and even if it were, the script would exit before reaching that line — the temp dir under `/tmp/backup.$$` is left behind. I don't have file-editing tools available in this session, so here's the corrected script for you to apply:

```bash
#!/usr/bin/env bash
#
# Nightly backup of the application data directory.

set -Eeuo pipefail
shopt -s inherit_errexit

PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
umask 077

readonly DATA_DIR=/srv/ledger/data
readonly TARGET=/mnt/backup
readonly REMOTE_HOST=backup@archive.example.internal

tmpdir=''

cleanup() {
  if [[ -n ${tmpdir} && -d ${tmpdir} ]]; then
    rm -rf -- "${tmpdir}"
  fi
  return 0
}

main() {
  tmpdir="$(mktemp -d)"
  trap cleanup EXIT

  tar czf "${tmpdir}/data.tar.gz" -- "${DATA_DIR}"
  scp -- "${tmpdir}/data.tar.gz" \
    "${REMOTE_HOST}:${TARGET}/data-$(date -u +%F).tar.gz"
}

main "$@"
```

Key changes:
- `trap cleanup EXIT` installed right after `mktemp -d`, so the temp dir is removed whether the script succeeds, fails on `tar`/`scp`, or is killed by a signal `bash` traps.
- `set -Eeuo pipefail` so a failing `tar` or `scp` actually stops the script instead of silently continuing (previously it had no error handling at all).
- `tmpdir` quoted everywhere, and the `rm -rf` target guarded by `-n`/`-d` checks so cleanup can't misfire on an unset or wrong path.
- Dropped the predictable `/tmp/backup.$$` path and unquoted backticks in favor of `mktemp -d` and `$(...)`.

Want me to also check `PATH`/credential handling for the `scp` step (e.g. whether it should use a locked-down SSH key), or is the cleanup fix the main thing you needed?
