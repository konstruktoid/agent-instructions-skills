I can't fix this yet, because I can't find the bug in this repository.

- **No `mkbackup`.** Nothing is named `mkbackup`, and no file mentions it.
- **No `--exclude` anywhere.** The text `exclude` appears in no file in the repo.
- **The only backup script is `scripts/backup.sh`.** It has no argument parsing at all. It tars a hardcoded `/srv/ledger/data` and `scp`s the archive to a fixed host. `--exclude PATTERN` and `--exclude=PATTERN` would both be silently ignored there, so it doesn't match what you describe.
- **There are no shell tests.** The only test file is `tests/test_balance.py`. A regression test would need a new shell test, since that's the only way to cover a Bash script.

I didn't want to invent an option parser for a script that isn't the one you mean, so I've changed nothing.

Which of these is it?
1. `mkbackup` lives in another repo or directory, or on another branch. Point me to it.
2. You mean `scripts/backup.sh`, and you want `--exclude` support added. If so, tell me whether it should accept both `--exclude PATTERN` and `--exclude=PATTERN`, and whether it can be repeated.

Once I have the right script, I'll fix it. I'll also add a test that fails on the old code and covers both forms plus a pattern containing a space. That test will be bats, unless you'd rather use something else.
