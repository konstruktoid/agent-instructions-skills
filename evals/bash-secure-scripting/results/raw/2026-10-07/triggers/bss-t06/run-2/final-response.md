I couldn't write `scripts/backup.sh`, because the Write tool is disabled in this session. Below is the POSIX sh rewrite you can drop in. I haven't run it under dash or checked it with shellcheck.

I assumed "this" meant `scripts/backup.sh`, since it's the only shell script in the repo. If you meant a different script, tell me which.

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

TMP=
cleanup() {
    if [ -n "$TMP" ]; then
        rm -rf -- "$TMP"
    fi
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

TMP=$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXX")

stamp=$(date +%F)
archive=$TMP/data.tar.gz

# -C keeps absolute paths out of the archive.
tar -czf "$archive" -C "$(dirname -- "$DATA_DIR")" -- "$(basename -- "$DATA_DIR")"

scp -q -- "$archive" "$REMOTE:$TARGET/data-$stamp.tar.gz"
```

**What changed**
- **Shebang:** it is now `#!/bin/sh`, and the script uses no bashisms. There's no `pipefail`, `[[ ]]`, arrays or `local`. Only `set -eu` is used, and dash supports that.
- **Temp directory:** `mktemp -d` under `umask 077` replaces `/tmp/backup.$$`, which was a predictable name that another user could pre-create or symlink.
- **Cleanup:** a trap on `EXIT` removes the temp directory. `HUP`, `INT` and `TERM` are mapped to `exit`, so cleanup also runs on signals. The original skipped `rm` whenever `tar` or `scp` failed.
- **Quoting:** every expansion is quoted, and `--` guards the paths. `date` now uses `$(...)` instead of backticks.
- **`PATH`:** it is pinned to the system directories, because maintainer scripts run as root.
- **Archive layout:** `tar -C` stores `data/...` instead of `srv/ledger/data/...`, which also drops tar's "removing leading /" warning. This changes what a restore sees. If you want the old layout back, use `tar -czf "$archive" -- "$DATA_DIR"`.

**What to check**
- `scp` needs non-interactive auth, such as a key, because there's no terminal in a maintainer script.
- A failed backup now exits non-zero. If this runs from `postinst` or `prerm`, that aborts the package operation. Decide whether you want that or an `|| true`.

Once Write is available again, I can save it to `scripts/backup.sh` and run `dash -n` and `shellcheck -s sh` on it.
