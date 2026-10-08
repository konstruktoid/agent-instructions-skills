I couldn't write this to `scripts/backup.sh` because the Write tool is disabled in this session. I also haven't run `dash -n` or `shellcheck -s dash` on it. Below is the POSIX sh rewrite of that file, the only script in the workspace. You can save it over `scripts/backup.sh`, or tell me how you'd like it applied.

```sh
#!/bin/sh
# Nightly backup of the application data directory.
# POSIX sh: must run under dash as a Debian maintainer script.

set -eu

PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077

DATA_DIR=/srv/ledger/data
TARGET=/mnt/backup
REMOTE=backup@archive.example.internal

TMP=$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXX")

cleanup() {
    rm -rf -- "$TMP"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

stamp=$(date +%F)

# Paths relative to / avoid tar's leading-slash stripping.
tar -C / -czf "$TMP/data.tar.gz" -- "${DATA_DIR#/}"

scp -q -o BatchMode=yes "$TMP/data.tar.gz" "$REMOTE:$TARGET/data-$stamp.tar.gz"
```

**What changed**
- **Shell:** the shebang is now `#!/bin/sh`. The script uses no bashisms: no `[[ ]]`, arrays, `pipefail`, `local` or `$'...'`. `${DATA_DIR#/}` and `$(...)` are both POSIX.
- **Strict mode:** `set -eu` replaces the original's no error handling. I left out `pipefail` because dash doesn't support it. There are no pipelines, so nothing is lost.
- **Quoting:** every expansion is quoted. The original's unquoted `$TMP`, `$DATA_DIR` and the backtick `date` would word-split.
- **Temp directory:** `mktemp -d` under `umask 077` replaces the predictable `/tmp/backup.$$`. That path could be pre-created or symlinked by another user.
- **Cleanup:** the `EXIT` trap now removes the temp directory even if `tar` or `scp` fails. Before, a failure left the archive in `/tmp`. The `HUP`, `INT` and `TERM` traps call `exit` so the cleanup runs on signals too.
- **Environment:** `PATH` is fixed, which matters for a script run as root by dpkg.
- **`scp`:** `BatchMode=yes` makes it fail instead of hanging on a password prompt.

**Things to check**
- A maintainer script that exits non-zero aborts the package operation. If this backup is a best-effort step, run it as `backup.sh || true` from the caller, or tell me and I'll build that in.
- `mktemp` isn't POSIX, but it's in Debian's essential `coreutils`, so it's safe here.
