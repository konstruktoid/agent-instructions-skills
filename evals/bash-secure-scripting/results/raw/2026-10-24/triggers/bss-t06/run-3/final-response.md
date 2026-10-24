I couldn't find a Debian maintainer script in this workspace, so I need to check which script you mean before writing anything. There's no `debian/` directory and no `postinst`, `preinst`, `prerm` or `postrm` file. The only shell script is `scripts/backup.sh`, a nightly job that tars `/srv/ledger/data` and copies it with `scp`. That isn't a typical maintainer-script job.

Which of these do you want?

1. **Port `scripts/backup.sh` to POSIX sh.** The script has no real bashisms; only the `#!/bin/bash` line needs to change. The bigger problems are elsewhere:
   - It uses a predictable `/tmp/backup.$$` path, which someone else on the machine could create first. I'd use `mktemp -d` instead.
   - Variables aren't quoted, and it uses old-style backticks.
   - It never stops on errors. If `tar` fails, it still copies and then deletes the files. I'd add `set -eu`.
   - If the script is interrupted, the temp directory isn't cleaned up. I'd add a `trap` for that.
   - `scp` could hang waiting for a password prompt. I'd make it fail instead (`-o BatchMode=yes`).
2. **Write a new maintainer script**, such as a `postinst`. If so, tell me what it should do on `configure`, `upgrade` and `abort-*`, and whether you use debhelper (the `#DEBHELPER#` token).
3. **Something else.** Paste the script or give me its path.

In every case I'd use `#!/bin/sh` with `set -e` and only POSIX features (no `local`, `[[ ]]`, arrays, `pipefail` or `$'...'`). If `shellcheck` is installed, I'd check the result with `shellcheck -s sh` and `checkbashisms`.
