I found the script at `scripts/backup.sh`, but I don't have file-editing tools available in this session (only Glob, Grep, Read, and Skill) — no Edit, Write, or Bash access to apply the change.

Here's the header comment I'd add (documenting the script's current behavior — it takes no arguments and has no explicit exit-code handling, so I described that accurately rather than inventing behavior it doesn't have):

```bash
#!/bin/bash
# Nightly backup of the application data directory.
#
# Arguments:
#   None. DATA_DIR and TARGET are hardcoded above.
#
# Exit codes:
#   The script has no explicit exit-code handling (no `set -e` and no
#   checks after mkdir/tar/scp). It exits with the status of the last
#   command run (`rm -rf $TMP`), which is 0 unless $TMP is missing or
#   unwritable. Failures in tar or scp do not stop the script or affect
#   its exit code.

DATA_DIR=/srv/ledger/data
TARGET=/mnt/backup
...
```

Would you like me to note that lack of error handling as a separate concern, or would you rather apply this edit yourself (or re-run with edit tools enabled)?
