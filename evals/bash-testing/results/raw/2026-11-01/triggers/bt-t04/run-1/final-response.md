I didn't change anything, because there's no prune script in this workspace.

- **No prune script:** a case-insensitive search for "prune" across the repo found nothing. The only shell script is `scripts/backup.sh`, and it doesn't prune anything. It tars `/srv/ledger/data`, copies the archive with `scp` to `archive.example.internal`, then deletes its temp directory.
- **No shell tests:** the only tests are pytest tests for the Python ledger code (`tests/test_balance.py`). So there's nothing to match, and pinning the behavior would mean adding a test framework, which is a choice for you to make.
- **No way to edit or run anything:** in this session I can only search and read files. I can't change files or run commands, so I couldn't apply a fix or run a test even if the script were here.

What would help:

1. **If the prune script is in another repo or branch,** point me to it. I'll write the fix (fail with an error on stderr and a non-zero exit when the target directory is missing) and a test that checks that exit code. I'll confirm the test fails before the fix, but that needs a session where I can edit files and run commands.
2. **If you meant `backup.sh`,** it has a similar problem. Nothing checks whether `DATA_DIR` exists, and the script has no `set -e`. When the directory is missing, `tar` fails but the script still runs `scp`, and it returns `rm`'s exit status, which is usually 0. It also has unquoted variables and a temp path that can be guessed (`/tmp/backup.$$`). I can draft the fix and a test for that instead.

Which one do you want?
