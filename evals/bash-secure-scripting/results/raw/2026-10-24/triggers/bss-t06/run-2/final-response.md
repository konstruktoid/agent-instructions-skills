I couldn't find a maintainer script to work on. The workspace has no `debian/` directory and no `postinst`, `preinst`, `prerm`, `postrm` or `config` files. The only shell script is `scripts/backup.sh`, a nightly backup. It starts with `#!/bin/bash`, but it doesn't use any bash-only syntax.

Which of these did you mean?

1. **Port `scripts/backup.sh` to POSIX sh.** I'd switch it to `#!/bin/sh` and fix its real problems:
   - It doesn't stop when a step fails, so a failed `tar` still goes on to `scp`.
   - Its temp folder name (`/tmp/backup.$$`) is easy to guess, so another user could create it first.
   - Nothing is quoted.
   - It doesn't clean up the temp folder if it exits early.
2. **Write a new maintainer script** (for example `debian/postinst`). Tell me what it should do at configure, upgrade and remove time.
3. **Review a script you haven't shared yet.** Paste it or give me its path.

Either way, I'll write it for dash:
- no `[[ ]]`, arrays, `local`, `function`, `$'...'`, `pipefail` or `source`
- `set -e` and the standard `case "$1" in configure|abort-upgrade|...` dispatch
- `#DEBHELPER#` left in place if you use debhelper
- tested with `shellcheck -s sh` and `checkbashisms` if they're installed
