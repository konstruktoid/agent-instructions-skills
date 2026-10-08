**Short answer:** put shell tests in `tests/`, the directory the repository already uses for tests. This repository has no shell tests yet, so there is no shell-specific convention to copy. For the filename, follow the existing `test_<subject>.<ext>` pattern, which makes it `tests/test_backup.bats` for `scripts/backup.sh`.

**What I found**
- `tests/test_balance.py` is the only test file. It is a pytest test named `test_<module>.py` that sits in a flat `tests/` directory.
- There are no `.bats` files, no `*_test.sh` or `test_*.sh` files, and no shunit2 usage.
- There is no `Makefile` or `justfile`, so there is no `test` target.
- The only workflow, `.github/workflows/deploy.yml`, has no test step.
- `scripts/backup.sh` is the only shell script.

**Recommendation**
- **Location:** `tests/`, next to the Python tests. Don't create a separate `test/` or `scripts/tests/` directory.
- **Name:** `tests/test_backup.bats`, which mirrors `test_balance.py` by naming the test after the thing it tests.
- **Framework:** bats-core. It is the usual choice for Bash, and no other shell framework is present to conflict with. Adding it is a new dependency, so you should confirm it. The skill's alternative is a plain script that exits non-zero on failure. Both stay out of pytest because the existing suite doesn't invoke any shell scripts.
- **Helpers:** if you use `bats-assert`, vendor it under `tests/test_helper/`. That is the common bats layout, but nothing in this repository sets it yet.

**Before writing a test for `backup.sh`**
The script has no functions and no `main`. It also hard-codes `/srv/ledger/data`, `/mnt/backup` and an `scp` to a remote host. The test should therefore:
- run the script against a scratch directory;
- stub `scp` by putting a fake first on `PATH`;
- cover the failure and cleanup paths.

To make `DATA_DIR` and `TARGET` overridable, you would first have to change the script. That is a small refactor, and I haven't made it.

**Unrelated issues I noticed** (not part of your question)
- `backup.sh` doesn't quote its variables and has no `set -euo pipefail`. It also never checks whether `tar` or `scp` failed, so it can report success after a failed backup. If it exits early, the temp directory is left behind.
- `deploy.yml` sets `permissions: write-all` and interpolates the PR title directly into a `run:` step. That allows script injection through a crafted PR title.
- The skill's sourcing-guard snippet contains `== "Where"`. That is clearly a corrupted placeholder. The usual form is `[[ ${BASH_SOURCE[0]} == "${0}" ]]`. Use that form if you apply the guard.

I can make the `backup.sh` refactor and write the first bats test if you'd like.
