Before I write anything, I need to know what "it" is. Your message gives a constraint (POSIX sh under dash, no bashisms) but not the task.

The only shell script in the workspace is `scripts/backup.sh`. It's a 13-line nightly backup that tars `/srv/ledger/data` and copies it with `scp` to `backup@archive.example.internal`. It doesn't look like a maintainer script, so I don't want to guess. Which of these do you mean?

1. **Convert `scripts/backup.sh` to POSIX sh.** I'd change the shebang to `#!/bin/sh` and replace the backticks with `$(...)`. I'd also fix its real problems:
   - The predictable `/tmp/backup.$$` path is a symlink/race risk; I'd use `mktemp -d` instead.
   - None of the variables are quoted.
   - Nothing stops the script if `tar` fails, so it would still `scp` a broken archive. I'd add `set -eu` and check each step.
   - The temp directory isn't cleaned up on failure; I'd add an `EXIT` trap.

   I'd leave out `pipefail` because dash doesn't reliably support it.
2. **Write a new maintainer script** (`postinst`, `prerm`, `postrm` or `preinst`) for a package, for example one that installs this backup as a cron job or systemd timer. If so, tell me:
   - which script and package
   - what it should do for each action it receives (`configure`, `remove`, `purge`, `upgrade`, ...)
   - whether you use debhelper, so I can include the `#DEBHELPER#` token

Either way I'd follow the Debian Policy rules for maintainer scripts:
- Start with `set -e`.
- Handle every argument with a `case` statement.
- Make the script safe to run more than once.
- Don't prompt the user (use debconf for questions).

I'd check it with `checkbashisms`, `shellcheck -s sh` and `dash -n` where those tools are installed.
