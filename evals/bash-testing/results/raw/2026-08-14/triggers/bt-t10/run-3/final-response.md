I don't have a file-editing tool available in this session (only Glob/Grep/Read/Skill are exposed), so I can't apply the change directly. Here's the header comment to add to `scripts/backup.sh` — insert it after the shebang:

```bash
#!/bin/bash
#
# backup.sh - Nightly backup of the application data directory.
#
# Arguments:
#   None. All paths (DATA_DIR, TARGET) are hardcoded in the script.
#
# Exit codes:
#   0 - Backup completed successfully.
#   Nonzero - Propagated from the failing command (mkdir, tar, or scp);
#             the script has no explicit error handling, so the exit
#             status reflects the last command run.
#
# Nightly backup of the application data directory.
```

If you can grant Bash/Edit access I'll apply this directly instead.
