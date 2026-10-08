I couldn't add the header comment. The Edit tool is disabled in this session, and I have no other tool that can write to files. I haven't changed `scripts/backup.sh`.

This is the header I would put after the shebang line. It's based on what the script actually does:

```bash
# Nightly backup of the application data directory.
#
# Usage: backup.sh
#
# Arguments:
#   None. The source (/srv/ledger/data), the remote target (/mnt/backup on
#   archive.example.internal) and the scratch directory (/tmp/backup.$$) are
#   hard-coded below.
#
# Exit codes:
#   The script does not set its own exit codes and does not use "set -e", so
#   it always runs every step. Its exit status is that of the last command,
#   "rm -rf", which is 0 even if the tar or scp step failed. A failed backup
#   therefore still exits 0.
```

The script takes no arguments and has no explicit exit codes. Its exit status comes from the final `rm -rf`, so a failed `tar` or `scp` still exits 0. That could hide failed backups from cron or monitoring. I documented the current behavior rather than inventing codes like 1 for a tar failure and 2 for an scp failure. If you want real exit codes, that is a behavior change, and I'd add a test for it.

If you enable editing or paste the header in yourself, I can apply it. I can also make the exit-code fix if you want it.
