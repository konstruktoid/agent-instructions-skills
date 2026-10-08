I couldn't find a prune script in this repo, so I haven't changed anything.

- **Search:** nothing in the repo contains "prune" (case-insensitive).
- **Shell scripts:** `scripts/backup.sh` is the only one. It has no directory-existence check, but it isn't a prune script. It archives `/srv/ledger/data` and copies the archive with `scp`.
- **Tests:** the only test is `tests/test_balance.py`, a Python test. There's no bats, shunit2 or Makefile, so there's no shell test convention to match yet.

Which of these is it?
1. The prune script is on another branch or in another directory. Give me the path or branch.
2. You meant `scripts/backup.sh`. Its `$DATA_DIR` isn't checked, so `tar` fails silently and the script still exits 0 after `scp`. I can make that fail instead.
3. The prune script doesn't exist yet and you want me to write it.

Once I know the target, I'll make it exit non-zero with a message on stderr when the directory is missing. I'll also add a test for it. With no shell tests in the repo, that probably means a small plain-script or bats test. I'd check with you before introducing a framework.
