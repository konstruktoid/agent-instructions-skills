I don't have a file-editing or shell tool in this session, so I couldn't change `scripts/backup.sh` or run it under dash. Below is a POSIX `sh` rewrite to paste in. I assumed `scripts/backup.sh` is the script you mean, since it's the only shell script in the workspace.

```sh
#!/bin/sh
# Nightly backup of the application data directory.
# POSIX sh only: this runs under dash as a Debian maintainer script.
set -eu

DATA_PARENT=/srv/ledger
DATA_NAME=data
REMOTE=backup@archive.example.internal
TARGET=/mnt/backup

PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077

tmpdir=
cleanup() {
    if [ -n "$tmpdir" ]; then
        rm -rf -- "$tmpdir"
    fi
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

tmpdir=$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXXXXXX")
archive=$tmpdir/data.tar.gz
stamp=$(date +%Y-%m-%d)

tar -czf "$archive" -C "$DATA_PARENT" "$DATA_NAME"
scp -q -o BatchMode=yes -- "$archive" "$REMOTE:$TARGET/data-$stamp.tar.gz"
```

**What changed and why:**
- **Shebang:** changed from `#!/bin/bash` to `#!/bin/sh`. The script uses no `[[ ]]`, arrays, `local`, `pipefail`, `$'…'` or `function` keyword, so it stays POSIX.
- **`set -eu`:** a failed `tar` no longer leads to `scp` sending a missing or partial archive, and the script now reports failure instead of exiting 0.
- **`mktemp -d` instead of `/tmp/backup.$$`:** the PID-based name was predictable. Since this runs as root, another local user could plant a symlink there ahead of time. `mktemp` creates the directory safely.
- **Cleanup:** the `EXIT` trap now removes the temp directory on every exit path. The original only removed it if every step succeeded. dash doesn't run the `EXIT` trap when killed by a signal, so the `HUP`, `INT` and `TERM` traps call `exit`, which then runs it.
- **`umask 077`:** stops the ledger data archive being world-readable while it sits in the temp directory.
- **Quoting and `$(…)`:** all expansions are quoted and the backticks are gone. `-C` with a relative path stores `data/` in the archive, so tar doesn't warn about stripping a leading `/`.
- **`date +%Y-%m-%d`:** POSIX format instead of `%F`.
- **`scp -o BatchMode=yes`:** dpkg runs maintainer scripts without a terminal, so `scp` fails instead of hanging on a password or host-key prompt.
- **Fixed `PATH`:** maintainer scripts shouldn't depend on the caller's `PATH`.

**Debian-specific issues to decide on:**
1. **Package dependency:** `tar`, `gzip`, `coreutils` and `dash` are Essential, but `scp` isn't, so the package needs `Depends: openssh-client`.
2. **A failure blocks the install:** with `set -e`, an unreachable backup host makes the maintainer script fail and leaves the package half-configured. If the backup shouldn't block the install or upgrade, change the last line to `scp … || echo "backup: upload failed, continuing" >&2`.
3. **dpkg passes an action argument:** if this goes in `preinst` or `postinst`, wrap the body in `case "$1" in upgrade|configure) … ;; esac` so it doesn't run on every action. Also note that a nightly job would normally be a cron job or systemd timer shipped by the package, not something run from the maintainer script.

To check it, run `dash -n scripts/backup.sh` and `shellcheck -s sh scripts/backup.sh` (and `checkbashisms` from `devscripts` if you have it).
