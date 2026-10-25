I couldn't find a maintainer script to work on. Your message doesn't include one, and the workspace has no `debian/` directory and no `postinst`, `preinst`, `postrm` or `prerm`.

The only shell script in the workspace is `scripts/backup.sh`. It's a `#!/bin/bash` nightly backup that tars `/srv/ledger/data` and copies it off with `scp`. It doesn't look like a maintainer script, so I didn't assume it's the one you meant.

Which do you want?

1. **Paste or point me to the maintainer script.** I'll review or rewrite it as POSIX `sh` for dash.
2. **Turn `scripts/backup.sh` into POSIX sh.** Note that this file also has problems unrelated to bash vs. dash:
   - It uses a predictable `/tmp/backup.$$` directory, which another local user could create first.
   - None of its variables are quoted.
   - It doesn't check for errors, so `scp` still runs after a failed `tar`.
   - It only deletes the temp directory if it reaches the last line.
3. **Write a new maintainer script.** Tell me which one (`postinst`, `prerm`, etc.) and what it should do.

Whichever you pick, the dash version will:
- start with `#!/bin/sh` and `set -e`, as Debian policy expects
- dispatch on `"$1"` with `case` (`configure`, `abort-upgrade`, `remove`, `purge`, …)
- include the `#DEBHELPER#` token
- use none of `[[ ]]`, arrays, `local`, `pipefail`, `$'…'`, `function`, `source` or `echo -e`

Then I'll check it with `shellcheck -s sh` and `dash -n`, and `checkbashisms` if it's installed.
