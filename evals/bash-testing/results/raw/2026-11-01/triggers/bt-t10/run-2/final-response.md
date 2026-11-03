I couldn't add the header: I only have tools to read and search files in this session, not to edit them. And when I read `scripts/backup.sh`, it turned out the header you asked for would describe things the script doesn't do.

**What the script actually does**
- **Arguments:** None. It ignores anything passed to it. The source directory (`/srv/ledger/data`), the remote host (`backup@archive.example.internal`) and the target directory (`/mnt/backup`) are all fixed in the code.
- **Exit codes:** It never sets any. It has no `set -e` and never checks `$?`, so it exits with the status of its last command, `rm -rf $TMP`. That is nearly always 0, which means **the script reports success even when `tar` or `scp` fails.** For a nightly backup, that's the part I'd worry about more than the missing comment.

**A header that matches the current behaviour**, if you want to paste it in place of line 2:

```bash
# backup.sh — Nightly backup of the application data directory.
#
# Archives /srv/ledger/data into a gzipped tarball and copies it with scp to
# backup@archive.example.internal:/mnt/backup/data-YYYY-MM-DD.tar.gz.
#
# Usage:     backup.sh
# Arguments: none (anything passed is ignored; paths and host are fixed in the script)
#
# Exit codes:
#   Undefined: the script exits with the status of its final `rm -rf`, which is
#   almost always 0. tar and scp failures are NOT reported.
```

If you'd rather it document proper exit codes (for example 0 = success, 1 = archive failed, 2 = copy failed), the script needs to be changed to actually return them. I can write that change for you to apply, or make it myself in a session where I can edit files.
