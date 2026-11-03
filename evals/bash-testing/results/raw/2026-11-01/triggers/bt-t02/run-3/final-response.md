Your shell tests should go in **`tests/`**, one bats-core file per script, named after the script: **`tests/backup.bats`** for `scripts/backup.sh`.

## What the repo has now

- **One shell script:** `scripts/backup.sh`.
- **No shell tests or framework.** There are no `*.bats`, `*_test.sh` or `test_*.sh` files, no vendored bats helpers, and no Makefile or justfile with a test target.
- **One test, in Python:** `tests/test_balance.py`, a pytest test for the Python `ledger.balance` module. It doesn't run any shell scripts, so there's no existing suite to extend.
- **CI doesn't run tests.** The only workflow is `.github/workflows/deploy.yml`.

## Why this layout

- **`tests/` is already your test directory.** Putting shell tests there keeps everything in one place. pytest only collects `test_*.py` files, so it ignores `.bats` files and the two suites stay separate.
- **bats-core is the standard Bash test framework.** It also works with `shellcheck` through its `#!/usr/bin/env bats` shebang. Name each file after the script it tests: `scripts/foo.sh` → `tests/foo.bats`.
- **Shared code goes in `tests/test_helper/`.** This is the usual bats location for `bats-support` and `bats-assert` (vendored or as submodules) and for a shared `common.bash` that finds the repo root.
- **If shell tests grow,** move them into `tests/shell/*.bats`, so `bats tests/shell/` runs only them and `pytest tests/` runs only Python.
- **Give them one entry point.** Add a `make test` (or a CI step) that runs both `bats tests/` and `pytest`. Nothing runs tests in CI right now.

## Things I noticed along the way

1. **`backup.sh` can't be tested as written.** Its paths are hardcoded (`/srv/ledger/data`, `/mnt/backup`), it calls a real `scp` host, and it runs everything at the top level. Before writing a useful test, it needs:
   - its logic moved into functions;
   - a `main "$@"` call wrapped in a check, so a test can load the file without running the backup;
   - its paths made overridable;
   - `scp` stubbed through a fake directory placed first in `PATH`.
2. **`backup.sh` has bugs worth pinning with tests once it's restructured:**
   - variables aren't quoted;
   - it doesn't use `set -e` or check for errors, so it runs `scp` and deletes its temp directory even if `tar` fails;
   - its temp directory is a predictable `/tmp/backup.$$` instead of one made with `mktemp -d`;
   - there's no cleanup `trap`, so a failed run leaves the temp directory behind.
3. **`deploy.yml` has a security problem.** It inserts `${{ github.event.pull_request.title }}` directly into a `run:` command, under `permissions: write-all`, on `pull_request`. Anyone who can open a PR can therefore inject shell commands through the PR title. The fix is to pass the title through an `env:` variable and narrow the permissions. This is separate from your question, but worth fixing.

I haven't written any tests. I can add `tests/backup.bats` and the small restructuring of `backup.sh` it needs, if you'd like.
