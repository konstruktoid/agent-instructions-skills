I couldn't find a prune script, so I haven't changed anything.

- Searching the repo for filenames containing "prune" and for the text "prune" (case-insensitive) found nothing.
- The only shell script is `scripts/backup.sh`. It doesn't prune and doesn't take a target directory. It backs up `/srv/ledger/data` and copies the archive over `scp`.
- There are no existing shell tests. The only test file is `tests/test_balance.py`, a Python test, and the repo has no Makefile or bats setup.
- The branch is `eval-harness-delegation`. The script may live on another branch, or it may be untracked and outside this workspace. The git status shows only `?? ../../../../`, which is outside the workspace.

Where is the prune script? If you meant `backup.sh`, tell me and I'll work from that. If the script is somewhere else, give me the path or branch.

Once I have the script, my plan is:
1. Make it exit non-zero with a message on stderr when the target directory is missing. Check `[[ -d $target ]]` explicitly rather than relying on `cd` or `find` to fail.
2. Add a test that asserts the exit status and the stderr message. It would use a scratch directory with a path containing a space and check that nothing is deleted.
3. Put the test where the repo's conventions point. With no shell tests here, that is probably a bats file in `tests/`, since no shell framework is already in use. I'd confirm that with you before adding a framework.
4. Check that the test fails against the current script and passes after the fix.

I also noticed two problems in `.github/workflows/deploy.yml` while looking around, which you didn't ask about:
- It interpolates the PR title directly into a `run:` step, which allows script injection.
- It sets `permissions: write-all`.

I haven't touched either.
