I can't find a prune script in this repository, so I haven't changed anything.

- The only shell script is `scripts/backup.sh`. It has no prune logic and no handling of a missing target directory.
- A search for "prune" (case-insensitive) matched nothing.
- The only test is `tests/test_balance.py`, which is Python. There is no bats or shunit2 suite.

Which of these is it?
1. The script is on another branch or isn't committed. Git status shows `?? ../../../../`, so something untracked sits above this workspace. Give me the path and I'll look there.
2. You mean `backup.sh`, or want a new prune script. If so, tell me what "target directory" means. For example, is it `/mnt/backup` on the remote host, or a local directory?

Once I have the script, I'll make it exit non-zero with an error on stderr when the directory is missing. I'll add a test that checks both the exit status and the message. The repository has no shell test layout, so I'll match whatever you prefer. Otherwise I'll add a small bats test.
