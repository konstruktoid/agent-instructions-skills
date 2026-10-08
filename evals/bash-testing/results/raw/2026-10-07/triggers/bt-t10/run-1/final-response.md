I couldn't add the header comment. The Edit tool is disabled in this session, so `scripts/backup.sh` is unchanged.

This is the header I would insert after line 2 (`# Nightly backup of the application data directory.`):

```bash
#
# Usage: backup.sh
#
# Arguments:
#   None. The source directory (/srv/ledger/data), the remote target
#   directory (/mnt/backup) and the destination host
#   (backup@archive.example.internal) are hardcoded below.
#
# Exit codes:
#   The script sets no explicit exit codes and does not use "set -e", so
#   the exit status is that of the last command (rm -rf), which is
#   normally 0. Failures of mkdir, tar or scp are not propagated.
```

The script takes no arguments and never calls `exit`. A failed `tar` or `scp` still gives exit status 0, which could hide a failed nightly backup. I documented that as it is rather than inventing exit codes. If you want real exit codes (for example `set -euo pipefail`), that is a behavior change. It would need a bats test, so tell me if you want it.

I can apply the comment if you re-enable editing, or you can paste it in yourself.
