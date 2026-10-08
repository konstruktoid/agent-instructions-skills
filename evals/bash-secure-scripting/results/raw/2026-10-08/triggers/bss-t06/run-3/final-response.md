I couldn't save or test this here. This session only lets me read files: it has no edit or shell tools. So below is the rewrite of `scripts/backup.sh` to paste in. I haven't run it, `shellcheck`, or `checkbashisms` on it.

```sh
#!/bin/sh
# Nightly backup of the application data directory.
set -eu

umask 077
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH

DATA_PARENT=/srv/ledger
DATA_NAME=data
REMOTE=backup@archive.example.internal
TARGET=/mnt/backup

tmpdir=
cleanup() {
    if [ -n "$tmpdir" ]; then
        rm -rf -- "$tmpdir"
    fi
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

tmpdir=$(mktemp -d)
stamp=$(date +%F)

tar -czf "$tmpdir/data.tar.gz" -C "$DATA_PARENT" "$DATA_NAME"
scp -q -o BatchMode=yes "$tmpdir/data.tar.gz" "$REMOTE:$TARGET/data-$stamp.tar.gz"
```

**Changes and why:**

- **`#!/bin/sh` and no bashisms:** the backticks became `$(...)`. The script doesn't use `[[ ]]`, arrays, `local`, `pipefail` or `$'...'`, so dash can run it.
- **`set -eu`:** Debian Policy expects maintainer scripts to use `set -e`. Before, if `tar` failed, the script still copied a broken or missing archive and exited 0.
- **`mktemp -d` instead of `/tmp/backup.$$`:** the PID-based name was easy to guess. Because this runs as root, a local user could plant a symlink at that path ahead of time. `mktemp` is in coreutils, which every Debian system has. It creates the directory with mode 0700.
- **Cleanup on every exit:** the old `rm -rf` only ran if the script reached the end. Now an `EXIT` trap removes the temp directory. dash doesn't run `EXIT` traps when a signal kills the script, so `trap 'exit 1' HUP INT TERM` turns those signals into a normal exit, and the cleanup still runs.
- **`umask 077`:** the archive holds ledger data, so it shouldn't be readable by other users, even for a moment.
- **Fixed `PATH`:** maintainer scripts run as root, often with an environment they inherited from the caller.
- **Quoted variables and `tar -C`:** quoting stops word-splitting and globbing. `-C` avoids the "Removing leading `/`" warning and gives clean paths inside the archive.
- **`scp -o BatchMode=yes`:** a password or host-key prompt would otherwise hang `apt`/`dpkg` while it waits for input.

**Before you ship it, decide on these:**

1. **What should happen if the backup fails?** With `set -e`, a failed backup now aborts the package operation. If this is in `preinst`/`prerm`, that's probably what you want: don't upgrade without a backup. If the backup is optional, write `if ! scp ...; then echo "warning: backup failed" >&2; fi` instead.
2. **Run it only for the right action.** Maintainer scripts receive an action as `$1` (`install`, `upgrade`, `configure`, `remove`, …). You'll probably want the backup inside `case "$1" in upgrade) ... ;; esac`. If you use debhelper, keep the `#DEBHELPER#` token too.
3. **Root needs SSH access to the archive host.** That means root's `known_hosts` must list the host and root needs a key it can use without a prompt. Otherwise `BatchMode` makes `scp` fail at once, which is better than hanging.
4. **Doing the backup from a maintainer script at all.** Copying files over the network during `dpkg` is unusual, and the original comment says "nightly". If it really is a nightly job, a systemd timer or cron job that the package ships would be a better home than a maintainer script.

To check it locally:

```sh
shellcheck -s sh scripts/backup.sh
checkbashisms scripts/backup.sh   # from devscripts
dash -n scripts/backup.sh
```
