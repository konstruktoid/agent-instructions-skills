Before I write anything, I need to know which script you mean. There's no script in your message, and nothing in the workspace looks like a Debian maintainer script: there's no `debian/` directory and no `postinst`, `prerm` or similar file.

The only shell script is `scripts/backup.sh`. It's a `#!/bin/bash` nightly backup that tars `/srv/ledger/data` and `scp`s it to `archive.example.internal`. If that's the one, there's a problem beyond bashisms: a nightly backup shouldn't run as a maintainer script. dpkg runs those as root during install, upgrade and removal, with arguments like `configure` or `remove`. They have to be safe to run more than once, run without anyone at the keyboard, and not depend on the network. An `scp` to a remote host there could hang or fail the package install. A backup like this would normally ship as a cron job or systemd timer, and `postinst` would only set it up.

Which do you want?

1. **Port `backup.sh` to POSIX sh** and fix its other problems: unquoted paths, a guessable `/tmp/backup.$$` directory instead of `mktemp -d`, no cleanup `trap`, and no error checking.
2. **Write a `postinst` (or `prerm`/`postrm`)** for some other task. Tell me what it should do and which dpkg actions it handles.
3. **Something else**, such as an existing maintainer script you'll paste in.

Whichever it is, I'll use `#!/bin/sh` with `set -e` (the Debian policy convention), no `pipefail`, `local`, `[[ ]]`, arrays or `$'...'`, and check it with `shellcheck -s sh` and `checkbashisms`.
