I couldn't add the header comment. The Edit tool is disabled in this session, and I have no other tool that can modify files, so `scripts/backup.sh` is unchanged.

I read the script and have the comment ready. It would go directly under the existing description line:

```bash
# Nightly backup of the application data directory.
#
# Usage: backup.sh
#
# Arguments:
#   None. The data directory (/srv/ledger/data), the remote target
#   (/mnt/backup on archive.example.internal) and the archive name
#   (data-YYYY-MM-DD.tar.gz) are fixed in the script.
#
# Exit codes:
#   The script does not set any explicitly and does not use set -e, so it
#   exits with the status of its last command, rm -rf of the temporary
#   directory. That is normally 0, even if mkdir, tar or scp failed earlier.
#   Callers cannot rely on the exit code to detect a failed backup.
```

The script takes no arguments and never calls `exit`. A failed `tar` or `scp` therefore still ends in exit 0, and the comment says so. I haven't fixed that, because it would change the script's behavior and you only asked for documentation. Adding `set -euo pipefail` and an explicit `exit` would be the fix if you want it.

You can paste the block in yourself. If you enable editing, I can apply it.
