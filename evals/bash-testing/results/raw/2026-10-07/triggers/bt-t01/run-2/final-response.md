I couldn't fix this, because the bug you describe isn't in this repository.

- **No `mkbackup`:** nothing in the repo is called `mkbackup`. The only backup script is `scripts/backup.sh`, and a search for `mkbackup` finds nothing.
- **No option parsing:** `backup.sh` takes no arguments. It runs `tar czf` on a hardcoded `/srv/ledger/data` and copies the result with `scp`. It has no `--exclude` handling in either form, so there is no `--exclude=PATTERN` case to fix.
- **No shell tests:** the only test is the Python file `tests/test_balance.py`. There is no bats or shunit2 suite to extend.

Inventing option parsing for this script would be a feature, not a fix, and it wouldn't be the script you're running.

Which of these is it?
1. `mkbackup` lives in another repository or branch. If so, point me at it.
2. You want `--exclude PATTERN` and `--exclude=PATTERN` added to `scripts/backup.sh`. I'd then pass them to `tar` and add a bats test for both forms, covering a pattern containing a space and a rejected missing value.
