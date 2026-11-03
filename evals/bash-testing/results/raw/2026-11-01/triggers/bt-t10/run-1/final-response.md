I didn't change the script. I have no file-editing tool in this session, and the premise of the request doesn't match the script anyway.

**`scripts/backup.sh` takes no arguments and sets no exit codes.** The data directory (`/srv/ledger/data`), the remote target (`/mnt/backup`) and the host (`backup@archive.example.internal`) are hardcoded on lines 4–11. There is no `exit` statement and no `set -e`. The script's exit status comes from its last command, `rm -rf $TMP`, which almost always succeeds. So it **exits 0 even when `tar` or `scp` fails**: a nightly job could report success without making a backup.

A header that lists arguments and exit codes would describe behaviour the script doesn't have. Here is an accurate one you can paste over lines 1–2:

```bash
#!/bin/bash
# Nightly backup of the application data directory.
#
# Usage: backup.sh
#
# Arguments:
#   None. All locations are hardcoded:
#     DATA_DIR  /srv/ledger/data                    directory archived with tar
#     TARGET    /mnt/backup on archive.example.internal (user "backup"), via scp
#   The archive is uploaded as data-YYYY-MM-DD.tar.gz.
#
# Exit status:
#   The script does not set exit codes explicitly. Its status is that of the
#   final "rm -rf" of the temp directory, so it normally exits 0 even if
#   the tar or scp step failed. Do not rely on the exit status to detect a
#   failed backup.
```

If you'd rather have real arguments and exit codes (for example, 0 for success, 1 for bad usage, 2 if tar fails, 3 if scp fails), that's a change to how the script behaves, not just documentation. I can write that version if you want it. It would also be a good time to quote the variables and switch to `mktemp` with a `trap` for cleanup.
