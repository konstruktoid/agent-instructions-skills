I don't have a script to work on yet. Your message says what the result must be (POSIX sh that runs under dash as a Debian maintainer script) but not which script it is.

I looked through the workspace and didn't find a maintainer script. There's no `debian/` directory and nothing named `postinst`, `preinst`, `prerm` or `postrm`. The only shell script is `scripts/backup.sh`, a `#!/bin/bash` nightly backup that tars `/srv/ledger/data` and copies it off with `scp`. It isn't a maintainer script, so I didn't assume you meant it.

Could you tell me which of these you want?

1. **A new maintainer script.** Say which one (`postinst`, `prerm`, etc.), which package, and what it should do: create users, set permissions, enable a service, migrate data, and so on.
2. **An existing script you'll paste or point me to.** I'll convert it to POSIX sh and harden it.
3. **`scripts/backup.sh`.** I can rewrite it as POSIX sh, though it would still be a cron job, not a maintainer script.

In every case I'll follow these rules:
- `#!/bin/sh` and `set -e`, as Debian policy requires. No `pipefail`, because dash doesn't support it, so I'll check pipeline failures explicitly where they matter.
- No bashisms: no `[[ ]]`, arrays, `local`-dependent logic, `$'...'`, `source`, `function`, `==` in `test`, process substitution or brace expansion.
- A `case "$1" in configure|abort-upgrade|...)` dispatch with `#DEBHELPER#` in the right place.
- Every expansion quoted, `mktemp` instead of `$$` for temporary files, and cleanup via `trap ... EXIT`.
- I'll check it with `checkbashisms`, `shellcheck -s sh` and `dash -n`.
