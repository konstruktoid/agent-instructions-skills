I don't have a file-editing tool available in this session (only Glob, Grep, Read, and Skill), so I can't apply the change directly. Here's the header comment to add to `scripts/backup.sh` — you can paste it in after the shebang:

```bash
#!/bin/bash
# Nightly backup of the application data directory.
#
# Arguments:
#   None. Source and destination paths are hardcoded (DATA_DIR, TARGET).
#
# Exit codes:
#   0  - Script completed (note: tar/scp failures are not currently checked,
#        so a 0 exit does not guarantee the backup or upload succeeded).
#   1+ - Reserved for future explicit error handling; not currently set.
```

Note: as written, the script doesn't check `tar`/`scp` exit status or use `set -e`, so it will normally exit 0 even if the backup or upload fails — I called that out in the comment rather than claiming exit codes it doesn't actually produce. Let me know if you'd like me to also add real error handling (checking each step and exiting non-zero on failure) — I can do that once I have edit access, or you can apply the above manually.
