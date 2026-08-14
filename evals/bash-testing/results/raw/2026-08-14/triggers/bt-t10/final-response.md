The Edit tool isn't available in this session, so I can't make the file change directly. Could you enable file editing, or would you like me to just paste the exact text to add so you can apply it yourself?

Here's the header comment I'd add after the shebang line:

```bash
#!/bin/bash
# Nightly backup of the application data directory.
#
# Arguments:
#   None. DATA_DIR (source) and TARGET (remote backup path) are hardcoded
#   below rather than passed in.
#
# Exit codes:
#   The script has no explicit exit codes and does not use `set -e`, so a
#   failure in mkdir/tar/scp does not stop execution or force a non-zero
#   exit. The final exit status is whatever `rm -rf $TMP` returns, which is
#   normally 0.
```
