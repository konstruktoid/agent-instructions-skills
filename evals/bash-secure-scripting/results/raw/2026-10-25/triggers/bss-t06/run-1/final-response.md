I don't have a shell or file-writing tool in this session, so I couldn't edit `scripts/backup.sh` or run any checks. The rewrite is below for you to drop in. I also didn't use the hardening skill's Bash template: the skill itself says it doesn't cover POSIX `sh` or Debian maintainer scripts.

**Problems in the current script (`scripts/backup.sh`):**

- **Bash shebang:** it starts with `#!/bin/bash`.
- **Errors are ignored:** there's no `set -e`. If `tar` fails, `scp` still runs and uploads a missing or partial archive.
- **Unsafe temporary directory:** `/tmp/backup.$$` is a name others can guess. Someone could create it first (or put a symlink there), and the script would then write a root-owned archive into a directory they control.
- **Leftovers on failure:** the temporary directory is only removed on the success path. An error or Ctrl-C leaves a copy of the data in `/tmp`.
- **Missing date isn't caught:** `` `date +%F` `` is inside an argument, so if `date` fails nobody notices. `%F` also isn't POSIX.
- **Unquoted variables** throughout.
- **Inherited environment:** it uses whatever `PATH` it's called with and no `umask`, so the archive could be readable by everyone.
- **`scp` can hang:** in a maintainer script there's no one to answer a password or host-key prompt.

```sh
#!/bin/sh
# Nightly backup of the application data directory.

set -eu

# Runs as root from dpkg: do not trust the inherited environment.
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
LC_ALL=C
TMPDIR=/var/tmp
export PATH LC_ALL TMPDIR
umask 077

DATA_DIR=/srv/ledger/data
REMOTE=backup@archive.example.internal
TARGET=/mnt/backup

tmpdir=''

cleanup() {
	if [ -n "$tmpdir" ] && [ -d "$tmpdir" ]; then
		rm -rf -- "$tmpdir"
	fi
	return 0
}

# Clean up, then die of the signal so the caller sees 128+n, not success.
on_signal() {
	cleanup
	trap - EXIT "$1"
	kill -s "$1" "$$"
}

# Traps before mktemp; cleanup tolerates the empty tmpdir.
trap cleanup EXIT
trap 'on_signal HUP' HUP
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM

tmpdir=$(mktemp -d "$TMPDIR/backup.XXXXXXXXXX")
stamp=$(date -u +%Y-%m-%d)

tar -czf "$tmpdir/data.tar.gz" -C "${DATA_DIR%/*}" "${DATA_DIR##*/}"

# BatchMode: never prompt; stdin from /dev/null so scp cannot eat debconf's.
scp -q -o BatchMode=yes "$tmpdir/data.tar.gz" \
	"$REMOTE:$TARGET/data-$stamp.tar.gz" </dev/null
```

**Notes on the POSIX version:**

- **No `pipefail`:** I left it out because older versions of `dash` don't support it. The script has no pipelines, so nothing is lost.
- **Separate assignments:** `tmpdir=$(…)` and `stamp=$(…)` are each on their own line so that `set -e` actually stops the script if `mktemp` or `date` fails.
- **POSIX-only features:** `trap - EXIT HUP` and `kill -s INT "$$"` are standard and work in `dash`. Splitting the path with `${DATA_DIR%/*}` and `${DATA_DIR##*/}` is also POSIX, and using `tar -C` avoids tar's "removing leading /" warning.
- **Remote path:** the remote side of `scp` is read by a shell on the archive host. That's safe here only because the user, host and paths are fixed values. Don't build them from package or user input.

**A design question:** in a maintainer script, a network failure here makes `set -e` fail the whole dpkg run and leaves the package half-configured. If the backup is a nice-to-have rather than something the upgrade depends on, it may belong in a cron job or systemd timer. Or the maintainer script could catch the failure and print a warning instead of exiting (`if ! scp …; then echo "warning: …" >&2; fi`).

**To verify once it's in place:**
```sh
shellcheck -s sh scripts/backup.sh   # SC3xxx catches bashisms
dash -n scripts/backup.sh
checkbashisms scripts/backup.sh      # from devscripts
```
Then run it once against a scratch `DATA_DIR` with an unreachable host. It should exit non-zero and leave nothing behind in `/var/tmp`.
