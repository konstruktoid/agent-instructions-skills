I couldn't add the comment. I only have file read and search tools in this session, and no way to edit or write files, so `scripts/backup.sh` is unchanged. Below is a header you can paste in. I also didn't put it in a Claude Doc, since you asked for a change to the script itself.

Reading the script showed that the header can't truthfully describe arguments or exit codes the way you might expect:

- **Arguments:** it takes none. The source directory, destination and remote host are hardcoded (`scripts/backup.sh:4-5`, `:11`).
- **Exit codes:** it doesn't set any. There's no `set -e` and no `exit`, so the script exits with the status of its last command, `rm -rf $TMP` (`scripts/backup.sh:13`), which nearly always succeeds. If `tar` or `scp` fails, the script still exits 0, so a failed backup looks like a successful one to cron or monitoring.

This header describes what the script actually does. It replaces lines 1–2:

```bash
#!/bin/bash
# Nightly backup of the application data directory.
#
# Usage: backup.sh
#
# Arguments:
#   None. Paths and destination are hardcoded:
#     DATA_DIR  /srv/ledger/data   directory to archive
#     TARGET    /mnt/backup        directory on the archive host
#     Remote    backup@archive.example.internal (via scp)
#   The archive is written as $TARGET/data-YYYY-MM-DD.tar.gz.
#
# Exit status:
#   The script sets no exit codes of its own. It exits with the status of
#   its final command (rm -rf of the temp dir), which is almost always 0.
#   NOTE: a failure in mkdir, tar, or scp does NOT cause a non-zero exit,
#   so a 0 status does not mean the backup succeeded.
```

If you'd rather have a header that promises real exit codes (for example 0 = success, 1 = archive failed, 2 = transfer failed), the script needs a code change first: error checks after `tar`/`scp`, `mktemp -d` in place of `/tmp/backup.$$`, and a `trap` for cleanup. That changes how it behaves, so it should come with a test. I can write it in a session where I can edit files.
