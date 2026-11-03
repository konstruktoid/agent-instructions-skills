I don't have a file-writing or shell tool in this session, so I couldn't edit `scripts/backup.sh` or run `dash -n` or `shellcheck -s sh` on it. Here is the POSIX sh version to paste in:

```sh
#!/bin/sh
# Nightly backup of the application data directory.
# POSIX sh: must run under dash (Debian maintainer script context).

set -eu

PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077

DATA_PARENT=/srv/ledger
DATA_NAME=data
REMOTE=backup@archive.example.internal
TARGET=/mnt/backup

tmp=
cleanup() {
	if [ -n "$tmp" ]; then
		rm -rf -- "$tmp"
	fi
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

tmp=$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXXXXXX")

stamp=$(date +%F)
archive=$tmp/data.tar.gz

tar -czf "$archive" -C "$DATA_PARENT" -- "$DATA_NAME"

scp -q -o BatchMode=yes -- "$archive" "$REMOTE:$TARGET/data-$stamp.tar.gz"
```

**What changed and why:**

- **`#!/bin/sh` with no bashisms:** there are no `[[ ]]`, arrays, `local`, `pipefail`, `$'…'`, `source` or `function` keywords. The cleanup is a plain function that uses `[ ]`.
- **`set -eu`:** Debian Policy requires maintainer scripts to use `set -e`. `-u` catches typos in variable names. I left out `pipefail` because older dash versions don't support it, and the script has no pipelines that would need it.
- **`mktemp -d` instead of `/tmp/backup.$$`:** a PID-based name is easy to guess. Another local user could create that path or a symlink first and catch or redirect the archive. `mktemp` isn't strictly POSIX, but it's always present on Debian (coreutils, which is Essential).
- **`umask 077`:** the archive holds ledger data, so it's created readable by its owner only.
- **Cleanup on every exit:** the original never deleted the temp directory if `tar` or `scp` failed. Now the `EXIT` trap removes it. dash doesn't run the `EXIT` trap when it's killed by a signal, so the `HUP`, `INT` and `TERM` traps call `exit` with the usual 128+N status, which then runs the cleanup.
- **`PATH` is set explicitly:** maintainer scripts and cron jobs shouldn't rely on whatever `PATH` they inherit.
- **Variables are quoted and the date is read once:** `$(…)` replaces the backticks, and every expansion is quoted. The date is stored in `stamp` so it can't change partway through.
- **`tar -C … data`:** the archive stores the relative path `data/` instead of `/srv/ledger/data`. This also stops tar warning that it is removing the leading `/`.
- **`scp -o BatchMode=yes`:** if the key or host key is missing, scp fails straight away instead of waiting for a password. That's important when nothing is attached to the terminal.

**Before you ship it:**

1. **Is this really a maintainer script?** A nightly backup usually belongs in a cron job or systemd timer that the package installs, not in `postinst` or `preinst`. If it is meant to run from `preinst` before an upgrade, wrap the body in `case "$1" in upgrade) … ;; esac`. Otherwise it will also run on `install` and `abort-upgrade`. It also makes package installs depend on the network and on SSH keys, which Debian Policy discourages.
2. **The remote path:** scp has the remote side's shell expand the destination path. That's fine here because `TARGET` and the date are fixed and safe. Don't let user-supplied or package-supplied values reach that argument without checking them first.
3. **Check it:** run `dash -n scripts/backup.sh` and `shellcheck -s sh scripts/backup.sh`. Neither has been run on this version.
