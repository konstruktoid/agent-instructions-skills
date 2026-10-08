I couldn't edit `scripts/backup.sh` because file writing is disabled in this session. Below is a POSIX `sh` rewrite you can drop in. I haven't run it or checked it with `dash -n` or shellcheck.

```sh
#!/bin/sh
# Nightly backup of the application data directory.
# POSIX sh: must run under dash as a Debian maintainer script.

set -eu
umask 077
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH

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

STAMP=$(date +%F)
ARCHIVE=$TMP/data.tar.gz

# -C plus a relative name avoids storing the absolute path in the archive.
tar -czf "$ARCHIVE" -C "$(dirname -- "$DATA_DIR")" -- "$(basename -- "$DATA_DIR")"

scp -q -- "$ARCHIVE" "$REMOTE:$TARGET/data-$STAMP.tar.gz"
```

**What changed from the original**
- **Shebang:** it is now `#!/bin/sh`. Nothing in the script is a bashism. It uses no `[[ ]]`, arrays, `pipefail` or `local`.
- **Strict mode:** `set -eu` is added. The original kept going after a failed `tar` and then removed the temp directory anyway.
- **Temp directory:** `mktemp -d` replaces `/tmp/backup.$$`, which was predictable and open to symlink races. `umask 077` keeps the archive private. `mktemp` isn't in POSIX, but it is always present on Debian.
- **Cleanup:** an `EXIT` trap removes the temp directory on every exit path. The `HUP`, `INT` and `TERM` traps call `exit`, so the `EXIT` trap also runs on those signals under dash.
- **Quoting:** every variable expansion is quoted, and `date` uses `$(...)` instead of backticks.
- **`PATH`:** it is pinned to system directories, since maintainer scripts shouldn't trust the caller's environment.
- **Archive paths:** the archive stores `data/...` instead of the absolute path. If you want the old layout, change the `tar` line back to `tar -czf "$ARCHIVE" -- "$DATA_DIR"`.

**Things to check**
- **Unattended `scp`:** `scp` needs non-interactive key authentication when this runs from a maintainer script or cron. Consider adding `-o BatchMode=yes`.
- **Debian maintainer scripts:** these normally don't make network transfers. If this is meant for `postinst` or `prerm`, you may want it in a cron job or systemd timer instead.

If you re-enable writes, I can apply this to `scripts/backup.sh` and run `dash -n` and `shellcheck -s dash` on it.
