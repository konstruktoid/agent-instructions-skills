I can't make this fix, because the code it describes isn't in this repository.

- **No `mkbackup` script.** The only shell script is `scripts/backup.sh`, and there's no file named `mkbackup` anywhere.
- **No argument parsing.** `backup.sh` takes no arguments. It runs `tar czf` on a hard-coded `DATA_DIR` and copies the result with `scp`.
- **No `--exclude` handling.** A search for "exclude" matches nothing in the repo, so there's no `--exclude PATTERN` branch to compare against the `--exclude=PATTERN` form.

I didn't want to invent an option parser and call that the fix. Either `mkbackup` lives in a different repo or branch, or you want me to add `--exclude` support to `backup.sh`.

The repo has no shell tests. The only test is a pytest file, `tests/test_balance.py`, and the only CI workflow is `deploy.yml`. For the regression test I'd add a bats test, or a plain-script test if you'd rather not add a framework. It would cover both `--exclude=PATTERN` and `--exclude PATTERN`, plus a pattern with a space in it, and I'd confirm it fails without the fix. I'd also have to split `backup.sh` into functions with a `main "$@"` guard so the test can source it.

Can you point me to the right file or branch, or tell me to add the option to `backup.sh`?
