I couldn't find a Debian maintainer script in this workspace, so I need to know which script you mean before writing anything.

There are no `debian/` files, `postinst`, `prerm` or similar here. The only shell script is `scripts/backup.sh`, a nightly backup that starts with `#!/bin/bash` and copies the archive to a remote server with `scp`. That isn't the kind of thing a maintainer script does. Which do you want?

1. **A new maintainer script** (`postinst`, `prerm`, `postrm` or `preinst`). Tell me what it should do, such as creating a system user, fixing ownership on `/srv/ledger/data`, or enabling a service.
2. **`scripts/backup.sh` rewritten in POSIX sh.** It needs fixing either way: it doesn't stop on errors and nothing is quoted. It uses a predictable `/tmp/backup.$$` directory. If `tar` or `scp` fails, it still deletes the temp directory and exits 0.

Whichever it is, I'll write it to these rules:

- **Shell and error handling:** `#!/bin/sh` with `set -e`, as Debian policy requires. I won't use `pipefail`, because the dash in current Debian releases doesn't support it. Where a pipe's exit status matters, I'll check it directly.
- **No bashisms:** no `[[ ]]`, arrays, `local`, `function`, `$'...'`, `<<<`, `{1..n}`, `==` inside `[ ]`, `echo -e`/`-n` (I'll use `printf`), `source` (I'll use `.`) or `$RANDOM`.
- **Standard structure:** a `case "$1" in configure|abort-upgrade|...)` block for the arguments dpkg passes, with an error on unknown actions. It will also include the `#DEBHELPER#` token if you build with debhelper.
- **Safe temp files and cleanup:** temp paths from `mktemp -d`, removed by a `trap` on `EXIT` that also covers `INT` and `TERM`. Every variable will be quoted, and paths will be passed after `--`.
- **Checks:** I'll run `checkbashisms`, `shellcheck -s sh` and `dash -n` on the result if they're installed.
